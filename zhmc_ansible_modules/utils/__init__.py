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
STARTED_STATUSES = ('active', 'degraded', 'reservation-error')

# Partition status values that may happen after Partition.stop()
STOPPED_STATUSES = ('stopped', 'terminated', 'paused')

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


def stop_partition(partition, check_mode):
    """
    Ensure that the partition is stopped, by influencing the operational
    status of the partition, regardless of what its current operational status
    is.

    The resulting operational status will be one of STOPPED_STATUSES.

    Parameters:
      partition (zhmcclient.Partition): The partition (must exist, and its
        status property is assumed to be current).
      check_mode (bool): Indicates whether the playbook was run in check mode,
        in which case this method does ot actually stop the partition, but
        just returns what would have been done.

    Returns:
      bool: Indicates whether the partition was changed.

    Raises:
      StatusError: Partition is in one of BAD_STATUSES.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """
    changed = False
    partition.pull_full_properties()
    status = partition.get_property('status')
    if status in BAD_STATUSES:
        raise StatusError(
            "Target CPC {!r} has issues; status of partition {!r} is: {!r}".
            format(partition.manager.cpc.name, partition.name, status))
    elif status == 'starting':
        if not check_mode:
            # Let it first finish the starting
            partition.wait_for_status(STARTED_STATUSES)
            partition.stop()
        changed = True
    elif status == 'stopping':
        if not check_mode:
            partition.wait_for_status(STOPPED_STATUSES)
        changed = True
    elif status in STARTED_STATUSES:
        if not check_mode:
            partition.stop()
        changed = True
    else:
        assert status in STOPPED_STATUSES
    return changed


def start_partition(partition, check_mode):
    """
    Ensure that the partition is started, by influencing the operational
    status of the partition, regardless of what its current operational status
    is.

    The resulting operational status will be one of STARTED_STATUSES.

    Parameters:
      partition (zhmcclient.Partition): The partition (must exist, and its
        status property is assumed to be current).
      check_mode (bool): Indicates whether the playbook was run in check mode,
        in which case this method does not actually change the partition, but
        just returns what would have been done.

    Returns:
      bool: Indicates whether the partition was changed.

    Raises:
      StatusError: Partition is in one of BAD_STATUSES.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """
    changed = False
    partition.pull_full_properties()
    status = partition.get_property('status')
    if status in BAD_STATUSES:
        raise StatusError(
            "Target CPC {!r} has issues; status of partition {!r} is: {!r}".
            format(partition.manager.cpc.name, partition.name, status))
    elif status == 'stopping':
        if not check_mode:
            # Let it first finish the stopping
            partition.wait_for_status(STOPPED_STATUSES)
            partition.start()
        changed = True
    elif status == 'starting':
        if not check_mode:
            partition.wait_for_status(STARTED_STATUSES)
        changed = True
    elif status in STOPPED_STATUSES:
        if not check_mode:
            partition.start()
        changed = True
    else:
        assert status in STARTED_STATUSES
    return changed


def wait_for_transition_completion(partition):
    """
    If the partition is in a transitional state, wait for completion of that
    transition. This is required for updating properties.

    The resulting operational status will be one of STARTED_STATUSES or
    STOPPED_STATUSES.

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
        partition.wait_for_status(STOPPED_STATUSES)
    elif status == 'starting':
        partition.wait_for_status(STARTED_STATUSES)
    else:
        assert status in STARTED_STATUSES or status in STOPPED_STATUSES


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

    The input value may be a binary string or a unicode string, or None.
    If it is a binary string, it is encoded to a unicode string using UTF-8.
    """
    if isinstance(value, six.binary_type):
        return value.decode('utf-8')
    elif isinstance(value, six.text_type):
        return value
    elif value is None:
        return None
    else:
        raise TypeError("Value is not a binary or unicode string: {!r} {}".
                        format(value, type(value)))
