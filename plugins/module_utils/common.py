# Copyright 2017-2020 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Utility functions for use by more than one Ansible module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import logging
import traceback
import platform
import sys

from ansible.module_utils import six

try:
    from zhmcclient import Session, ClientAuthError
    IMP_ZHMCCLIENT_ERR = None
except ImportError:
    IMP_ZHMCCLIENT_ERR = traceback.format_exc()

try:
    from zhmcclient_mock import FakedSession
    IMP_ZHMCCLIENT_MOCK_ERR = None
except ImportError:
    IMP_ZHMCCLIENT_MOCK_ERR = traceback.format_exc()


class Error(Exception):
    """
    Abstract base class that serves as a common exception superclass for the
    zhmc Ansible module.
    """
    pass


class ImageError(Error):
    """
    Indicates an error with ISO image files.
    """
    pass


class ParameterError(Error):
    """
    Indicates an error with the module input parameters.
    """
    pass


class StatusError(Error):
    """
    Indicates an error with the status of the partition or LPAR.
    """
    pass


class VersionError(Error):
    """
    Indicates an error with the required version of HMC or SE/CPC.
    """
    pass


# Partition status values that cause failure in any status related method
PART_BAD_STATUSES = ('communications-not-active', 'status-check')

# Possible (not necessarily desired) partition status values after 'starting'
PART_STARTING_END_STATUSES = (
    'active', 'degraded', 'reservation-error', 'terminated'
) + PART_BAD_STATUSES

# Possible (not necessarily desired) partition status values after 'stopping'
PART_STOPPING_END_STATUSES = (
    'stopped', 'terminated'
) + PART_BAD_STATUSES


def common_fail_on_import_errors(module):
    """
    Check for import errors in this module.
    """
    if IMP_ZHMCCLIENT_ERR is not None:
        module.fail_json(msg=missing_required_lib("zhmcclient"),
                         exception=IMP_ZHMCCLIENT_ERR)
    if IMP_ZHMCCLIENT_MOCK_ERR is not None:
        module.fail_json(msg=missing_required_lib("zhmcclient_mock"),
                         exception=IMP_ZHMCCLIENT_MOCK_ERR)


def missing_required_lib(library, reason=None, url=None):
    """
    Return a message for a missing Python library (= module).
    """
    hostname = platform.node()
    msg = "Failed to import the required Python library " \
          "(%s) on %s's Python %s." % (library, hostname, sys.executable)
    if reason:
        msg += " This is required %s." % reason
    if url:
        msg += " See %s for more info." % url

    msg += (" Please read module documentation and install in the appropriate "
            "location. If the required library is installed, but Ansible is "
            "using the wrong Python interpreter, please consult the "
            "documentation on ansible_python_interpreter")
    return msg


def open_session(params):
    """
    Open a session with the HMC and validate session-related parameters.

    This is called by modules in order to communicate with the HMC.

    There are three ways the session can be established:

    * Faked session: If the '_faked_session' item in `params` is present
      and not `None`, a faked (=mocked) session with that
      zhmcclient_mock.FakedSession object is returned, and there is no
      communication with an HMC established. The faked session will not be
      logged off in close_session(). This is used for testing only.

    * HMC session with module-scope logoff: If the 'session_id' item in
      `params` is absent or `None`, a zhmcclient.Session object is
      returned that is set up with a newly created HMC session. That HMC session
      will be logged off in close_session().

    * HMC session with user-controlled logoff: If the 'session_id' item in
      `params` is present and not `None`, a zhmcclient.Session object is
      returned that is set up for this existing HMC session. That HMC session
      will not be logged off in close_session().

    Parameters:
      params (dict): Module parameters, with these items:
        - hmc_host (str): HMC host name or IP address.
        - hmc_auth (dict): Credentials, either with password or session_id.
          In case of a password, a new HMC session is created.
          In case of a session_id, that existing HMC session is used.
        - _faked_session (zhmcclient_mock.FakedSession): Faked session, if
          testing.

    Returns:
      tuple: Tuple with these items:
      - session (zhmcclient.Session): The session object to use.
      - logoff (bool): Indicator to logoff in close_session().
    """

    faked_session = params.get('_faked_session', None)
    if faked_session is not None:
        # Faked session
        if not isinstance(faked_session, FakedSession):
            raise ParameterError(
                "Module parameter '_faked_session' must be a FakedSession "
                "object if specified, but is of type {0}".
                format(type(faked_session)))
        logoff = False
        return faked_session, logoff

    hmc_host = params['hmc_host']
    hmc_auth = params['hmc_auth']
    session_id = hmc_auth.get('session_id', None)
    if session_id is None:
        # New HMC session with module-scope logoff
        required_items = ('userid', 'password')
        missing_required_items = [
            p for p in required_items if hmc_auth.get(p, None) is None
        ]
        if missing_required_items:
            raise ParameterError(
                "Module parameter 'hmc_auth' has no 'session_id' item and "
                "therefore must have items {0!r}, but {1!r} are missing.".
                format(required_items, missing_required_items))
        userid = hmc_auth['userid']
        password = hmc_auth['password']
        logoff = True
    else:
        # Existing HMC session with user-controlled logoff
        forbidden_items = ('userid', 'password')
        present_forbidden_items = [
            p for p in forbidden_items if hmc_auth.get(p, None) is not None
        ]
        if present_forbidden_items:
            raise ParameterError(
                "Module parameter 'hmc_auth' has the 'session_id' item and "
                "therefore must not have items {0!r}, but {1!r} are present.".
                format(forbidden_items, present_forbidden_items))
        userid = None
        password = None
        logoff = False

    ca_certs = hmc_auth.get('ca_certs', None)
    verify = hmc_auth.get('verify', True)
    verify_cert = ca_certs if verify else False
    session = Session(
        hmc_host, userid, password, verify_cert=verify_cert,
        session_id=session_id)
    return session, logoff


def close_session(session, logoff):
    """
    Close a session with the HMC.

    Parameters:
      session (zhmcclient.Session): The session object to close.
      logoff (bool): Indicator to logoff the session.
    """
    if logoff:
        try:
            session.logoff()
        except ClientAuthError:
            pass


def hmc_auth_parameter():
    "Return the Ansible module definition of the hmc_auth parameter."
    hmc_auth = dict(
        required=True,
        type='dict',
        options=dict(
            userid=dict(required=False, type='str', default=None),
            password=dict(required=False, type='str', default=None,
                          no_log=True),
            session_id=dict(required=False, type='str', default=None,
                            no_log=True),
            ca_certs=dict(required=False, type='str', default=None),
            verify=dict(required=False, type='bool', default=True),
        ),
    )
    return hmc_auth


def eq_hex(hex_actual, hex_new, prop_name):
    """
    Test two hex string values of a property for equality.
    """
    if hex_actual:
        try:
            int_actual = int(hex_actual, 16)
        except ValueError:
            raise ParameterError(
                "Unexpected: Actual value of property {0!r} is not a valid  "
                "hex number: {1!r}".format(prop_name, hex_actual))
    else:
        int_actual = None
    if hex_new:
        try:
            int_new = int(hex_new, 16)
        except ValueError:
            raise ParameterError(
                "New value for property {0!r} is not a valid "
                "hex number: {1!r}".format(prop_name, hex_new))
    else:
        int_new = None
    return int_actual == int_new


def _normalized_mac(mac_str):
    mac_ints = [int(h, 16) for h in mac_str.split(':')]
    mac_str = ':'.join(["%02x" % i for i in mac_ints])
    return mac_str


def eq_mac(mac_actual, mac_new, prop_name):
    """
    Test two MAC address string values of a property for equality.
    """

    if mac_actual:
        try:
            mac_actual = _normalized_mac(mac_actual)
        except ValueError:
            raise ParameterError(
                "Unexpected: Actual value of property {0!r} is not a valid "
                "MAC address: {1!r}".format(prop_name, mac_actual))
    else:
        mac_actual = None
    if mac_new:
        try:
            mac_new = _normalized_mac(mac_new)
        except ValueError:
            raise ParameterError(
                "New value for property {0!r} is not a valid "
                "MAC address: {1!r}".format(prop_name, mac_new))
    else:
        mac_new = None
    return mac_actual == mac_new


def pull_partition_status(partition):
    """
    Retrieve the partition operational status as fast as possible and return
    it.

    Partition status values and their meaning:

    Status             Resources allocated   OS running
    -----------------------------------------------------------------------
    stopped            no                    no
    starting           transitional          transitional
    stopping           transitional          transitional
    reservation-error  no                    no
    active             yes                   yes
    degraded           yes                   yes
    terminated         yes                   no
    paused             yes                   no
    comm-not-active    unknown               unknown
    status-check       unknown               unknown
    """
    parts = partition.manager.cpc.partitions.list(
        filter_args={'name': partition.name})
    if len(parts) != 1:
        raise AssertionError()
    this_part = parts[0]
    actual_status = this_part.get_property('status')
    return actual_status


def stop_partition(logger, partition, check_mode):
    """
    Ensure that the partition is stopped, regardless of what its current
    operational status is. In some cases, multiple "Stop Partition" operations
    are performed.

    When this method returns, the status of the partition is 'stopped' or
    'reservation-error'.

    Bad statuses ('comm-not-active', 'status-check') are handled by raising
    StatusError.

    This method performs the following actions in a loop:

    Status             Action
    -----------------------------------------------------------------------
    comm-not-active    Bad status: Raise StatusError
    status-check       Bad status: Raise StatusError
    stopped            Success: Return
    reservation-error  Success: Return
    starting           Wait for transition completion, check again
    stopping           Wait for transition completion, check again
    terminated         Stop Partition, wait for job completion, check again
    active             Stop Partition, wait for job completion, check again
    degraded           Stop Partition, wait for job completion, check again
    paused             Stop Partition, wait for job completion, check again

    Parameters:
      logger (logging.Logger): The logger to be used.

      partition (zhmcclient.Partition): The partition.

      check_mode (bool): Indicates whether the playbook was run in check mode,
        in which case this method does ot actually stop the partition, but
        just returns what would have been done.

    Returns:
      bool: Indicates whether the partition was changed.

    Raises:
      StatusError: CPC has issues, partition has a bad status.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """
    changed = False
    status = pull_partition_status(partition)
    max_turns = 10
    turns = 0
    while turns < max_turns:
        turns += 1
        if status in PART_BAD_STATUSES:
            raise StatusError(
                "CPC {cn!r} has issues; partition {pn!r} has bad status: {s!r}".
                format(cn=partition.manager.cpc.name, pn=partition.name,
                       s=status))
        elif status in ('stopped', 'reservation-error'):
            logger.debug("Partition %r on CPC %r is now in status %r",
                         partition.name, partition.manager.cpc.name, status)
            break
        elif status == 'starting':
            logger.debug("Waiting for completion of starting of partition %r "
                         "on CPC %r",
                         partition.name, partition.manager.cpc.name)
            # Let it first finish the starting
            partition.wait_for_status(PART_STARTING_END_STATUSES)
            # Then stop it in the next loop turn
            status = pull_partition_status(partition)
            partition.update_properties_local({'status': status})
            changed = True
        elif status == 'stopping':
            logger.debug("Waiting for completion of stopping of partition %r "
                         "on CPC %r",
                         partition.name, partition.manager.cpc.name)
            # Let it finish the stopping
            partition.wait_for_status(PART_STOPPING_END_STATUSES)
            status = pull_partition_status(partition)
            partition.update_properties_local({'status': status})
            changed = True
        elif status in ('terminated', 'active', 'degraded', 'paused'):
            logger.debug("Stop partition %r on CPC %r (current status: %r)",
                         partition.name, partition.manager.cpc.name, status)
            if not check_mode:
                job = partition.stop(wait_for_completion=False)
                job.wait_for_completion()
                status = pull_partition_status(partition)
            else:
                status = 'stopped'
            partition.update_properties_local({'status': status})
            changed = True
        else:
            raise AssertionError(
                "Partition {pn!r} on CPC {cn!r} has unknown status: {s!r}".
                format(cn=partition.manager.cpc.name, pn=partition.name,
                       s=status))
    else:
        raise AssertionError(
            "Abandoning waiting for the completion of the stop of partition "
            "{pn!r} on CPC {cn!r} after exhausting state machine loop. "
            "Current status: {s!r}.".
            format(cn=partition.manager.cpc.name, pn=partition.name,
                   s=status))
    return changed


def start_partition(logger, partition, check_mode):
    """
    Ensure that the partition is started, regardless of what its current
    operational status is.

    When this method returns, the status of the partition is 'active' or
    'degraded'.

    Bad statuses ('comm-not-active', 'status-check') are handled by raising
    StatusError.

    This method performs the following actions in a loop:

    Status             Action
    -----------------------------------------------------------------------
    comm-not-active    Bad status: Raise StatusError
    status-check       Bad status: Raise StatusError
    active             Success: Return
    degraded           Success: Return
    starting           Wait for transition completion, check again
    stopping           Wait for transition completion, check again
    terminated         If start was alreday performed: Raise StatusError
                       Else: Stop Partition, wait for job compl., check again
    paused             If start was alreday performed: Raise StatusError
                       Else: Stop Partition, wait for job compl., check again
    reservation-error  Start Partition, wait for job completion, check again
    stopped            Start Partition, wait for job completion, check again

    In status 'terminated' and 'paused', an earlier 'Start Partition' causes
    StatusError to be raised in order to avoid a loop: stopped -> start ->
    paused -> stop -> stopped.

    Parameters:
      logger (logging.Logger): The logger to be used.

      partition (zhmcclient.Partition): The partition.

      check_mode (bool): Indicates whether the playbook was run in check mode,
        in which case this method does not actually change the partition, but
        just returns what would have been done.

    Returns:
      bool: Indicates whether the partition was changed.

    Raises:
      StatusError: CPC has issues, partition has a bad status.
      StatusError: Abandoning reaching paused/terminated after start.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """
    changed = False
    status = pull_partition_status(partition)
    max_turns = 10
    turns = 0
    tried_start = False
    while turns < max_turns:
        turns += 1
        if status in PART_BAD_STATUSES:
            raise StatusError(
                "CPC {cn!r} has issues; partition {pn!r} has bad status: {s!r}".
                format(cn=partition.manager.cpc.name, pn=partition.name,
                       s=status))
        elif status in ('active', 'degraded'):
            logger.debug("Partition %r on CPC %r is now in status %r",
                         partition.name, partition.manager.cpc.name, status)
            break
        elif status == 'stopping':
            logger.debug("Waiting for completion of stopping of partition %r "
                         "on CPC %r",
                         partition.name, partition.manager.cpc.name)
            # Let it first finish the stopping
            partition.wait_for_status(PART_STOPPING_END_STATUSES)
            # Then start it in the next loop turn
            status = pull_partition_status(partition)
            partition.update_properties_local({'status': status})
            changed = True
        elif status == 'starting':
            logger.debug("Waiting for completion of starting of partition %r "
                         "on CPC %r",
                         partition.name, partition.manager.cpc.name)
            # Let it finish the starting
            partition.wait_for_status(PART_STARTING_END_STATUSES)
            status = pull_partition_status(partition)
            partition.update_properties_local({'status': status})
            changed = True
        elif status in ('terminated', 'paused'):
            if tried_start:
                raise StatusError(
                    "Abandoning the start of partition {pn!r} on CPC {cn!r} "
                    "after reaching status {s!r} after an earlier "
                    "'Start Partition' operation.".
                    format(cn=partition.manager.cpc.name, pn=partition.name,
                           s=status))

            logger.debug("Stop partition %r on CPC %r (current status: %r)",
                         partition.name, partition.manager.cpc.name, status)
            if not check_mode:
                job = partition.stop(wait_for_completion=False)
                job.wait_for_completion()
                status = pull_partition_status(partition)
            else:
                status = 'stopped'
            partition.update_properties_local({'status': status})
            changed = True
        elif status in ('stopped', 'reservation-error'):
            logger.debug("Start partition %r on CPC %r (current status: %r)",
                         partition.name, partition.manager.cpc.name, status)
            if not check_mode:
                job = partition.start(wait_for_completion=False)
                job.wait_for_completion()
                status = pull_partition_status(partition)
            else:
                # In check mode, simulate the behavior for linux-type partitions
                # that have no boot-device set, to go to 'paused' status.
                if partition.prop('type') == 'linux' \
                        and partition.prop('boot-device') == 'none':
                    status = 'paused'
                else:
                    status = 'active'
            partition.update_properties_local({'status': status})
            changed = True
            tried_start = True
        else:
            raise AssertionError(
                "Partition {pn!r} on CPC {cn!r} has unknown status: {s!r}".
                format(cn=partition.manager.cpc.name, pn=partition.name,
                       s=status))
    else:
        raise AssertionError(
            "Abandoning waiting for the completion of the start of partition "
            "{pn!r} on CPC {cn!r} after exhausting state machine loop. "
            "Current status: {s!r}.".
            format(cn=partition.manager.cpc.name, pn=partition.name,
                   s=status))
    return changed


def wait_for_transition_completion(logger, partition):
    """
    If the partition is in a transitional state ('starting', 'stopping'),
    wait for completion of that transition.

    This is required for updating properties.

    When this method returns, the status of the partition is one of:
      'terminated',
      'paused',
      'reservation-error',
      'active',
      'degraded',
      'stopped'.

    Bad statuses ('comm-not-active', 'status-check') are handled by raising
    StatusError.

    This method performs the following actions in a loop:

    Status             Action
    -----------------------------------------------------------------------
    comm-not-active    Bad status: Raise StatusError
    status-check       Bad status: Raise StatusError
    starting           Wait for transition completion, check again
    stopping           Wait for transition completion, check again
    any other          Success: Return

    Parameters:
      logger (logging.Logger): The logger to be used.

      partition (zhmcclient.Partition): The partition.

    Raises:
      StatusError: CPC has issues, partition has a bad status.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """
    status = pull_partition_status(partition)
    max_turns = 2
    turns = 0
    while turns < max_turns:
        turns += 1
        if status in PART_BAD_STATUSES:
            raise StatusError(
                "CPC {cn!r} has issues; partition {pn!r} has bad status: {s!r}".
                format(cn=partition.manager.cpc.name, pn=partition.name,
                       s=status))
        elif status == 'stopping':
            logger.debug("Waiting for completion of stopping of partition %r "
                         "on CPC %r",
                         partition.name, partition.manager.cpc.name)
            partition.wait_for_status(PART_STOPPING_END_STATUSES)
            status = pull_partition_status(partition)
        elif status == 'starting':
            logger.debug("Waiting for completion of starting of partition %r "
                         "on CPC %r",
                         partition.name, partition.manager.cpc.name)
            partition.wait_for_status(PART_STARTING_END_STATUSES)
            status = pull_partition_status(partition)
        else:
            break
    else:
        raise AssertionError(
            "Abandoning waiting for the completion of a status transition of "
            "partition {pn!r} on CPC {cn!r} after exhausting state machine "
            "loop. Current status: {s!r}.".
            format(cn=partition.manager.cpc.name, pn=partition.name,
                   s=status))


def pull_lpar_status(lpar):
    """
    Retrieve the LPAR operational status as fast as possible and return it.

    LPAR status values and their meaning:

    Status             Resources allocated   OS running
    -----------------------------------------------------------------------
    not-activated      no                    no
    not-operating      yes                   no
    operating          yes                   yes
    acceptable         yes                   yes
    exceptions         unknown               unknown
    """
    lpars = lpar.manager.cpc.lpars.list(filter_args={'name': lpar.name})
    if len(lpars) != 1:
        raise AssertionError()
    this_lpar = lpars[0]
    actual_status = this_lpar.get_property('status')
    return actual_status


def ensure_lpar_inactive(logger, lpar, check_mode):
    """
    Ensure that the LPAR is in an inactive status, regardless of what its
    current operational status is.

    If this function returns, the operational status of the LPAR will be
    'not-activated'.

    Parameters:

      logger (logging.Logger): The logger to be used.

      lpar (zhmcclient.Lpar): The LPAR (must exist, and its
        status property is assumed to be current).

      check_mode (bool): Indicates whether the playbook was run in check mode,
        in which case this method does ot actually stop the LPAR, but
        just returns what would have been done.

    Returns:
      bool: Indicates whether the LPAR was changed.

    Raises:
      zhmcclient.Error: Any zhmcclient exception can happen.
      StatusError: Could not get LPAR into an inactive state.
    """
    changed = False
    status = org_status = pull_lpar_status(lpar)

    if status == 'not-activated':
        logger.debug("LPAR %r was already inactive with status %r",
                     lpar.name, status)
        return changed

    logger.debug("Deactivating LPAR %r (current status %r)",
                 lpar.name, status)
    if not check_mode:
        lpar.deactivate(force=True)
        status = pull_lpar_status(lpar)
    changed = True

    if not check_mode and status != 'not-activated':
        raise StatusError(
            "Could not get LPAR {0!r} from {1!r} status into "
            "an inactive state; current status is: {2!r}".
            format(lpar.name, org_status, status))

    return changed


def ensure_lpar_active(
        logger, lpar, check_mode, activation_profile_name, timeout, force):
    """
    Ensure that the LPAR is at least active, regardless of what its
    current operational status is.

    If the LPAR has auto-load set, it will continue to become loaded.
    If the LPAR was already loaded, it remains loaded.

    If this function returns, the operational status of the LPAR will be one of
    'not-operating', 'operating', or 'exceptions'.

    Parameters:

      logger (logging.Logger): The logger to be used.

      lpar (zhmcclient.Lpar): The LPAR (must exist, and its
        status property is assumed to be current).

      check_mode (bool): Indicates whether the playbook was run in check mode,
        in which case this method does not actually change the LPAR, but
        just returns what would have been done.

      activation_profile_name (string): The name of the image or load activation
        profile to be used when the LPAR needs to be activated. If None, the
        image or load activation profile specified in the
        'next-activation-profile-name' property is used when the LPAR needs to
        be activated.

        If the LPAR was already active, the `force` parameter determines what
        happens.

      timeout (int): Timeout in seconds, for activate (if needed).

      force (bool): Controls what happens when the LPAR is already in
        one of the active statuses: If `True`, the LPAR is re-activated.
        Otherwise, nothing is done.

    Returns:
      bool: Indicates whether the LPAR was changed.

    Raises:
      zhmcclient.Error: Any zhmcclient exception can happen.
      StatusError: Could not get LPAR into an active or loaded state.
    """
    changed = False
    check_mode_txt = " (check mode)" if check_mode else ""
    status = org_status = pull_lpar_status(lpar)

    if status in ('not-operating', 'operating', 'exceptions'):
        if force:
            logger.debug("LPAR %r is in status %r and force is specified, "
                         "re-activating it%s",
                         lpar.name, status, check_mode_txt)
            if not check_mode:
                lpar.activate(
                    activation_profile_name=activation_profile_name,
                    operation_timeout=timeout,
                    force=True)
                status = pull_lpar_status(lpar)
            changed = True
        else:
            logger.debug("LPAR %r is in status %r and force is not specified, "
                         "doing nothing", lpar.name, status)
        return changed

    if status == 'not-activated':
        logger.debug("LPAR %r is in status %r, activating it%s",
                     lpar.name, status, check_mode_txt)
        if not check_mode:
            lpar.activate(
                activation_profile_name=activation_profile_name,
                operation_timeout=timeout)
            status = pull_lpar_status(lpar)
        changed = True

    logger.debug("LPAR %r is now in status %r%s",
                 lpar.name, status, check_mode_txt)

    if not check_mode and status not in \
            ('not-operating', 'operating', 'exceptions'):
        raise StatusError(
            "Could not get LPAR {0!r} from {1!r} status into "
            "an active or loaded state; current status is: {2!r}".
            format(lpar.name, org_status, status))

    return changed


def ensure_lpar_loaded(
        logger, lpar, check_mode, activation_profile_name, load_address,
        load_parameter, clear_indicator, store_status_indicator, timeout,
        force):
    """
    Ensure that the LPAR is loaded, regardless of what its current operational
    status is.

    If the current LPAR status is 'not-activated', the LPAR will be activated
    using the "Activate Logical Partition" operation. That will cause an
    automatic load to be performed in some cases. If the LPAR status after
    the activation is 'not-operating', the "Load Logical Partition" operation
    is performed.

    If the current LPAR status is 'not-operating', the "Load Logical Partition"
    operation is performed.

    If the current LPAR status is 'operating' or 'exceptions', no operation
    is performed, except if the the C(force) parameter is True, in which case
    the operating system is shut down and rebooted.

    If this function returns, the operational status of the LPAR will be
    'operating' or 'exceptions'.
    If these status values cannot be reached, an exception is raised.

    Parameters:

      logger (logging.Logger): The logger to be used.

      lpar (zhmcclient.Lpar): The LPAR (must exist).

      check_mode (bool): Indicates whether the playbook was run in check mode,
        in which case this method does not actually change the LPAR, but
        just returns what would have been done.

      activation_profile_name (string):
        The name of the image or load activation profile to be used when the
        LPAR needs to be activated.

        If `None`, the image or load profile specified in the
        `next-activation-profile-name` property of the LPAR is used when the
        LPAR needs to be activated.

        For LPARs with activation modes other than SSC or zAware, the following
        applies:
        - If an image activation profile is specified, the 'load-at-activation'
          property of the image activation profile determines whether an
          automatic load is performed, using the load parameters from the image
          activation profile.
        - If a load activation profile is specified, an automatic load is
          performed using the load parameters from the load activation profile.

        For LPARs with activation modes SSC or zAware, the following applies:
        - A load profile cannot be specified
        - The LPAR is always auto-loaded using internal load parameters
          (ignoring the 'load-at-activation' property and the load-related
          properties of their image activation profile).

      load_address (string): The hexadecimal address of an I/O device that
        provides access to the control program to be loaded.

        This parameter is used only when explicitly loading the LPAR (i.e.
        when the LPAR dos not have auto-load set).

      load_parameter (string): A parameter string that is passed to the
        control program when loading it.

        This parameter is used only when explicitly loading the LPAR (i.e.
        when the LPAR dos not have auto-load set).

      clear_indicator (bool): Controls whether memory is cleared before
        performing the load.

        This parameter is used only when explicitly loading the LPAR (i.e.
        when the LPAR dos not have auto-load set).

      store_status_indicator (bool): Controls whether the current values of
        CPU timer and other internal resources are stored to their assigned
        absolute storage locations, for state=loaded.

      timeout (int): Timeout in seconds, for activate (if needed) and for
        load (if needed).

      force (bool): Controls what happens when the LPAR is already in
        one of the operating statuses: If `True`, the LPAR is re-loaded.
        Otherwise, nothing is done.

    Returns:
      bool: Indicates whether the LPAR was changed.

    Raises:
      zhmcclient.Error: Any zhmcclient exception can happen.
      StatusError: Could not get LPAR into a loaded state.
    """
    changed = False
    check_mode_txt = " (check mode)" if check_mode else ""
    status = org_status = pull_lpar_status(lpar)

    if status in ('operating', 'exceptions'):
        if force:
            logger.debug("LPAR %r is in status %r and force is specified, "
                         "re-loading it%s",
                         lpar.name, status, check_mode_txt)
            if not check_mode:
                lpar.load(
                    load_address=load_address,
                    load_parameter=load_parameter,
                    clear_indicator=clear_indicator,
                    store_status_indicator=store_status_indicator,
                    operation_timeout=timeout,
                    force=True)
                status = pull_lpar_status(lpar)
            changed = True
        else:
            logger.debug("LPAR %r is in status %r and force is not specified, "
                         "doing nothing", lpar.name, status)
        return changed

    if status == 'not-activated':
        logger.debug("LPAR %r is in status %r, activating it%s",
                     lpar.name, status, check_mode_txt)
        if not check_mode:
            lpar.activate(
                activation_profile_name=activation_profile_name,
                operation_timeout=timeout)
            status = pull_lpar_status(lpar)
        changed = True

    if status == 'not-operating':
        # The LPAR was defined not to auto-load, so we load it.
        logger.debug("LPAR %r is in status %r, loading it%s",
                     lpar.name, status, check_mode_txt)
        if not check_mode:
            lpar.load(
                load_address=load_address,
                load_parameter=load_parameter,
                clear_indicator=clear_indicator,
                store_status_indicator=store_status_indicator,
                operation_timeout=timeout)
            status = pull_lpar_status(lpar)
        changed = True

    logger.debug("LPAR %r is now in status %r%s",
                 lpar.name, status, check_mode_txt)

    if not check_mode and status not in ('operating', 'exceptions'):
        raise StatusError(
            "Could not get LPAR {0!r} from {1!r} status into "
            "a loaded state; current status is: {2!r}".
            format(lpar.name, org_status, status))

    return changed


def to_unicode(value):
    """
    Return the input value as a unicode string.

    The input value may be and will result in:
    * None -> None
    * binary string -> decoded using UTF-8 to unicode string
    * unicode string -> unchanged
    * list or tuple with items of any of the above -> list with converted items
    """
    if isinstance(value, (list, tuple)):
        list_uval = []
        for val in value:
            uval = to_unicode(val)
            list_uval.append(uval)
        return list_uval
    elif isinstance(value, six.binary_type):
        return value.decode('utf-8')
    elif isinstance(value, six.text_type):
        return value
    elif value is None:
        return None
    else:
        raise TypeError("Value of {0} cannot be converted to unicode: {1!r}".
                        format(type(value), value))


def process_normal_property(
        prop_name, resource_properties, input_props, resource):
    """
    Process a normal (= non-artificial) property.

    Parameters:

      prop_name (string): Property name (using Ansible module names).

      resource_properties (dict): Dictionary of property definitions for the
        resource type (e.g. ZHMC_PARTITION_PROPERTIES). Each value must be a
        tuple (allowed, create, update, update_while_active, eq_func,
        type_cast, required(o), default(o)). For details, see the modules
        using this function. (o) means optional.

      input_props (dict): New properties.

      resource: zhmcclient resource object (e.g. zhmcclient.Partition) with
        all properties pulled.

    Returns:

      tuple of (create_props, update_props, stop), where:
        * create_props: dict of properties for resource creation.
        * update_props: dict of properties for resource update.
        * deactivate (bool): Indicates whether the resource needs to be
          deactivated because there are properties to be updated that
          require that.

    Raises:
      ParameterError: An issue with the module parameters.
    """

    create_props = {}
    update_props = {}
    deactivate = False

    p = resource_properties[prop_name]
    allowed, create, update, update_while_active, eq_func, type_cast = p[0:6]
    # Note: If and when required/default are be used here:
    # try:
    #     required = p[6]
    # except IndexError:
    #     required = False
    # try:
    #     default = p[7]
    # except IndexError:
    #     default = None

    # Double check that the property is not a read-only property
    if not allowed:
        raise AssertionError()
    if not (create or update):
        raise AssertionError()

    hmc_prop_name = prop_name.replace('_', '-')
    input_prop_value = input_props[prop_name]

    if type_cast:
        input_prop_value = type_cast(input_prop_value)

    if resource:
        # Resource does exist.

        current_prop_value = resource.properties.get(hmc_prop_name)

        if eq_func:
            equal = eq_func(current_prop_value, input_prop_value,
                            prop_name)
        else:
            equal = (current_prop_value == input_prop_value)

        if not equal:
            if update:
                update_props[hmc_prop_name] = input_prop_value
                if not update_while_active:
                    deactivate = True
            else:
                raise ParameterError(
                    "Property {0!r} can be set during {1} "
                    "creation but cannot be updated afterwards "
                    "(from {2!r} to {3!r}).".
                    format(prop_name, resource.__class__.__name__,
                           current_prop_value, input_prop_value))
    else:
        # Resource does not exist.
        # Prefer setting the property during resource creation.
        if create:
            create_props[hmc_prop_name] = input_prop_value
        else:
            update_props[hmc_prop_name] = input_prop_value
            if not update_while_active:
                deactivate = True

    return create_props, update_props, deactivate


def log_init(logger_name, log_file=None):
    """
    Set up logging for the loggers of the current Ansible module, and for the
    loggers of the underlying zhmcclient package.

    The log level of these loggers is set to debug.

    If a log file is specified, a log file handler for that log file (with a
    log formatter) is created and attached to these loggers.

    Parameters:

        logger_name (string): Name of the logger to be used for the current
          Ansible module.

        log_file (string): Path name of a log file to log to, or `None`.
          If `None`, logging will be propagated to the Python root logger.
    """

    # The datefmt parameter of logging.Formatter() supports the datetime
    # formatting placeholders of time.strftime(). Unfortunately, the %f
    # placeholder for microseconds is not supported by time.strftime().
    # If datefmt=None, the milliseconds are added manually by the
    # logging.Formatter() class. So this is a choice between precision and
    # indicating the timezone offset.
    # The time is in the local timezone.
    #
    DATEFMT = '%Y-%m-%dT%H:%M:%S%z'  # 2019-02-20T10:54:26+0100
    # DATEFMT = None  # 2019-02-20 10:54:26,123 (= local time)

    if log_file:
        handler = logging.FileHandler(log_file)
        fmt = logging.Formatter(
            fmt='%(asctime)s %(levelname)s %(name)s %(process)d %(message)s',
            datefmt=DATEFMT)
        handler.setFormatter(fmt)
    else:
        handler = None

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    if handler:
        ensure_one_handler(logger, handler)

    logger = logging.getLogger('zhmcclient.hmc')
    logger.setLevel(logging.DEBUG)
    if handler:
        ensure_one_handler(logger, handler)


def ensure_one_handler(logger, handler):
    """
    Ensure that the logger has the specified handler exactly once. The handler
    must be a FileHandler, and the handler is recognized by the file name it
    logs to (i.e. the new and existing handler may be different Python objects).
    """
    for hdlr in logger.handlers:
        if isinstance(hdlr, logging.FileHandler) and \
                hdlr.stream.name == handler.stream.name:
            break
    else:
        logger.addHandler(handler)
