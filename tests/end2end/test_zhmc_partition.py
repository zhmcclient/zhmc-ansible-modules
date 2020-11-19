# Copyright 2019-2020 IBM Corp. All Rights Reserved.
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

import pytest
import mock
import requests.packages.urllib3
import zhmcclient
from zhmcclient.testutils.hmc_definition_fixtures import hmc_definition, hmc_session  # noqa: F401, E501

from plugins.modules import zhmc_partition
from .utils import mock_ansible_module, get_failure_msg

requests.packages.urllib3.disable_warnings()


# Partition properties that are not always present, nbut only under certain
# conditions.
PARTITION_CONDITIONAL_PROPS = (
    'boot-ftp-password',
    'boot-network-nic-name',
    'boot-storage-hba-name',
    'ssc-master-pw',
)


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


def assert_partition_props(partition_props):
    """
    Assert the output object of the zhmc_partition module
    """
    assert isinstance(partition_props, dict)  # Dict of Partition properties

    # Assert presence of normal properties in the output
    for prop_name in zhmc_partition.ZHMC_PARTITION_PROPERTIES:
        prop_name_hmc = prop_name.replace('_', '-')
        if prop_name_hmc in PARTITION_CONDITIONAL_PROPS:
            # TODO: Do better than just skipping them - they are present under
            # certain conditions.
            continue
        assert prop_name_hmc in partition_props

    # Assert presence of the artificial properties in the output

    assert 'hbas' in partition_props
    hba_props_list = partition_props['hbas']
    if hba_props_list is not None:
        assert isinstance(hba_props_list, list)  # List of HBAs
        for hba_props in hba_props_list:
            assert isinstance(hba_props, dict)  # Dict of HBA properties

    assert 'nics' in partition_props
    nic_props_list = partition_props['nics']
    if nic_props_list is not None:
        assert isinstance(nic_props_list, list)  # List of NICs
        for nic_props in nic_props_list:
            assert isinstance(nic_props, dict)  # Dict of NIC properties

    assert 'virtual-functions' in partition_props
    vf_props_list = partition_props['virtual-functions']
    if vf_props_list is not None:
        assert isinstance(vf_props_list, list)  # List of VFs
        for vf_props in vf_props_list:
            assert isinstance(vf_props, dict)  # Dict of VF properties


@pytest.mark.parametrize(
    "check_mode", [False, True])
@mock.patch("plugins.modules.zhmc_partition.AnsibleModule", autospec=True)
def test_partition_facts(ansible_mod_cls, check_mode, hmc_session):  # noqa: F811, E501
    """
    Test fact gathering on a partition.
    """

    hd = hmc_session.hmc_definition

    # Determine one of the CPCs in the HMC definition file to test
    cpc_names = hd.cpcs.keys()
    assert len(cpc_names) >= 1
    cpc_name = cpc_names[0]

    # Determine an existing partition to test. This also validates that
    # the CPC defined in the HMC definition file actually exists.
    client = zhmcclient.Client(hmc_session)
    cpc = client.cpcs.find_by_name(cpc_name)
    partitions = cpc.partitions.list()
    assert len(partitions) >= 1
    partition = partitions[0]  # Pick first partition in list

    # Prepare module input parameters
    params = {
        'hmc_host': hd.hmc_host,
        'hmc_auth': dict(userid=hd.hmc_userid, password=hd.hmc_password),
        'cpc_name': cpc_name,
        'name': partition.name,
        'state': 'facts',
        'log_file': None,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_partition.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, \
        "Module unexpectedly failed with this message:\n{0}". \
        format(get_failure_msg(mod_obj))

    # Assert module output
    changed, partition_props = get_module_output(mod_obj)
    assert changed is False
    assert_partition_props(partition_props)
