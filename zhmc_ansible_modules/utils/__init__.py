# Copyright 2017 IBM Corp. All Rights Reserved.
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

import logging

from ansible.module_utils import six

from zhmcclient import Session
from zhmcclient_mock import FakedSession


class Error(Exception):
    """
    Abstract base class that serves as a common exception superclass for the
    zhmc Ansible module.
    """
    pass


class ParameterError(Error):
    """
    Indicates an error with the module input parameters.
    """
    pass


class StatusError(Error):
    """
    Indicates an error with the status of the partition.
    """
    pass


# Partition status values that may happen after Partition.start()
START_END_STATUSES = ('active', 'degraded', 'reservation-error')

# Partition status values that may happen after Partition.stop()
STOP_END_STATUSES = ('stopped', 'terminated', 'paused')

# Partition status values that indicate CPC issues
BAD_STATUSES = ('communications-not-active', 'status-check')


def eq_hex(hex_actual, hex_new, prop_name):
    """
    Test two hex string values of a property for equality.
    """
    if hex_actual:
        try:
            int_actual = int(hex_actual, 16)
        except ValueError:
            raise ParameterError(
                "Unexpected: Actual value of property {!r} is not a valid hex "
                "number: {!r}".
                format(prop_name, hex_actual))
    else:
        int_actual = None
    if hex_new:
        try:
            int_new = int(hex_new, 16)
        except ValueError:
            raise ParameterError(
                "New value for property {!r} is not a valid hex number: {!r}".
                format(prop_name, hex_new))
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
                "Unexpected: Actual value of property {!r} is not a valid MAC "
                "address: {!r}".
                format(prop_name, mac_actual))
    else:
        mac_actual = None
    if mac_new:
        try:
            mac_new = _normalized_mac(mac_new)
        except ValueError:
            raise ParameterError(
                "New value for property {!r} is not a valid MAC address: {!r}".
                format(prop_name, mac_new))
    else:
        mac_new = None
    return mac_actual == mac_new


def get_hmc_auth(hmc_auth):
    """
    Extract HMC userid and password from the 'hmc_auth' module input
    parameter.

    Parameters:
      hmc_auth (dict): value of the 'hmc_auth' module input parameter,
        which is a dictionary with items 'userid' and 'password'.

    Returns:
      tuple(userid, password): A tuple with the respective items
        of the input dictionary.

    Raises:
      ParameterError: An item in the input dictionary was missing.
    """
    try:
        userid = hmc_auth['userid']
    except KeyError:
        raise ParameterError("Required item 'userid' is missing in "
                             "dictionary module parameter 'hmc_auth'.")
    try:
        password = hmc_auth['password']
    except KeyError:
        raise ParameterError("Required item 'password' is missing in "
                             "dictionary module parameter 'hmc_auth'.")
    return userid, password


def pull_partition_status(partition):
    """
    Retrieve the partition operational status as fast as possible and return
    it.
    """
    parts = partition.manager.cpc.partitions.list(
        filter_args={'name': partition.name})
    assert len(parts) == 1
    this_part = parts[0]
    actual_status = this_part.get_property('status')
    return actual_status


def stop_partition(partition, check_mode):
    """
    Ensure that the partition is stopped, by influencing the operational
    status of the partition, regardless of what its current operational status
    is.

    If this function returns, the operational status of the partition will be
    'stopped'.

    Parameters:
      partition (zhmcclient.Partition): The partition (must exist, and its
        status property is assumed to be current).
      check_mode (bool): Indicates whether the playbook was run in check mode,
        in which case this method does ot actually stop the partition, but
        just returns what would have been done.

    Returns:
      bool: Indicates whether the partition was changed.

    Raises:
      StatusError: Partition is in one of BAD_STATUSES or did not reach the
        'stopped' status despite attempting it.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """
    changed = False
    partition.pull_full_properties()
    status = partition.get_property('status')
    if status in BAD_STATUSES:
        raise StatusError(
            "Target CPC {!r} has issues; status of partition {!r} is: {!r}".
            format(partition.manager.cpc.name, partition.name, status))
    elif status == 'stopped':
        pass
    elif status == 'starting':
        if not check_mode:
            # Let it first finish the starting
            partition.wait_for_status(START_END_STATUSES)
            start_end_status = pull_partition_status(partition)
            # Then stop it
            partition.stop()
            status = pull_partition_status(partition)
            if status != 'stopped':
                raise StatusError(
                    "Could not get partition {!r} from {!r} status into "
                    "'stopped' status after waiting for its starting to "
                    "complete; current status is: {!r}".
                    format(partition.name, start_end_status, status))
        changed = True
    elif status == 'stopping':
        if not check_mode:
            # Let it finish the stopping
            partition.wait_for_status(STOP_END_STATUSES)
            stop_end_status = pull_partition_status(partition)
            if stop_end_status != 'stopped':
                # Make another attempt to stop it
                partition.stop()
                status = pull_partition_status(partition)
                if status != 'stopped':
                    raise StatusError(
                        "Could not get partition {!r} from {!r} status into "
                        "'stopped' status after waiting for its stopping to "
                        "complete; current status is: {!r}".
                        format(partition.name, stop_end_status, status))
        changed = True
    else:
        if not check_mode:
            previous_status = pull_partition_status(partition)
            partition.stop()
            status = pull_partition_status(partition)
            if status != 'stopped':
                raise StatusError(
                    "Could not get partition {!r} from {!r} status into "
                    "'stopped' status; current status is: {!r}".
                    format(partition.name, previous_status, status))
        changed = True
    return changed


def start_partition(partition, check_mode):
    """
    Ensure that the partition is started, by influencing the operational
    status of the partition, regardless of what its current operational status
    is.

    The resulting operational status will be one of START_END_STATUSES.

    Parameters:
      partition (zhmcclient.Partition): The partition (must exist, and its
        status property is assumed to be current).
      check_mode (bool): Indicates whether the playbook was run in check mode,
        in which case this method does not actually change the partition, but
        just returns what would have been done.

    Returns:
      bool: Indicates whether the partition was changed.

    Raises:
      StatusError: Partition is in one of BAD_STATUSES or did not reach a
        started status despite attempting it.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """
    changed = False
    partition.pull_full_properties()
    status = partition.get_property('status')
    if status in BAD_STATUSES:
        raise StatusError(
            "Target CPC {!r} has issues; status of partition {!r} is: {!r}".
            format(partition.manager.cpc.name, partition.name, status))
    elif status in START_END_STATUSES:
        pass
    elif status == 'stopping':
        if not check_mode:
            # Let it first finish the stopping
            partition.wait_for_status(STOP_END_STATUSES)
            stop_end_status = pull_partition_status(partition)
            # Then start it
            partition.start()
            status = pull_partition_status(partition)
            if status not in START_END_STATUSES:
                raise StatusError(
                    "Could not get partition {!r} from {!r} status into "
                    "a started status after waiting for its stopping to "
                    "complete; current status is: {!r}".
                    format(partition.name, stop_end_status, status))
        changed = True
    elif status == 'starting':
        if not check_mode:
            # Let it finish the starting
            partition.wait_for_status(START_END_STATUSES)
        changed = True
    else:
        if not check_mode:
            previous_status = pull_partition_status(partition)
            partition.start()
            status = pull_partition_status(partition)
            if status not in START_END_STATUSES:
                raise StatusError(
                    "Could not get partition {!r} from {!r} status into "
                    "a started status; current status is: {!r}".
                    format(partition.name, previous_status, status))
        changed = True
    return changed


def wait_for_transition_completion(partition):
    """
    If the partition is in a transitional state, wait for completion of that
    transition. This is required for updating properties.

    The resulting operational status will be one of START_END_STATUSES or
    STOP_END_STATUSES.

    Parameters:
      partition (zhmcclient.Partition): The partition (must exist, and its
        status property is assumed to be current).

    Raises:
      StatusError: Partition is in one of BAD_STATUSES.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """
    partition.pull_full_properties()
    status = partition.get_property('status')
    if status in BAD_STATUSES:
        raise StatusError(
            "Target CPC {!r} has issues; status of partition {!r} is: {!r}".
            format(partition.manager.cpc.name, partition.name, status))
    elif status == 'stopping':
        partition.wait_for_status(STOP_END_STATUSES)
    elif status == 'starting':
        partition.wait_for_status(START_END_STATUSES)
    else:
        assert status in START_END_STATUSES or status in STOP_END_STATUSES


def get_session(faked_session, host, userid, password):
    """
    Return a session object for the HMC.

    Parameters:
      faked_session (zhmcclient_mock.FakedSession or None):
        If this object is a `zhmcclient_mock.FakedSession` object, return that
        object.
        Else, return a new `zhmcclient.Session` object from the `host`,
        `userid`, and `password` arguments.
    """
    if isinstance(faked_session, FakedSession):
        return faked_session
    else:
        return Session(host, userid, password)


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
        raise TypeError("Value of {} cannot be converted to unicode: {!r}".
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
        type_cast). For details, see the modules using this function.

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

    allowed, create, update, update_while_active, eq_func, type_cast = \
        resource_properties[prop_name]

    # Double check that the property is not a read-only property
    assert allowed
    assert create or update

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
                    "Property {!r} can be set during {} "
                    "creation but cannot be updated afterwards "
                    "(from {!r} to {!r}).".
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
        logger.addHandler(handler)

    logger = logging.getLogger('zhmcclient.hmc')
    logger.setLevel(logging.DEBUG)
    if handler:
        logger.addHandler(handler)

    if False:  # Too much gorp, disabled for now
        logger = logging.getLogger('zhmcclient.api')
        logger.setLevel(logging.DEBUG)
        if handler:
            logger.addHandler(handler)
