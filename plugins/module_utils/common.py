# Copyright 2017,2020 IBM Corp. All Rights Reserved.
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
import threading
import platform
import sys
import re
from collections.abc import Mapping
from copy import deepcopy

try:
    from zhmcclient import Session, ClientAuthError, HTTPError
    IMP_ZHMCCLIENT_ERR = None
except ImportError:
    IMP_ZHMCCLIENT_ERR = traceback.format_exc()

try:
    from zhmcclient_mock import FakedSession
    IMP_ZHMCCLIENT_MOCK_ERR = None
except ImportError:
    IMP_ZHMCCLIENT_MOCK_ERR = traceback.format_exc()

BLANKED_OUT = '********'  # Replacement for blanked out sensitive values

# Resource name indicating that the resource is unknown
UNKNOWN_NAME = "(unknown)"


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
        - hmc_host (str or list of str): The hostnames or IP addresses of a
          single HMC or of a list of redundant HMCs, suitable for
          zhmcclient.Session: A single HMC must be specified as a string type
          or as a list type with one item. An HMC list must be specified as a
          list type.
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
                f"object if specified, but is of type {type(faked_session)}")
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
                f"therefore must have items {required_items!r}, but "
                f"{missing_required_items!r} are missing.")
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
                f"therefore must not have items {forbidden_items!r}, but "
                f"{present_forbidden_items!r} are present.")
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
                f"Unexpected: Actual value of property {prop_name!r} is not "
                f"a valid  hex number: {hex_actual!r}")
    else:
        int_actual = None
    if hex_new:
        try:
            int_new = int(hex_new, 16)
        except ValueError:
            raise ParameterError(
                f"New value for property {prop_name!r} is not a valid "
                f"hex number: {hex_new!r}")
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
                f"Unexpected: Actual value of property {prop_name!r} is not "
                f"a valid MAC address: {mac_actual!r}")
    else:
        mac_actual = None
    if mac_new:
        try:
            mac_new = _normalized_mac(mac_new)
        except ValueError:
            raise ParameterError(
                f"New value for property {prop_name!r} is not a valid "
                f"MAC address: {mac_new!r}")
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
                f"CPC {partition.manager.cpc.name!r} has issues; partition "
                f"{partition.name!r} has bad status: {status!r}")

        if status in ('stopped', 'reservation-error'):
            logger.debug("Partition %r on CPC %r is now in status %r",
                         partition.name, partition.manager.cpc.name, status)
            break

        if status == 'starting':
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
                f"Partition {partition.name!r} on CPC "
                f"{partition.manager.cpc.name!r} has unknown status: "
                f"{status!r}")
    else:
        raise AssertionError(
            "Abandoning waiting for the completion of the stop of partition "
            f"{partition.name!r} on CPC {partition.manager.cpc.name!r} after "
            f"exhausting state machine loop. Current status: {status!r}.")
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
                f"CPC {partition.manager.cpc.name!r} has issues; partition "
                f"{partition.name!r} has bad status: {status!r}")

        if status in ('active', 'degraded'):
            logger.debug("Partition %r on CPC %r is now in status %r",
                         partition.name, partition.manager.cpc.name, status)
            break

        if status == 'stopping':
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
                    f"Abandoning the start of partition {partition.name!r} on "
                    f"CPC {partition.manager.cpc.name!r} after reaching "
                    f"status {status!r} after an earlier 'Start Partition' "
                    "operation.")

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
                f"Partition {partition.name!r} on CPC "
                f"{partition.manager.cpc.name!r} has unknown "
                f"status: {status!r}")
    else:
        raise AssertionError(
            "Abandoning waiting for the completion of the start of partition "
            f"{partition.name!r} on CPC {partition.manager.cpc.name!r} after "
            f"exhausting state machine loop. Current status: {status!r}.")
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
                f"CPC {partition.manager.cpc.name!r} has issues; partition "
                f"{partition.name!r} has bad status: {status!r}")

        if status == 'stopping':
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
            f"partition {partition.name!r} on CPC "
            f"{partition.manager.cpc.name!r} after exhausting state machine "
            f"loop. Current status: {status!r}.")


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


def ensure_lpar_inactive(
        logger, lpar, check_mode, operation_timeout, status_timeout):
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
        in which case this method does not actually stop the LPAR, but
        just returns what would have been done.

      operation_timeout (int): Timeout in seconds, for the HMC operation
        (deactivate), if needed).

      status_timeout (int): Timeout in seconds, for waiting for the desired
        LPAR status to be reached.

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
        lpar.deactivate(
            operation_timeout=operation_timeout,
            status_timeout=status_timeout,
            force=True)
        status = pull_lpar_status(lpar)
    changed = True

    if not check_mode and status != 'not-activated':
        raise StatusError(
            f"Could not get LPAR {lpar.name!r} from {org_status!r} status into "
            f"an inactive state; current status is: {status!r}")

    return changed


def ensure_lpar_active(
        logger, lpar, check_mode, activation_profile_name, operation_timeout,
        status_timeout, allow_status_exceptions, force):
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

      operation_timeout (int): Timeout in seconds, for the HMC operation
        (activate), if needed).

      status_timeout (int): Timeout in seconds, for waiting for the desired
        LPAR status to be reached.

      allow_status_exceptions (bool): Controls whether LPAR status "exceptions"
        is considered an additional acceptable end status.

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
                    operation_timeout=operation_timeout,
                    status_timeout=status_timeout,
                    allow_status_exceptions=allow_status_exceptions,
                    force=True)
                status = pull_lpar_status(lpar)
            else:
                # In check mode, we assume the LPAR is not auto-started and
                # would have successfully activated.
                status = 'not-operating'
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
                operation_timeout=operation_timeout,
                status_timeout=status_timeout,
                allow_status_exceptions=allow_status_exceptions)
            status = pull_lpar_status(lpar)
        else:
            # In check mode, we assume the LPAR is not auto-started and
            # would have successfully activated.
            status = 'not-operating'
        changed = True

    logger.debug("LPAR %r is now in status %r%s",
                 lpar.name, status, check_mode_txt)

    if status not in ('not-operating', 'operating', 'exceptions'):
        raise StatusError(
            f"Could not get LPAR {lpar.name!r} from {org_status!r} status into "
            f"an active or loaded state; current status is: {status!r}")

    return changed


def ensure_lpar_loaded(
        logger, lpar, check_mode, activation_profile_name, load_address,
        load_parameter, clear_indicator, store_status_indicator,
        operation_timeout, status_timeout, allow_status_exceptions, force):
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

      operation_timeout (int): Timeout in seconds, for the HMC operation
        (activate/load), if needed).

      status_timeout (int): Timeout in seconds, for waiting for the desired
        LPAR status to be reached.

      allow_status_exceptions (bool): Controls whether LPAR status "exceptions"
        is considered an additional acceptable end status.

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
                    operation_timeout=operation_timeout,
                    status_timeout=status_timeout,
                    allow_status_exceptions=allow_status_exceptions,
                    force=True)
                status = pull_lpar_status(lpar)
            else:
                # In check mode, we assume the LPAR would have successfully
                # re-loaded.
                status = 'operating'
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
                operation_timeout=operation_timeout,
                status_timeout=status_timeout,
                allow_status_exceptions=allow_status_exceptions)
            status = pull_lpar_status(lpar)
        else:
            # In check mode, we assume the LPAR is not auto-started and
            # would have successfully activated.
            status = 'not-operating'
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
                operation_timeout=operation_timeout,
                status_timeout=status_timeout,
                allow_status_exceptions=allow_status_exceptions)
            status = pull_lpar_status(lpar)
        else:
            # In check mode, we assume the LPAR would have successfully
            # loaded.
            status = 'operating'
        changed = True

    logger.debug("LPAR %r is now in status %r%s",
                 lpar.name, status, check_mode_txt)

    if status not in ('operating', 'exceptions'):
        raise StatusError(
            f"Could not get LPAR {lpar.name!r} from {org_status!r} status into "
            f"a loaded state; current status is: {status!r}")

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

    if isinstance(value, bytes):
        return value.decode('utf-8')

    if isinstance(value, str):
        return value

    if value is None:
        return None

    raise TypeError(
        f"Value of {type(value)} cannot be converted to unicode: "
        f"{value!r}")


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
                    f"Property {prop_name!r} can be set during "
                    f"{resource.__class__.__name__} creation but cannot be "
                    f"updated afterwards (from {current_prop_value!r} "
                    f"to {input_prop_value!r}).")
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

    logger = logging.getLogger('zhmcclient.jms')
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


def pull_properties(resource, select_prop_names, update_prop_names=None):
    """
    Pull the properties to be returned for the resource.

    select_prop_names(list of string): Property names to limit the result to,
      from the 'select_properties' module input parameter, using underscores
      instead of hyphens. If None, full properties are pulled.

    update_prop_names(list of string): Property names to be updated from
      the 'properties' module input parameter, using underscores instead of
      hyphens.
    """
    if select_prop_names is None:
        resource.pull_full_properties()
    else:
        prop_names = [pn.replace('_', '-') for pn in select_prop_names]
        if update_prop_names is not None:
            prop_names += [pn.replace('_', '-') for pn in update_prop_names]
        if prop_names:
            resource.pull_properties(prop_names)


def parse_hmc_host(hmc_host):
    """
    Check the actual type of the raw-typed 'hmc_host' parameter and
    convert a possible string representation of a list back to a list type
    to make the 'hmc_host' parameter suitable for zhmcclient.Session.

    Returns:
      The parsed hmc_host input parameter.

    Raises:
      ParameterError: Invalid type of 'hmc_host'.
    """
    if isinstance(hmc_host, str):
        m = re.match(r'\[(.*)\]', hmc_host)
        if m:
            hmc_host = [h.strip(' "\'') for h in m.group(1).split(',')]
    elif not isinstance(hmc_host, list):
        raise ParameterError(
            "Module parameter 'hmc_host' must be a string or list type, but "
            f"is of type {type(hmc_host)}")
    return hmc_host


def underscore_properties(prop_dict):
    """
    Return a copy of the input property dict with property names converted from
    hyphens (as used by HMC) to underscores (as used by Ansible).

    This is done recursively on all property values.

    Note that property values that are not mappings are not copied, so the
    returned object is not a full deep copy of the input object.

    This is used to convert properties returned by the HMC to return values of
    Ansible modules that use underscores in their result.

    Parameters:
        prop_dict (Mapping): The input property dict (key: property name,
          value: property value).

          Note that this includes the following types:
            * a plain dict
            * an immutable_views.DictView object as returned by
              zhmcclient.BaseResource.properties

    Returns:
        dict: Converted property dict, recursively.
    """
    under_prop_dict = {}
    for pname_hyphen, pvalue in prop_dict.items():
        pname_under = pname_hyphen.replace('-', '_')
        if isinstance(pvalue, Mapping):
            pvalue = underscore_properties(pvalue)
        under_prop_dict[pname_under] = pvalue
    return under_prop_dict


def underscore_properties_list(res_list):
    """
    Return a list of dicts from the input resource list with property names
    converted from hyphens (as used by HMC) to underscores (as used by Ansible).

    This is done recursively on all property values.

    Note that property values that are not mappings are not copied, so the
    returned object is not a full deep copy of the input object.

    This is used to convert lists of resource objects returned by the HMC to
    return values of Ansible modules that use underscores in their result.

    Parameters:
        res_list (iterable of zhmcclient.BaseResource): The input resource list,
          as returned by zhmcclient list() or findall() methods.

    Returns:
        list of dict: Converted list of property dicts of the input resources,
        recursively.
    """
    under_prop_dicts = []
    for res in res_list:
        under_prop_dict = underscore_properties(res.properties)
        under_prop_dicts.append(under_prop_dict)
    return under_prop_dicts


def hyphen_properties(prop_dict):
    """
    Return a copy of the input property dict with property names converted from
    underscores (as used by Ansible) to hyphens (as used by HMC).

    This is done recursively on all property values.

    Note that property values that are not mappings are not copied, so the
    returned object is not a full deep copy of the input object.

    This is used when property names specified in Ansible that have underscores
    in the name need to be converted to property names for HMC operations,
    where they need to have hyphens in the name.

    Parameters:
        prop_dict (Mapping): The input property dict (key: property name,
          value: property value).

    Returns:
        dict: Converted property dict, recursively.
    """
    hyphen_prop_dict = {}
    for pname_under, pvalue in prop_dict.items():
        pname_hyphen = pname_under.replace('_', '-')
        if isinstance(pvalue, Mapping):
            pvalue = hyphen_properties(pvalue)
        hyphen_prop_dict[pname_hyphen] = pvalue
    return hyphen_prop_dict


class NotificationThread(threading.Thread):
    """
    A thread class derived from :class:`py:threading.Thread` that is designed
    for running threads that receive zhmcclient notifications.

    Capabilities:

    * handles exceptions that are raised in the started thread, by re-raising
      them in the thread that joins the started thread.

    * can be stopped by calling stop(). The thread function must regularly
      check for whether it should stop by calling need_to_stop().

    * can indicate an arbitrary readiness condition to the calling thread.

    The thread function needs to be specified with the 'target' init argument.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._exc_info = None
        self._stop_event = threading.Event()
        self._ready_event = threading.Event()

    def run(self):
        """
        Call inherited run() and save exception info.
        """
        try:
            super().run()
        except Exception:  # noqa: E722 pylint: disable=broad-except
            self._exc_info = sys.exc_info()

    def join(self, timeout=None):
        """
        Call inherited join() and reraise exception if exception info was saved.
        """
        super().join(timeout)
        if self._exc_info:
            raise self._exc_info.value

    def stop(self):
        """
        In the code that started the thread, request the thread to stop.
        """
        self._stop_event.set()

    def need_to_stop(self):
        """
        In the thread function, check whether a stop has been requested.
        """
        return self._stop_event.is_set()

    def ready(self):
        """
        In the thread function, indicate readiness.
        """
        self._ready_event.set()

    def wait_ready(self, timeout=None):
        """
        In the code that started the thread, wait for readiness.

        The timeout is an int or float in seconds.
        """
        return self._ready_event.wait(timeout)


def params_deepcopy(params):
    """
    Return a deep copy of the module input parameters, for dict items where
    a deep copy is possible.

    For items where a deep copy is not possible, it keeps the original value.

    Reason for this function (instead of simply using `copy.deepcopy()`) is
    the fact that in this collection, the module input params may contain
    an optional '_faked_session' item with a value that cannot be copied.

    Parameters:
      params (dict): Module input parameters. Must not be None.

    Returns:
      dict: Deep copy of params, where possible.
    """
    copy_params = {}
    for key, value in params.items():
        try:
            copy_params[key] = deepcopy(value)
        except TypeError:
            copy_params[key] = value
    return copy_params


def blanked_params(params, blanked_properties=None):
    """
    Return a copy of the module input parameters, with the following items
    blanked out:

    * params['properties'][...] according to the blanked_properties list
    * params['hmc_auth']['password']
    * params['hmc_auth']['session_id']

    Parameters:
      params (dict): Module input parameters. Must not be None.
      blanked_properties (Sequence): List of property names that will be
        blanked out in the 'properties' item of the module input parameters.
        Property names that are not in the input properties will be ignored.

    Returns:
      dict: Deep copy of the input parameters, with blanked out values.
    """
    # The params['properties'] dict and the params['hmc_auth'] dict in the
    # return value will be copies of the corresponding input items, and
    # therefore it is sufficient to make a shallow copy of params.
    copied_params = dict(params)
    if 'properties' in copied_params and copied_params['properties'] \
            and blanked_properties:
        copied_params['properties'] = \
            blanked_dict(copied_params['properties'], blanked_properties)
    if 'hmc_auth' in copied_params:
        copied_params['hmc_auth'] = \
            blanked_dict(copied_params['hmc_auth'], ['password', 'session_id'])
    return copied_params


def blanked_dict(properties, blanked_properties):
    """
    Return a shallow copy of the input properties, where the values of the
    specified properties have been blanked out.

    Parameters:
      properties (Mapping): Input properties. Must not be None.
      blanked_properties (Sequence): List of property names that will be
        blanked out. Property names that are not in the input properties
        will be ignored. Must not be None.

    Returns:
      dict: Shallow copy of the input properties, with blanked out values.
    """
    copied_properties = dict(properties)
    for pname in blanked_properties:
        if pname in copied_properties:
            copied_properties[pname] = BLANKED_OUT
    return copied_properties


def removed_dict(properties, removed_properties):
    """
    Return a shallow copy of the input properties, where the specified
    properties have been removed.

    Parameters:
      properties (Mapping): Input properties. Must not be None.
      removed_properties (Sequence): List of property names that will be
        removed. Property names that are not in the input properties
        will be ignored. Must not be None.

    Returns:
      dict: Shallow copy of the input properties, with removed properties.
    """
    copied_properties = dict(properties)
    for pname in removed_properties:
        try:
            del copied_properties[pname]
        except KeyError:
            pass
    return copied_properties


def object_from_uri(uri, manager):
    """
    Return the zhmcclient resource object for the specified URI, using the
    specified manager object for listing them. The resource object will have
    all properties.

    If the resource object is not found (e.g. because it is not accessible),
    None is returned.

    For resource classes that support selective property retrieval, this
    could be optimized by adding the desired properties to the interface of
    this function, so that only the name is retrieved when only the name is
    exported. However, this function is used only for resource classes that do
    not support selective property retrieval, so this optimization is not
    needed.

    Parameters:
      uri(str): URI for which the resource object is to be looked up.
      manager(zhmcclient.BaseManager): Manager object for listing all
        resource objects.

    Returns:
      zhmcclient.BaseResource: Resource object, or None.
    """
    obj = manager.resource_object(uri)
    try:
        obj.pull_full_properties()
    except HTTPError as exc:
        if exc.http_status == 404 and exc.reason == 1:
            obj = None
    except Exception:
        raise
    return obj


def object_name(obj):
    """
    Return the names of the specified object. If the object is None, the name in
    the constant `UNKNOWN_NAME` is used.

    Parameters:
      object(zhmcclient.BaseResource or None): The resource object or None.

    Returns:
      str: The name of the resource object, or the value of `UNKNOWN_NAME`.
    """
    if obj is None:
        return UNKNOWN_NAME
    return obj.name


def object_properties(obj):
    """
    Return the properties of the specified object as a dict. If the object is
    None, None is returned.

    Parameters:
      obj(zhmcclient.BaseResource or None): The resource object with all
        properties, or None.

    Returns:
      dict or None: The properties of the resource object, or None.
    """
    if obj is None:
        return None
    return dict(obj.properties)


class ObjectsByUriCache:
    """
    Object cache that contains a list of zhmcclient resource objects and allows
    lookup of these resource objects by URI.

    The cache is not automatically updated, but it is used only for short
    periods of time, i.e. within the scope of a single zhmc module call.
    """

    def __init__(self, manager, objects=None):
        """
        Parameters:
          manager(zhmcclient.BaseManager): Resource manager for listing the
            resources.
          objects(list of zhmcclient.BaseResource): Initial resources to be put
            into the cache. If None, the resources will be fetched from the HMC
            when the cache is used.
        """
        self._manager = manager
        if objects is None:
            self._objects_by_uri = None
        else:
            self._objects_by_uri = {}
            for obj in objects:
                self._objects_by_uri[obj.uri] = obj

    def fetch(self):
        """
        Fetch the objects from the HMC and put them into the cache.
        Any existing cache content is replaced.
        """
        self._objects_by_uri = {}
        for obj in self._manager.list(full_properties=False):
            self._objects_by_uri[obj.uri] = obj

    def resource_object(self, uri):
        """
        Return the resource object for the specified URI by looking it up in the
        cache. If the URI cannot be found in the cache (e.g. due to missing
        access), None is used.

        If the cache is empty (e.g. initially), the resource objects are
        fetched from the HMC and put into the cache.

        Parameters:
          uri(str): URI of the resource object to be looked up.

        Returns:
          zhmcclient.BaseResource or None
        """
        if self._objects_by_uri is None:
            self.fetch()
        try:
            return self._objects_by_uri[uri]
        except KeyError:
            return None

    def object_name(self, uri):
        """
        Return the name of the resource object of the specified URI. If the
        URI cannot be found in the cache (e.g. due to missing access), the name
        in the constant `UNKNOWN_NAME` is used.

        If the cache is empty (e.g. initially), the resource objects are
        fetched from the HMC and put into the cache.

        Parameters:
          uri(str): URI for which the resource object is to be looked up.

        Returns:
          str: Name of the resource object.
        """
        obj = self.resource_object(uri)
        if obj is None:
            return UNKNOWN_NAME
        return obj.name

    def object_properties(self, uri):
        """
        Return the full set of properties of the resource object of the
        specified URI. If the URI cannot be found in the cache (e.g. due to
        missing access), None is used.

        If the cache is empty (e.g. initially), the resource objects are
        fetched from the HMC and put into the cache.

        This method pulls the full properties for the object if it does not
        yet have full properties.

        Parameters:
          uri(str): URI for which the resource object is to be looked up.

        Returns:
          dict: Properties of the resource object. If the object cannot be
          found, None will be returned.
        """
        obj = self.resource_object(uri)
        if obj is None:
            return None
        if not obj.has_full_properties:
            obj.pull_full_properties()
        return dict(obj.properties)

    def resource_object_list(self, uris):
        """
        Return the resource objects for the specified URIs by looking them up
        in the cache. For URIs that cannot be found in the cache (e.g. due to
        missing access), None is used.

        If the cache is empty (e.g. initially), the resource objects are
        fetched from the HMC and put into the cache.

        The list items in the return value are index-correlated with the
        specified URIs.

        Parameters:
          uris(list of str): URIs for which the resource objects are to be
            looked up.

        Returns:
          list of BaseResource: List of zhmcclient resource objects, in the same
          order as the specified URIs. For URIs that cannot be found, the list
          items are None.
        """
        if self._objects_by_uri is None:
            self.fetch()
        objs = []
        for uri in uris:
            try:
                obj = self._objects_by_uri[uri]
            except KeyError:
                obj = None
            objs.append(obj)
        return objs

    def object_name_list(self, uris):
        """
        Return a list with the names of the resource objects of the specified
        URIs. For URIs that cannot be found in the cache (e.g. due to
        missing access), the name in the constant `UNKNOWN_NAME` is used.

        If the cache is empty (e.g. initially), the resource objects are
        fetched from the HMC and put into the cache.

        The list items in the return value are index-correlated with the
        specified URIs.

        Parameters:
          uris(list of str): URIs for which the resource objects are to be
            looked up.

        Returns:
          list of str: List of the names of the resource objects. For URIs that
          cannot be found, the list item will be the name in the constant
          `UNKNOWN_NAME`.
        """
        objs = self.resource_object_list(uris)
        names = []
        for obj in objs:
            if obj is None:
                name = UNKNOWN_NAME
            else:
                name = obj.name
            names.append(name)
        return names

    def object_properties_list(self, uris):
        """
        Return a list with the full set of properties of the resource objects of
        the specified URIs. For URIs that cannot be found in the cache (e.g. due
        to missing access), None is used.

        If the cache is empty (e.g. initially), the resource objects are
        fetched from the HMC and put into the cache.

        The list items in the return value are index-correlated with the
        specified URIs.

        This method pulls the full properties for each object that does not
        yet have full properties.

        Parameters:
          uris(list of str): URIs for which the resource objects are to be
            looked up.

        Returns:
          list of dict: List of the properties of the resource objects. For
          URIs that cannot be found, the list item will be None.
        """
        objs = self.resource_object_list(uris)
        properties = []
        for obj in objs:
            if obj is None:
                props = None
            else:
                if not obj.full_properties:
                    obj.pull_full_properties()  # updates the object in the cache
                props = dict(obj.properties)
            properties.append(props)
        return properties
