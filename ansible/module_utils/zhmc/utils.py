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


class ParameterError(Exception):
    """
    Indicates an error with the module input parameters.
    """
    pass


class StatusError(Exception):
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
    try:
        int_actual = int(hex_actual, 16)
    except ValueError:
        raise ParameterError(
            "Unexpected: Actual value of property {!r} is not a valid hex "
            "number: {!r}".
            format(prop_name, hex_actual))
    try:
        int_new = int(hex_new, 16)
    except ValueError:
        raise ParameterError(
            "New value for property {!r} is not a valid hex number: {!r}".
            format(prop_name, hex_new))
    return int_actual == int_new


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
