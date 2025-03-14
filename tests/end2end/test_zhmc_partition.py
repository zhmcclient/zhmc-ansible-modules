# Copyright 2019,2020 IBM Corp. All Rights Reserved.
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
End2end tests for zhmc_partition module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import uuid
import copy
from unittest import mock
import re
import random
import pdb
from pprint import pformat
import pytest
import urllib3
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
from zhmcclient.testutils import dpm_mode_cpcs  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_partition
from plugins.module_utils.common import pull_partition_status
from .utils import mock_ansible_module, get_failure_msg, setup_logging, \
    skip_warn

urllib3.disable_warnings()

DEBUG = False  # Print debug messages

# Logging for zhmcclient HMC interactions and test functions
LOGGING = False
LOG_FILE = 'test_zhmc_partition.log' if LOGGING else None

# Partition properties that are not always present, but only under certain
# conditions.
PARTITION_CONDITIONAL_PROPS = (
    'boot-network-nic-name',
    'boot-storage-hba-name',
    'boot-storage-volume',  # added in z14
    'boot-load-parameters',  # added in z14
    'permit-ecc-key-import-functions',  # added in z15
    'ssc-boot-selection',  # only present for type=ssc
    'ssc-host-name',  # only present for type=ssc
    'ssc-ipv4-gateway',  # only present for type=ssc
    'ssc-ipv6-gateway',  # only present for type=ssc, added in z14
    'ssc-dns-servers',  # only present for type=ssc
    'ssc-master-userid',  # only present for type=ssc
    'secure-boot',  # added in SE/CPC 2.15.0
    'secure-execution',  # added in SE/CPC 2.15.0
    'tape-link-uris',  # added in z15
    'partition-link-uris',  # added in z16
)
# Partition properties that are never returned.
PARTITION_WRITEONLY_PROPS = (
    'ssc-master-pw',
    'boot-ftp-password',
)

# Artificial partition properties (added by the module).
PARTITION_ARTIFICIAL_PROPS = (
    'hbas',
    'nics',
    'virtual-functions',
    'boot-storage-group-name',
    'boot-storage-volume-name',
)

# Minimally allowed memory for partitions
MIN_MEMORY = 4096  # MB

# A standard test partition, as the Ansible module input properties (i.e. using
# underscores, and limited to valid input parameters)
STD_LINUX_PARTITION_MODULE_INPUT_PROPS = {
    # 'name': provided in separate module input parameter
    'description': "zhmc test partition",
    'ifl_processors': 2,
    'initial_memory': MIN_MEMORY,
    'maximum_memory': MIN_MEMORY,
}
STD_SSC_PARTITION_MODULE_INPUT_PROPS = {
    # 'name': provided in separate module input parameter
    'description': "zhmc test partition",
    'ifl_processors': 2,
    'initial_memory': MIN_MEMORY,
    'maximum_memory': MIN_MEMORY,
    'type': 'ssc',
    'ssc_host_name': 'sschost',
    'ssc_master_userid': 'sscuser',
    'ssc_master_pw': 'Need2ChangeSoon!',
}

# A standard test partition, as the input properties for
# UserRoleManager.create() (i.e. using dashes, and limited to valid input
# parameters)
STD_LINUX_PARTITION_HMC_INPUT_PROPS = {
    # 'name': updated upon use
    'description': "zhmc test partition",
    'ifl-processors': 2,
    'initial-memory': MIN_MEMORY,
    'maximum-memory': MIN_MEMORY,
}
STD_LINUX_PARTITION_HMC_EXP_PROPS = dict(STD_LINUX_PARTITION_HMC_INPUT_PROPS)
STD_SSC_PARTITION_HMC_INPUT_PROPS = {
    # 'name': updated upon use
    'description': "zhmc test partition",
    'ifl-processors': 2,
    'initial-memory': MIN_MEMORY,
    'maximum-memory': MIN_MEMORY,
    'type': 'ssc',
    'ssc-host-name': 'sschost',
    'ssc-master-userid': 'sscuser',
    'ssc-master-pw': 'Need2ChangeSoon!',
}
STD_SSC_PARTITION_HMC_EXP_PROPS = dict(STD_SSC_PARTITION_HMC_INPUT_PROPS)
del STD_SSC_PARTITION_HMC_EXP_PROPS['ssc-master-pw']


def storage_mgmt_enabled(cpc):
    """
    Return whether the CPC has the 'dpm-storage-management' feature enabled.
    """
    for feature_info in cpc.prop('available-features-list', []):
        if feature_info['name'] == 'dpm-storage-management':
            return feature_info['state']
    return False


def setup_partition(hd, cpc, name, properties, status='stopped'):
    """
    Create a new partition on the specified CPC, for test purposes.

    The desired status of the new partition can be specified (within limits).

    Parameters:
      hd(zhmcclient.testutils.HMCDefinition): HMC definition context.
      cpc(zhmcclient.Cpc): CPC on which the partition will be created.
      name(string): Partition name. Must not exist yet.
      properties(dict): Input properties for Partition.create(), with property
        names using HMC notation (with dashes).
      status(string): Desired value of the 'status' property of the
        partition upon return from this function. Only a certain subset of
        status values can be achieved:
        * For Linux-type partitions: 'stopped', 'starting', 'stopping', 'paused'.
        * For SSC-type partitions: 'stopped', 'starting', 'stopping', 'active'.
    """
    props = copy.deepcopy(properties)
    props['name'] = name

    try:

        if DEBUG:
            print(f"Debug: setup_partition: Creating test partition {name!r}")
        try:
            partition = cpc.partitions.create(props)
        except zhmcclient.HTTPError as exc:
            if exc.http_status == 403 and exc.reason == 1:
                # User is not permitted to create partitions
                pytest.skip(f"HMC user {hd.userid!r} is not permitted to "
                            f"create test partition on CPC {cpc.name!r}")
            else:
                raise

        # Add a NIC to the partition.
        # For SSC partitions, create it as an SSC mgmt NIC.
        osa_adapters = cpc.adapters.findall(**{'type': 'osd'})
        if len(osa_adapters) == 0:
            pytest.skip(f"No OSA adapters found on CPC {cpc.name!r}")
        osa_adapter = osa_adapters[0]
        vswitches = cpc.virtual_switches.findall(
            **{'backing-adapter-uri': osa_adapter.uri})
        vswitch = vswitches[0]  # any port is ok
        osa_port_index = vswitch.get_property('port')
        nic_properties = {
            'name': 'nic1',
            'description': f'OSA adapter {osa_adapter.name!r}, port index '
            f'{osa_port_index}',
            'virtual-switch-uri': vswitch.uri,
        }
        if partition.get_property('type') == 'ssc':
            nic_properties.update({
                'ssc-management-nic': True,
                'ssc-ip-address-type': 'ipv4',
                'ssc-ip-address': '10.11.12.13',
                'ssc-mask-prefix': '255.255.255.0',
            })
        partition.nics.create(nic_properties)

        # The partition is initially in status 'stopped'.
        # Establish the desired partition status.
        if status == 'stopped':
            if DEBUG:
                print(f"Debug: setup_partition: Test partition {name!r} is "
                      "already in status 'stopped'.")
        elif status == 'starting':
            if DEBUG:
                print("Debug: setup_partition: Getting test partition "
                      f"{name!r} into status 'starting'")
            try:
                partition.start(wait_for_completion=False)
            except zhmcclient.HTTPError as exc:
                if exc.http_status == 409 and exc.reason == 131:
                    # SSC partitions boot the built-in installer. However,
                    # there seems to be an issue where the SSC partition fails
                    # to start with "HTTPError: 409,131: The operating system in
                    # the partition failed to load. The partition is stopped.".
                    # Reported as STG Defect 1071321, and ignored in this test.
                    print("Warning: setup_partition: Ignoring failure when "
                          f"starting partition: {exc}")
                else:
                    raise AssertionError(
                        "Starting test partition without waiting for "
                        f"completion failed with: {exc}")
            except zhmcclient.Error as exc:
                raise AssertionError(
                    "Starting test partition without waiting for "
                    f"completion failed with: {exc}")
            current_status = pull_partition_status(partition)
            if current_status != 'starting':
                raise AssertionError(
                    "setup_partition: Starting test partition without waiting "
                    "for completion did not result in status 'starting', but "
                    f"in status {current_status!r}")
            if DEBUG:
                print("Debug: setup_partition: Successfully got test "
                      f"partition {name!r} into status 'starting'")
        elif status == 'stopping':
            if DEBUG:
                print("Debug: setup_partition: Getting test partition "
                      f"{name!r} into status 'stopping'")
            try:
                job = partition.start(wait_for_completion=False)
                job.wait_for_completion()
            except zhmcclient.Error as exc:
                raise AssertionError(
                    "setup_partition: Starting test partition and waiting for "
                    f"completion failed with: {exc}")
            try:
                partition.stop(wait_for_completion=False)
            except zhmcclient.Error as exc:
                raise AssertionError(
                    "setup_partition: Stopping test partition without waiting "
                    f"for completion failed with: {exc}")
            current_status = pull_partition_status(partition)
            if current_status != 'stopping':
                raise AssertionError(
                      "setup_partition: Stopping test partition without "
                      "waiting for completion did not result in status "
                      f"'stopping', but in status {current_status!r}")
            if DEBUG:
                print("Debug: setup_partition: Successfully got test partition "
                      f"{name!r} into status 'stopping'")
        elif status == 'active':
            ptype = partition.prop('type')
            if ptype != 'ssc':
                raise AssertionError(
                      "setup_partition: Testcase definition error: Status "
                      "'active' can only be requested for SSC-type partitions, "
                      f"but partition {name!r} has type {ptype!r}")
            if DEBUG:
                print("Debug: setup_partition: Getting SSC test partition "
                      f"{name!r} into status 'active'")
            try:
                job = partition.start(wait_for_completion=False)
                job.wait_for_completion()
            except zhmcclient.HTTPError as exc:
                if exc.http_status == 409 and exc.reason == 131:
                    # SSC partitions boot the built-in installer. However,
                    # there seems to be an issue where the SSC partition fails
                    # to start with "HTTPError: 409,131: The operating system in
                    # the partition failed to load. The partition is stopped.".
                    # Reported as STG Defect 1071321, and ignored in this test.
                    print("Warning: setup_partition: Ignoring failure when "
                          f"starting partition: {exc}")
                else:
                    raise AssertionError(
                        "setup_partition: Starting SSC test partition "
                        f"{name!r} and waiting for completion failed with: "
                        f"{exc}")
            except zhmcclient.Error as exc:
                raise AssertionError(
                    "setup_partition: Starting SSC test partition "
                    f"{name!r} and waiting for completion failed with: "
                    f"{exc}")
            current_status = pull_partition_status(partition)
            if current_status != 'active':
                raise AssertionError(
                    f"setup_partition: Starting SSC test partition {name!r} "
                    "and waiting for completion did not result in status "
                    f"'active', but in status {current_status!r}")
            if DEBUG:
                print("Debug: setup_partition: Successfully got SSC test "
                      f"partition {name!r} into status 'active'")
        elif status == 'paused':
            ptype = partition.prop('type')
            if ptype != 'linux':
                raise AssertionError(
                      "setup_partition: Testcase definition error: Status "
                      "'paused' can only be requested for linux-type "
                      f"partitions, but partition {name!r} has type {ptype!r}")
            if DEBUG:
                print("Debug: setup_partition: Getting Linux test partition "
                      f"{name!r} into status 'paused'")
            try:
                job = partition.start(wait_for_completion=False)
                job.wait_for_completion()
            except zhmcclient.Error as exc:
                raise AssertionError(
                    f"setup_partition: Starting Linux test partition {name!r} "
                    f"and waiting for completion failed with: {exc}")
            current_status = pull_partition_status(partition)
            if current_status != 'paused':
                raise AssertionError(
                    f"setup_partition: Starting Linux test partition {name!r} "
                    "and waiting for completion did not result in status "
                    f"'paused', but in status {current_status!r}")
            if DEBUG:
                print("Debug: setup_partition: Successfully got linux test "
                      f"partition {name!r} into status 'paused'")
        else:
            raise AssertionError(
                  "setup_partition: Testcase definition error: Status "
                  f"{status!r} cannot be requested for setting up partition "
                  f"{name!r}.")

    except zhmcclient.Error as exc:
        teardown_partition(cpc, name)
        pytest.skip("Error in HMC operation during test partition setup: "
                    f"{exc}")

    return partition


def teardown_partition(cpc, name):
    """
    Delete a partition created for test purposes by setup_partition().

    The partition is looked up by name. If it was alreay deleted by
    the test code, that is tolerated.

    If the partition is not in the stopped state, it is stopped before being
    deleted.

    Parameters:
      cpc(zhmcclient.Cpc): CPC on which the partition has been created.
      name(string): Partition name.
    """

    try:
        # We invalidate the name cache of our client, because the partition
        # was possibly deleted by the Ansible module and not through our
        # client instance.
        cpc.partitions.invalidate_cache()
        partition = cpc.partitions.find_by_name(name)
    except zhmcclient.NotFound:
        return

    status = pull_partition_status(partition)
    if status not in ('stopped', 'reservation-error'):
        if DEBUG:
            print("Debug: teardown_partition: Stopping test partition "
                  f"{name!r} with status {status!r}")
        try:
            job = partition.stop(wait_for_completion=False)
            job.wait_for_completion()
        except zhmcclient.Error as exc:
            print("Warning: teardown_partition: Stopping test partition "
                  f"{name!r} with status {status!r} on CPC {cpc.name!r} "
                  f"failed with: {exc}")

    if DEBUG:
        print(f"Debug: teardown_partition: Deleting test partition {name!r}")
    try:
        partition.delete()
    except zhmcclient.Error as exc:
        print(f"Warning: teardown_partition: Deleting test partition {name!r} "
              f"on CPC {cpc.name!r} failed with: {exc} - please clean it up "
              "manually!")
    if DEBUG:
        print("Debug: teardown_partition: Successfully deleted test partition "
              f"{name!r}")


def unique_partition_name():
    """
    Return a unique partition name.
    """
    random_str = str(uuid.uuid4()).replace('-', '')
    partition_name = f'zhmc_test_{random_str}'
    return partition_name


def unique_stogrp_name():
    """
    Return a unique storage group name.
    """
    random_str = str(uuid.uuid4()).replace('-', '')
    stogrp_name = f'zhmc_test_sg_{random_str}'
    return stogrp_name


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, partition_properties) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, partition):
        return changed, partition

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_partition_props(act_props, exp_props, where):
    """
    Assert the actual properties of a partition.

    Parameters:
      act_props(dict): Actual partition props to verify (with dashes).
      exp_props(dict): Expected partition properties (with dashes).
      where(string): Indicator about the testcase for assertion messages.
    """

    assert isinstance(act_props, dict), where  # Dict of User role props

    # Assert presence of properties in the output
    for prop_name in zhmc_partition.ZHMC_PARTITION_PROPERTIES:
        prop_name_hmc = prop_name.replace('_', '-')
        if prop_name_hmc in PARTITION_CONDITIONAL_PROPS:
            continue
        if prop_name_hmc in PARTITION_WRITEONLY_PROPS:
            continue
        where_prop = where + (f", property {prop_name_hmc!r} missing in "
                              f"partition properties {act_props!r}")
        assert prop_name_hmc in act_props, where_prop

    # Assert the expected property values for non-artificial properties
    for prop_name in exp_props:
        prop_name_hmc = prop_name.replace('_', '-')
        if prop_name_hmc in PARTITION_ARTIFICIAL_PROPS:
            continue
        if prop_name_hmc in PARTITION_WRITEONLY_PROPS:
            continue
        exp_value = exp_props[prop_name]
        act_value = act_props[prop_name]
        # For list properties, ignore the order of list items:
        if prop_name in ('acceptable-status',):
            exp_value = set(exp_value)
            act_value = set(act_value)
        where_prop = where + (", Unexpected value of property "
                              f"{prop_name_hmc!r}: Expected: {exp_value!r}, "
                              f"Actual: {act_value!r}")
        assert act_value == exp_value, where_prop

    # Assert type of the artificial properties in the output
    assert 'hbas' in act_props, where
    hba_props_list = act_props['hbas']
    if hba_props_list is not None:
        assert isinstance(hba_props_list, list), where  # List of HBAs
        for hba_props in hba_props_list:
            assert isinstance(hba_props, dict), where  # Dict of HBA properties
    assert 'nics' in act_props, where
    nic_props_list = act_props['nics']
    if nic_props_list is not None:
        assert isinstance(nic_props_list, list), where  # List of NICs
        for nic_props in nic_props_list:
            assert isinstance(nic_props, dict), where  # Dict of NIC properties
    assert 'virtual-functions' in act_props, where
    vf_props_list = act_props['virtual-functions']
    if vf_props_list is not None:
        assert isinstance(vf_props_list, list), where  # List of VFs
        for vf_props in vf_props_list:
            assert isinstance(vf_props, dict), where  # Dict of VF properties
    assert 'boot-storage-group-name' in act_props, where
    if 'boot-storage-group-name' in exp_props:
        exp_boot_sg_name = exp_props['boot-storage-group-name']
        assert act_props['boot-storage-group-name'] == exp_boot_sg_name
    assert 'boot-storage-volume-name' in act_props, where
    if 'boot-storage-volume-name' in exp_props:
        exp_boot_sv_name = exp_props['boot-storage-volume-name']
        assert act_props['boot-storage-volume-name'] == exp_boot_sv_name

    # Assert that none of the write-only properties is in the output object
    for prop_name in zhmc_partition.WRITEONLY_PROPERTIES_HYPHEN:
        assert prop_name not in act_props, where


PARTITION_FACTS_TESTCASES = [
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - select_properties (list): Input for select_properties module parm
    # - exp_prop_names (list): Names of expected properties in module
    #   result (HMC-formatted) in case of module success. The module may
    #   return more then those listed.
    # - not_prop_names (list): Names of unexpected properties in module
    #   result (HMC-formatted) in case of module success. The module must
    #   not return those listed.
    # - exp_msg (string): Expected message pattern in case of module failure,
    #   or None for module success.
    # - exp_changed (bool): Boolean for expected 'changed' flag.
    # - run: Indicates whether the test should be run, or 'pdb' for debugger.

    (
        "Default input parms = full properties",
        None,
        [
            'name',
            'object-uri',
            'description',
            'status',
            'partition-id',
        ],
        [],
        None,
        False,
        True,
    ),
    (
        "select empty list of properties",
        [],
        [
            'name',             # always returned
            'object-uri',       # always returned
        ],
        [
            'description',
            'status',
            'partition-id',
        ],
        None,
        False,
        True,
    ),
    (
        "select one property",
        ['description'],
        [
            'name',
            'object-uri',
            'description',
        ],
        [
            'status',
            'partition-id',
        ],
        None,
        False,
        True,
    ),
    (
        "select two properties",
        ['description', 'status'],
        [
            'name',
            'object-uri',
            'description',
            'status',
        ],
        [
            'partition-id',
        ],
        None,
        False,
        True,
    ),
    (
        "select property with underscore",
        ['partition_id'],
        [
            'name',
            'object-uri',
            'partition-id',
        ],
        [
            'description',
            'status',
        ],
        None,
        False,
        True,
    ),
    (
        "select property with hyphen",
        ['partition-id'],
        [
            'name',
            'object-uri',
            'partition-id',
        ],
        [
            'description',
            'status',
        ],
        None,
        False,
        True,
    ),
]


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@pytest.mark.parametrize(
    "desc, select_properties, exp_prop_names, not_prop_names, "
    "exp_msg, exp_changed, run",
    PARTITION_FACTS_TESTCASES)
@mock.patch("plugins.modules.zhmc_partition.AnsibleModule", autospec=True)
def test_zhmc_partition_facts(
        ansible_mod_cls,
        desc, select_properties, exp_prop_names, not_prop_names,
        exp_msg, exp_changed, run,
        check_mode, dpm_mode_cpcs):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name,unused-argument
    """
    Test the zhmc_partition module with state=facts on DPM mode CPCs.
    """
    if not dpm_mode_cpcs:
        pytest.skip("HMC definition does not include any CPCs in DPM mode")

    if not run:
        skip_warn("Testcase is disabled in testcase definition")

    setup_logging(LOGGING, 'test_zhmc_partition_facts', LOG_FILE)

    for cpc in dpm_mode_cpcs:
        assert cpc.dpm_enabled

        session = cpc.manager.session
        hd = session.hmc_definition
        hmc_host = hd.host
        hmc_auth = dict(userid=hd.userid, password=hd.password,
                        ca_certs=hd.ca_certs, verify=hd.verify)

        faked_session = session if hd.mock_file else None

        # Determine a random existing partition
        partitions = cpc.partitions.list()
        partition = random.choice(partitions)

        where = f"partition '{partition.name}'"

        # Prepare module input parameters (must be all required + optional)
        params = {
            'hmc_host': hmc_host,
            'hmc_auth': hmc_auth,
            'cpc_name': cpc.name,
            'name': partition.name,
            'state': 'facts',
            'select_properties': select_properties,
            'image_name': None,
            'image_file': None,
            'ins_file': None,
            'properties': {},
            'expand_storage_groups': False,
            'expand_crypto_adapters': False,
            'log_file': LOG_FILE,
            '_faked_session': faked_session,
        }

        # Prepare mocks for AnsibleModule object
        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        # Exercise the code to be tested
        with pytest.raises(SystemExit) as exc_info:
            zhmc_partition.main()
        exit_code = exc_info.value.args[0]

        # Assert module exit code
        assert exit_code == 0, \
            f"{where}: Module failed with exit code {exit_code} and " \
            f"message:\n{get_failure_msg(mod_obj)}"

        # Assert module output
        changed, part_properties = get_module_output(mod_obj)
        assert changed is False, \
            f"{where}: Module returned changed={changed}"

        # Check the presence and absence of properties in the result
        part_prop_names = list(part_properties.keys())
        for pname in exp_prop_names:
            assert pname in part_prop_names
        for pname in not_prop_names:
            assert pname not in part_prop_names


PARTITION_STATE_TESTCASES = [
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - initial_props (dict): HMC-formatted properties for initial
    #    partition, or None for no initial partition.
    # - initial_status (string): Status for initial partition, or None when no
    #   initial partition.
    # - input_state (string): 'state' input parameter for zhmc_partition
    #   module.
    # - input_props (dict): 'properties' input parameter for zhmc_partition
    #   module.
    # - exp_msg (string): Expected message pattern in case of module failure,
    #   or None for module success.
    # - exp_props (dict): HMC-formatted properties for expected
    #   properties of created partition.
    # - exp_changed (bool): Boolean for expected 'changed' flag.
    # - run: Indicates whether the test should be run, or 'pdb' for debugger.

    (
        "state=stopped for Linux partition with non-existing partition",
        None,
        None,
        'stopped',
        STD_LINUX_PARTITION_MODULE_INPUT_PROPS,
        None,
        STD_LINUX_PARTITION_HMC_EXP_PROPS,
        True,
        True,
    ),
    (
        "state=stopped for Linux partition with existing stopped partition, "
        "no properties changed",
        STD_LINUX_PARTITION_HMC_INPUT_PROPS,
        'stopped',
        'stopped',
        None,
        None,
        STD_LINUX_PARTITION_HMC_EXP_PROPS,
        False,
        True,
    ),
    (
        "state=stopped for Linux partition with existing paused partition, "
        "no properties changed",
        STD_LINUX_PARTITION_HMC_INPUT_PROPS,
        'paused',
        'stopped',
        None,
        None,
        STD_LINUX_PARTITION_HMC_EXP_PROPS,
        True,
        True,
    ),
    (
        "state=active for Linux partition with existing stopped partition, "
        "no properties changed",
        STD_LINUX_PARTITION_HMC_INPUT_PROPS,
        'stopped',
        'active',
        None,
        "StatusError: Abandoning the start of partition .* after reaching "
        "status 'paused'.*",
        None,
        None,
        True,
    ),
    (
        "state=active for Linux partition with existing paused partition, "
        "no properties changed",
        STD_LINUX_PARTITION_HMC_INPUT_PROPS,
        'paused',
        'active',
        None,
        "StatusError: Abandoning the start of partition .* after reaching "
        "status 'paused'.*",
        None,
        None,
        True,
    ),
    (
        "state=stopped for Linux partition with existing stopped partition, "
        "some properties changed",
        dict(STD_LINUX_PARTITION_HMC_INPUT_PROPS).update({
            'description': 'bla',
        }),
        'stopped',
        'stopped',
        STD_LINUX_PARTITION_MODULE_INPUT_PROPS,
        None,
        STD_LINUX_PARTITION_HMC_EXP_PROPS,
        True,
        True,
    ),
    (
        "state=stopped for SSC partition with non-existing partition",
        None,
        None,
        'stopped',
        STD_SSC_PARTITION_MODULE_INPUT_PROPS,
        None,
        STD_SSC_PARTITION_HMC_EXP_PROPS,
        True,
        True,
    ),
    # Note: state=active for a non-existing SSC partition requires the addition
    #       of an SSC mgmt NIC before the partition can be started. This case
    #       is not part of these testcases, which invoke the zhmc_partition
    #       module only once.
    (
        "state=stopped for SSC partition with existing stopped partition, "
        "no properties changed",
        STD_SSC_PARTITION_HMC_INPUT_PROPS,
        'stopped',
        'stopped',
        None,
        None,
        STD_SSC_PARTITION_HMC_EXP_PROPS,
        False,
        True,
    ),
    (
        "state=active for SSC partition with existing stopped partition, "
        "no properties changed",
        STD_SSC_PARTITION_HMC_INPUT_PROPS,
        'stopped',
        'active',
        None,
        None,  # Code ignores "HTTPError: 409,131"
        STD_SSC_PARTITION_HMC_EXP_PROPS,
        True,
        True,
    ),
    (
        "state=stopped for SSC partition with existing stopped partition, "
        "some properties changed",
        dict(STD_SSC_PARTITION_HMC_INPUT_PROPS).update({
            'description': 'bla',
        }),
        'stopped',
        'stopped',
        STD_SSC_PARTITION_MODULE_INPUT_PROPS,
        None,
        STD_SSC_PARTITION_HMC_EXP_PROPS,
        True,
        True,
    ),
    (
        "state=absent with existing stopped Linux partition",
        STD_LINUX_PARTITION_HMC_INPUT_PROPS,
        'stopped',
        'absent',
        None,
        None,
        None,
        True,
        True,
    ),
    (
        "state=absent with existing stopped SSC partition",
        STD_SSC_PARTITION_HMC_INPUT_PROPS,
        'stopped',
        'absent',
        None,
        None,
        None,
        True,
        True,
    ),
    (
        "state=absent with non-existing partition",
        None,
        None,
        'absent',
        None,
        None,
        None,
        False,
        True,
    ),
]


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@pytest.mark.parametrize(
    "desc, initial_props, initial_status, input_state, input_props, exp_msg, "
    "exp_props, exp_changed, run",
    PARTITION_STATE_TESTCASES)
@mock.patch("plugins.modules.zhmc_partition.AnsibleModule", autospec=True)
def test_zhmc_partition_state(
        ansible_mod_cls,
        desc, initial_props, initial_status, input_state, input_props, exp_msg,
        exp_props, exp_changed, run,
        check_mode, dpm_mode_cpcs):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_partition module with different initial and target state.
    """

    if not dpm_mode_cpcs:
        pytest.skip("HMC definition does not include any CPCs in DPM mode")

    if not run:
        pytest.skip(f"Testcase disabled: {desc}")

    setup_logging(LOGGING, 'test_zhmc_partition_state', LOG_FILE)

    for cpc in dpm_mode_cpcs:
        assert cpc.dpm_enabled

        session = cpc.manager.session
        hd = session.hmc_definition
        hmc_host = hd.host
        hmc_auth = dict(userid=hd.userid, password=hd.password,
                        ca_certs=hd.ca_certs, verify=hd.verify)

        if hd.mock_file:
            pytest.skip("Asynchronous partition start/stop not supported "
                        "in zhmcclient_mock")

        faked_session = session if hd.mock_file else None

        # Create a partition name that does not exist
        partition_name = unique_partition_name()

        where = f"partition '{partition_name}'"

        if input_props is not None:
            input_props2 = input_props.copy()
        else:
            input_props2 = None

        # Create initial partition, if specified so
        if initial_props is not None:
            setup_partition(
                hd, cpc, partition_name, initial_props, initial_status)

        try:

            # Prepare module input parameters (must be all required + optional)
            params = {
                'hmc_host': hmc_host,
                'hmc_auth': hmc_auth,
                'cpc_name': cpc.name,
                'name': partition_name,
                'state': input_state,
                'select_properties': None,
                'image_name': None,
                'image_file': None,
                'ins_file': None,
                'properties': input_props2,
                'expand_storage_groups': False,
                'expand_crypto_adapters': False,
                'log_file': LOG_FILE,
                '_faked_session': faked_session,
            }

            mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

            with pytest.raises(SystemExit) as exc_info:

                if run == 'pdb':
                    pdb.set_trace()  # pylint: disable=forgotten-debug-statement

                # Exercise the code to be tested
                zhmc_partition.main()

            exit_code = exc_info.value.args[0]

            if exit_code != 0:
                msg = get_failure_msg(mod_obj)
                if msg.startswith('HTTPError: 403,1'):
                    pytest.skip(f"HMC user '{hd.userid}' is not permitted to "
                                "create test partition")
                if msg.startswith('HTTPError: 409,131'):
                    # SSC partitions boot the built-in installer. However,
                    # there seems to be an issue where the SSC partition fails
                    # to start with "HTTPError: 409,131: The operating system in
                    # the partition failed to load. The partition is stopped.".
                    # Reported as STG Defect 1071321, and ignored in this test.
                    print(f"Warning: Ignoring module failure: {msg}")
                    return
                assert exp_msg is not None, \
                    f"{where}: Module should have succeeded but failed with " \
                    f"exit code {exit_code} and message:\n{msg}"
                assert re.search(exp_msg, msg), \
                    f"{where}: Module failed as expected, but the error " \
                    f"message is unexpected:\n{msg}"
            else:
                assert exp_msg is None, \
                    f"{where}: Module should have failed but succeeded. " \
                    f"Expected failure message pattern:\n{exp_msg!r}"

                changed, output_props = get_module_output(mod_obj)
                if changed != exp_changed:
                    initial_props_sorted = \
                        dict(sorted(initial_props.items(), key=lambda x: x[0]))\
                        if initial_props is not None else None
                    input_props_sorted = \
                        dict(sorted(input_props2.items(), key=lambda x: x[0])) \
                        if input_props2 is not None else None
                    output_props_sorted = \
                        dict(sorted(output_props.items(), key=lambda x: x[0])) \
                        if output_props is not None else None
                    initial_props_str = pformat(initial_props_sorted, indent=2)
                    input_props_str = pformat(input_props_sorted, indent=2)
                    output_props_str = pformat(output_props_sorted, indent=2)
                    raise AssertionError(
                        f"Unexpected change flag returned: actual: {changed}, "
                        f"expected: {exp_changed}\n"
                        f"Initial partition properties:\n{initial_props_str}\n"
                        f"Module input properties:\n{input_props_str}\n"
                        f"Resulting partition properties:\n{output_props_str}")
                if input_state != 'absent':
                    assert_partition_props(output_props, exp_props, where)

        finally:
            teardown_partition(cpc, partition_name)


# New values for updating properties.
# Each list item is a single testcase. These testcases are executed in the
# order of items in the list against the same partition, so the results of
# earlier updates become the initial state for later updates.
# Each list item (testcase) is a dict of one or more new property values for
# the 'properties' input parameter of the Ansible module, i.e. property names
# are specified with underscores and include artificial properties supported
# by the Ansible module.
# New values of integer type can be specified as integer or decimal string.
# If the new value is a tuple, the first item is the value to be used as input
# for the properties parameter of the Ansible module, and the second item is
# the resulting HMC property value for comparison.

# Properties to be used as base
PARTITION_UPDATE_ITEMS_BASE = [
    {'description': 'fake'},
    {'description': 'fak\u00E9'},
    {'short_name': f'ZHMC{random.randrange(16 ^ 4):04X}'},  # noqa: E231
    {'acceptable_status': ['active', 'stopped', 'degraded']},
    {'ifl_absolute_processor_capping': True},
    {'ifl_absolute_processor_capping_value': 0.9},
    {'ifl_absolute_processor_capping_value': ("0.8", 0.8)},
    {'ifl_processing_weight_capped': True},
    {'ifl_processing_weight_capped': False},
    {'ifl_absolute_processor_capping': False},
    {'minimum_ifl_processing_weight': 10},
    {'minimum_ifl_processing_weight': ("9", 9)},
    {'maximum_ifl_processing_weight': 200},
    {'maximum_ifl_processing_weight': ("199", 199)},
    {'initial_ifl_processing_weight': 50},
    {'initial_ifl_processing_weight': ("49", 49)},
    {'cp_absolute_processor_capping': True},
    {'cp_absolute_processor_capping_value': 0.9},
    {'cp_absolute_processor_capping_value': ("0.8", 0.8)},
    {'cp_processing_weight_capped': True},
    {'cp_processing_weight_capped': False},
    {'cp_absolute_processor_capping': False},
    {'minimum_cp_processing_weight': 10},
    {'minimum_cp_processing_weight': ("9", 9)},
    {'maximum_cp_processing_weight': 200},
    {'maximum_cp_processing_weight': ("199", 199)},
    {'initial_cp_processing_weight': 50},
    {'initial_cp_processing_weight': ("49", 49)},
    # Enabling processor management requires weight capping disabled, but on
    # S67B still fails with HTTPError: 500,12: "Internal error: Minimum weight
    # : 0can't be zero when work load managment is enabled".
    # {'processor_management_enabled': True},
    # {'processor_management_enabled': False},
    {'access_global_performance_data': True},
    {'permit_cross_partition_commands': True},
    {'access_basic_counter_set': True},
    {'access_problem_state_counter_set': True},
    {'access_crypto_activity_counter_set': True},
    {'access_extended_counter_set': True},
    {'access_coprocessor_group_set': True},
    {'access_basic_sampling': True},
    {'access_diagnostic_sampling': True},
    {'permit_des_key_import_functions': False},
    {'permit_aes_key_import_functions': False},
    # TODO: Ensure the partition ID is not used yet
    # {'partition_id': '7F'},
    # {'autogenerate_partition_id': False},
    {'ifl_processors': 3},
    {'ifl_processors': ("4", 4)},
    # TODO: Switching processor type requires partition to be stopped.
    #       Create separate tests for that.
    # {'cp_processors': 1, 'ifl_processors': 0},
    # {'cp_processors': ("0", 0), 'ifl_processors': ("1", 1)},
    # TODO: processor_mode=dedicated may fail with 409,116 due to not enough
    #       resources. Create separate tests for that.
    # {'reserve_resources': True},
    # {'processor_mode': 'dedicated'},
    # {'processor_mode': 'shared'},
    {'initial_memory': 6144, 'maximum_memory': 6144},
    {'initial_memory': ("8192", 8192), 'maximum_memory': ("8192", 8192)},
    # TODO: reserve_resources=True may fail with 409,116 due to not enough
    #       resources. Create separate tests for that.
    # {'reserve_resources': True},
    {'reserve_resources': False},
    {'boot_timeout': 120},
    {'boot_timeout': ("100", 100)},
    {'boot_os_specific_parameters': 'fake'},
]

# Properties to be used as base for Linux type partitions
PARTITION_UPDATE_ITEMS_BASE_LINUX = PARTITION_UPDATE_ITEMS_BASE + [
    # TODO: Create an OSA/HS NIC and use it for this:
    # {
    #     'boot_device': 'network-adapter',
    #     'boot_network_nic_name': nic_name,
    # },
    {
        'boot_device': 'ftp',
        'boot_ftp_host': 'fake',
        'boot_ftp_username': 'fake',
        'boot_ftp_password': 'fake',
        'boot_ftp_insfile': 'fake',
    },
    {
        'boot_device': 'removable-media',
        'boot_removable_media': 'fake',
        'boot_removable_media_type': 'cdrom',
    },
    # TODO: Add support for mounting ISO image via boot_iso_image_name prop:
    # {
    #     'boot_device': 'iso-image',
    #     'boot_iso_image_name': 'bla',  # must be valid
    #     'boot_iso_ins_file': 'bla',
    # },
]
# Properties to be used as base for SSC type partitions
PARTITION_UPDATE_ITEMS_BASE_SSC = PARTITION_UPDATE_ITEMS_BASE + [
    # Note: ssc_boot_selection can only be changed from 'appliance' to 'installer'
    {'ssc_host_name': 'fake'},
    {'ssc_ipv4_gateway': '10.11.12.13'},
    {'ssc_dns_servers': ['10.11.12.13']},
    {'ssc_master_userid': 'sscuser2', 'ssc_master_pw': 'ShouldChangeIt2!'},
]

# Properties that should be tested on z13 (first generation with DPM mode):
PARTITION_UPDATE_ITEMS_Z13_LINUX = PARTITION_UPDATE_ITEMS_BASE_LINUX + [
    # TODO: Create an HBA and use it for this:
    # {
    #     'boot_device': 'storage-adapter',
    #     'boot_storage_hba_name': hba_name,
    #     'boot_logical_unit_number': '0123',
    #     'boot_world_wide_port_name': '0123456789abcdef',
    # },
]
PARTITION_UPDATE_ITEMS_Z13_SSC = PARTITION_UPDATE_ITEMS_BASE_SSC

# Properties that should be tested on z14:
PARTITION_UPDATE_ITEMS_Z14_LINUX = PARTITION_UPDATE_ITEMS_BASE_LINUX + [
    # TODO: Create a boot volume and use it for this:
    # {
    #     'boot_device': 'storage-volume',
    #     'boot_storage_volume_name': volume_name,
    #     'boot_record_lba': "12ff",
    #     'boot_configuration_selector': ("3", 3),
    # },
]
PARTITION_UPDATE_ITEMS_Z14_SSC = PARTITION_UPDATE_ITEMS_BASE_SSC

# Properties that should be tested on z15:
PARTITION_UPDATE_ITEMS_Z15_LINUX = PARTITION_UPDATE_ITEMS_Z14_LINUX
PARTITION_UPDATE_ITEMS_Z15_SSC = PARTITION_UPDATE_ITEMS_Z14_SSC

# Properties that should be tested on z16:
PARTITION_UPDATE_ITEMS_Z16_LINUX = PARTITION_UPDATE_ITEMS_Z15_LINUX
PARTITION_UPDATE_ITEMS_Z16_SSC = PARTITION_UPDATE_ITEMS_Z15_SSC
# access-coprocessor-group-set has become read-only in z16
PARTITION_UPDATE_ITEMS_Z16_LINUX.remove({'access_coprocessor_group_set': True})
PARTITION_UPDATE_ITEMS_Z16_SSC.remove({'access_coprocessor_group_set': True})

# Properties that do not come back with Get Partition Properies:
NON_RETRIEVABLE_PROPS = ('boot_ftp_password', 'ssc_master_pw')


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@pytest.mark.parametrize(
    "type_state", [
        pytest.param(('linux', 'stopped'), id="type=linux,state=stopped"),
        pytest.param(('ssc', 'stopped'), id="type=ssc,state=stopped"),
        pytest.param(('ssc', 'active'), id="type=ssc,state=active"),
    ]
)
@mock.patch("plugins.modules.zhmc_partition.AnsibleModule", autospec=True)
def test_zhmc_partition_properties(
        ansible_mod_cls, type_state, check_mode, dpm_mode_cpcs):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_partition module with updating properties.
    """

    if not dpm_mode_cpcs:
        pytest.skip("HMC definition does not include any CPCs in DPM mode")

    setup_logging(LOGGING, 'test_zhmc_partition_properties', LOG_FILE)

    partition_type, state = type_state

    for cpc in dpm_mode_cpcs:
        assert cpc.dpm_enabled

        session = cpc.manager.session
        hd = session.hmc_definition
        hmc_host = hd.host
        hmc_auth = dict(userid=hd.userid, password=hd.password,
                        ca_certs=hd.ca_certs, verify=hd.verify)

        if hd.mock_file:
            pytest.skip("Asynchronous partition start/stop not supported "
                        "in zhmcclient_mock")

        faked_session = session if hd.mock_file else None

        # Create a partition name that does not exist
        partition_name = unique_partition_name()

        # Create initial partition
        if partition_type == 'ssc':
            create_props = STD_SSC_PARTITION_HMC_INPUT_PROPS
        else:
            create_props = STD_LINUX_PARTITION_HMC_INPUT_PROPS
        create_props['type'] = partition_type
        if state == 'active':
            if partition_type == 'linux':
                initial_status = 'paused'
            else:
                assert partition_type == 'ssc'
                initial_status = 'active'
        else:
            assert state == 'stopped'
            initial_status = 'stopped'
        partition = setup_partition(
            hd, cpc, partition_name, create_props, initial_status)

        try:

            # The test is optimized for runtime - we use the same partition
            # for all updates.
            machine_type = cpc.get_property('machine-type')
            if machine_type in ('2964', '2965'):
                # z13
                if partition_type == 'ssc':
                    update_items = PARTITION_UPDATE_ITEMS_Z13_SSC
                else:
                    update_items = PARTITION_UPDATE_ITEMS_Z13_LINUX
            elif machine_type in ('3906', '3907'):
                # z14
                if partition_type == 'ssc':
                    update_items = PARTITION_UPDATE_ITEMS_Z14_SSC
                else:
                    update_items = PARTITION_UPDATE_ITEMS_Z14_LINUX
            elif machine_type in ('8561', '8562'):
                # z15
                if partition_type == 'ssc':
                    update_items = PARTITION_UPDATE_ITEMS_Z15_SSC
                else:
                    update_items = PARTITION_UPDATE_ITEMS_Z15_LINUX
            elif machine_type in ('3931', '3932'):
                # z16
                if partition_type == 'ssc':
                    update_items = PARTITION_UPDATE_ITEMS_Z16_SSC
                else:
                    update_items = PARTITION_UPDATE_ITEMS_Z16_LINUX
            else:
                raise AssertionError(
                    f"Unknown machine type: {machine_type!r}")

            for update_item in update_items:

                if DEBUG:
                    print(f"Debug: Testcase: update_item={update_item!r}")

                where = f"update_item {update_item!r}"

                partition.pull_full_properties()

                update_props = {}
                exp_props = {}
                exp_exit_code = 0
                exp_changed = False
                for prop_name in update_item:
                    prop_hmc_name = prop_name.replace('_', '-')
                    if prop_name in NON_RETRIEVABLE_PROPS:
                        current_hmc_value = '<non-retrievable>'
                    else:
                        current_hmc_value = partition.get_property(
                            prop_hmc_name)
                    value_item = update_item[prop_name]
                    if isinstance(value_item, tuple):
                        new_value = value_item[0]
                        new_hmc_value = value_item[1]
                    else:
                        new_value = value_item
                        new_hmc_value = value_item
                    # pylint: disable=unused-variable
                    allowed, create, update, update_while_active, eq_func, \
                        type_cast, required, default = \
                        zhmc_partition.ZHMC_PARTITION_PROPERTIES[prop_name]

                    # Note that update_while_active will be handled in the
                    # Ansible module by stopping the partition, updating the
                    # porperty and starting the partition.
                    if not update:
                        exp_exit_code = 1
                    else:
                        if prop_name in NON_RETRIEVABLE_PROPS:
                            exp_changed = True
                        elif current_hmc_value != new_hmc_value:
                            exp_changed = True

                    if DEBUG:
                        print(f"Debug: Property {prop_hmc_name!r}: "
                              f"update={update}, "
                              f"update_while_active={update_while_active}, "
                              f"current_hmc_value={current_hmc_value!r}, "
                              f"new_value={new_value!r}, "
                              f"new_hmc_value={new_hmc_value!r}")
                    update_props[prop_name] = new_value
                    if prop_name not in NON_RETRIEVABLE_PROPS:
                        exp_props[prop_hmc_name] = new_hmc_value

                if 'cp_processors' in update_props:
                    cpc_cp_count = cpc.get_property(
                        'processor-count-general-purpose')
                    if DEBUG:
                        print(f"Debug: CPC has {cpc_cp_count} CPs")
                    if cpc_cp_count < 2:
                        if DEBUG:
                            print("Debug: CPC has not enough CPs; "
                                  f"skipping update item: {update_item!r}")
                        continue
                if 'ifl_processors' in update_props:
                    cpc_ifl_count = cpc.get_property('processor-count-ifl')
                    if DEBUG:
                        print(f"Debug: CPC has {cpc_ifl_count} IFLs")
                    if cpc_ifl_count < 2:
                        if DEBUG:
                            print("Debug: CPC has not enough IFLs; "
                                  f"skipping update item: {update_item!r}")
                        continue

                initial_props = copy.deepcopy(partition.properties)

                if DEBUG:
                    print("Debug: Calling module with "
                          f"properties={update_props!r}")

                # Prepare module input parms (must be all required + optional)
                params = {
                    'hmc_host': hmc_host,
                    'hmc_auth': hmc_auth,
                    'cpc_name': cpc.name,
                    'name': partition_name,
                    'state': state,  # no state change
                    'select_properties': None,
                    'image_name': None,
                    'image_file': None,
                    'ins_file': None,
                    'properties': update_props,
                    'expand_storage_groups': False,
                    'expand_crypto_adapters': False,
                    'log_file': LOG_FILE,
                    '_faked_session': faked_session,
                }

                mod_obj = mock_ansible_module(
                    ansible_mod_cls, params, check_mode)

                # Exercise the code to be tested
                with pytest.raises(SystemExit) as exc_info:
                    zhmc_partition.main()
                exit_code = exc_info.value.args[0]

                if exit_code != 0:
                    msg = get_failure_msg(mod_obj)
                    if msg.startswith('HTTPError: 403,1'):
                        pytest.skip(f"HMC user '{hd.userid}' is not permitted "
                                    "to create test partition")
                    msg_str = f" and failed with message:\n{msg}"  # noqa: E231
                else:
                    msg_str = ''
                if exit_code != exp_exit_code:
                    raise AssertionError(
                        f"{where}: Module has unexpected exit code "
                        f"{exit_code}: {msg_str}")

                changed, output_props = get_module_output(mod_obj)
                if changed != exp_changed:
                    initial_props_sorted = \
                        dict(sorted(
                            initial_props.items(), key=lambda x: x[0])) \
                        if initial_props is not None else None
                    update_props_sorted = \
                        dict(sorted(update_props.items(), key=lambda x: x[0])) \
                        if update_props is not None else None
                    output_props_sorted = \
                        dict(sorted(output_props.items(), key=lambda x: x[0])) \
                        if output_props is not None else None
                    initial_props_str = pformat(initial_props_sorted, indent=2)
                    update_props_str = pformat(update_props_sorted, indent=2)
                    output_props_str = pformat(output_props_sorted, indent=2)
                    raise AssertionError(
                        f"{where}: Unexpected change flag returned: "
                        f"actual: {changed}, expected: {exp_changed}\n"
                        f"Initial partition properties:\n{initial_props_str}\n"
                        f"Module input properties:\n{update_props_str}\n"
                        f"Resulting partition properties:\n{output_props_str}")

                assert_partition_props(output_props, exp_props, where)

        finally:
            teardown_partition(cpc, partition_name)


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@pytest.mark.parametrize(
    "via", [
        pytest.param('uri', id="via=uri"),
        pytest.param('name', id="via=name"),
    ]
)
@pytest.mark.parametrize(
    "type_state", [
        pytest.param(('linux', 'stopped'), id="type=linux,state=stopped"),
    ]
)
@mock.patch("plugins.modules.zhmc_partition.AnsibleModule", autospec=True)
def test_zhmc_partition_boot_stovol(
        ansible_mod_cls, type_state, via, check_mode, dpm_mode_cpcs):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_partition module when configuring boot from a storage volume.
    """

    if not dpm_mode_cpcs:
        pytest.skip("HMC definition does not include any CPCs in DPM mode")

    setup_logging(LOGGING, 'test_zhmc_partition_boot_stovol', LOG_FILE)

    partition_type, state = type_state

    for cpc in dpm_mode_cpcs:
        assert cpc.dpm_enabled

        if not storage_mgmt_enabled(cpc):
            pytest.skip(f"CPC {cpc.name} does not have the "
                        "'dpm-storage-management' feature enabled")

        console = cpc.manager.console
        session = cpc.manager.session
        hd = session.hmc_definition
        hmc_host = hd.host
        hmc_auth = dict(userid=hd.userid, password=hd.password,
                        ca_certs=hd.ca_certs, verify=hd.verify)

        faked_session = session if hd.mock_file else None

        if hd.mock_file:
            pytest.skip("zhmcclient mock support does not implement "
                        "storage group attachment")

        # Create a partition name that does not exist
        partition_name = unique_partition_name()

        # Create initial partition
        assert partition_type == 'linux'
        create_props = STD_LINUX_PARTITION_HMC_INPUT_PROPS
        create_props['type'] = partition_type
        partition = setup_partition(hd, cpc, partition_name, create_props,
                                    state)

        stogrp = None
        try:

            # Create a storage group with a boot volume
            stogrp_name = unique_stogrp_name()
            stogrp = console.storage_groups.create({
                'name': stogrp_name,
                'cpc-uri': cpc.uri,
                'type': 'fcp',
            })
            boot_volume = stogrp.storage_volumes.create({
                'name': 'vol1',
                'size': 8,
                'usage': 'boot',
            })

            # Attach the storage group to the partition
            # Note: It is not fulfilled. Yet, attachment works.
            partition.attach_storage_group(stogrp)

            if via == 'name':
                update_props = {
                    'boot_device': 'storage-volume',
                    'boot_storage_group_name': stogrp.name,
                    'boot_storage_volume_name': boot_volume.name,
                }
            else:
                assert via == 'uri'
                update_props = {
                    'boot_device': 'storage-volume',
                    'boot_storage_volume': boot_volume.uri,
                }

            if DEBUG:
                print(f"Debug: Calling module with properties={update_props!r}")

            # Prepare module input parms (must be all required + optional)
            params = {
                'hmc_host': hmc_host,
                'hmc_auth': hmc_auth,
                'cpc_name': cpc.name,
                'name': partition_name,
                'state': state,  # no state change
                'select_properties': None,
                'image_name': None,
                'image_file': None,
                'ins_file': None,
                'properties': update_props,
                'expand_storage_groups': False,
                'expand_crypto_adapters': False,
                'log_file': LOG_FILE,
                '_faked_session': faked_session,
            }

            mod_obj = mock_ansible_module(
                ansible_mod_cls, params, check_mode)

            # Exercise the code to be tested
            with pytest.raises(SystemExit) as exc_info:
                zhmc_partition.main()
            exit_code = exc_info.value.args[0]

            if check_mode:
                # Check mode of the zhmc_partition module does not implement
                # the check for the boot volume to be fulfilled.
                exp_exit_code = 0
                exp_msg_pattern = None
            else:
                # We are in a real HMC environment, without check mode.
                # The HMC does not allow configuring boot from storage volume
                # when the volume is not fulfilled.
                exp_exit_code = 1
                exp_msg_pattern = "HTTPError: 409,122: Storage volume is not " \
                    "fulfilled"

            if exit_code != 0:
                msg = get_failure_msg(mod_obj)
                if exit_code != exp_exit_code:
                    raise AssertionError(
                        "Module unexpectedly failed with exit code "
                        f"{exit_code}, message: {msg}")
                if not re.search(exp_msg_pattern, msg):
                    raise AssertionError(
                        "Module failed as expected with exit code "
                        f"{exit_code}, but message does not match expected "
                        f"pattern {exp_msg_pattern}: {msg}")
            else:
                changed, result = get_module_output(mod_obj)
                if exit_code != exp_exit_code:
                    raise AssertionError(
                        "Module unexpectedly succeeded with changed: "
                        f"{changed}, result: {result}")

        finally:
            if stogrp:
                partition.detach_storage_group(stogrp)
                stogrp.delete()
            teardown_partition(cpc, partition_name)


PARTITION_ISO_MOUNT_TESTCASES = [
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - image_name (string): image_name module input parameter.
    # - image_file (string): image_file module input parameter.
    # - ins_file (string): ins_file module input parameter.
    # - exp_msg (string): Expected message pattern in case of module failure,
    #   or None for module success.
    # - exp_changed (bool): Boolean for expected 'changed' flag.

    (
        "Missing required input parameter image_name",
        None,
        'foo',
        'bar',
        "Missing required module input parameter",
        False,
    ),
    (
        "Missing required input parameter image_file",
        'foo',
        None,
        'bar',
        "Missing required module input parameter",
        False,
    ),
    (
        "Missing required input parameter ins_file",
        'foo',
        'bar',
        None,
        "Missing required module input parameter",
        False,
    ),
    (
        "ISO image file does not exist",
        'my_image',
        './non-existing.iso',
        '/dummy.ins',
        "Cannot open ISO image file",
        False,
    ),
    # TODO: Testcases with valid ISO file
]


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@pytest.mark.parametrize(
    "desc, image_name, image_file, ins_file, exp_msg, exp_changed",
    PARTITION_ISO_MOUNT_TESTCASES)
@mock.patch("plugins.modules.zhmc_partition.AnsibleModule", autospec=True)
def test_zhmc_partition_iso_mount(
        ansible_mod_cls,
        desc, image_name, image_file, ins_file, exp_msg, exp_changed,
        check_mode, dpm_mode_cpcs):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name,unused-argument
    """
    Test the zhmc_partition module with state='iso_mount'.
    """

    if not dpm_mode_cpcs:
        pytest.skip("HMC definition does not include any CPCs in DPM mode")

    for cpc in dpm_mode_cpcs:
        assert cpc.dpm_enabled

        session = cpc.manager.session
        hd = session.hmc_definition
        hmc_host = hd.host
        hmc_auth = dict(userid=hd.userid, password=hd.password,
                        ca_certs=hd.ca_certs, verify=hd.verify)

        faked_session = session if hd.mock_file else None

        if hd.mock_file:
            pytest.skip("zhmcclient mock support does not implement "
                        "ISO mount")

        # Create a partition name that does not exist
        partition_name = unique_partition_name()

        # Create initial partition
        create_props = STD_LINUX_PARTITION_HMC_INPUT_PROPS
        create_props['type'] = 'linux'
        partition = setup_partition(hd, cpc, partition_name, create_props,
                                    'stopped')

        try:

            # Prepare module input parms (must be all required + optional)
            params = {
                'hmc_host': hmc_host,
                'hmc_auth': hmc_auth,
                'cpc_name': cpc.name,
                'name': partition_name,
                'state': 'iso_mount',
                'image_name': image_name,
                'image_file': image_file,
                'ins_file': ins_file,
                'properties': None,
                'expand_storage_groups': False,
                'expand_crypto_adapters': False,
                'log_file': LOG_FILE,
                '_faked_session': faked_session,
            }

            mod_obj = mock_ansible_module(
                ansible_mod_cls, params, check_mode)

            # Exercise the code to be tested
            with pytest.raises(SystemExit) as exc_info:
                zhmc_partition.main()
            exit_code = exc_info.value.args[0]

            if exit_code != 0:
                msg = get_failure_msg(mod_obj)
                if not exp_msg:
                    raise AssertionError(
                        "Module unexpectedly failed with exit code "
                        f"{exit_code}, message: {msg}")
                if not re.search(exp_msg, msg):
                    raise AssertionError(
                        "Module failed as expected with exit code "
                        f"{exit_code}, but message does not match expected "
                        f"pattern {exp_msg}: {msg}")
            else:
                changed, result = get_module_output(mod_obj)
                if exp_msg:
                    raise AssertionError(
                        "Module unexpectedly succeeded with changed: "
                        f"{changed}, result: {result}")

        finally:
            image_name = partition.get_property('boot-iso-image-name')
            if image_name:
                partition.unmount_iso_image()
            teardown_partition(cpc, partition_name)


# TODO: Testcases for ISO unmount
