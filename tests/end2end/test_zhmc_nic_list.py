# Copyright 2025 IBM Corp. All Rights Reserved.
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
End2end tests for zhmc_nic_list module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import random
from unittest import mock
import pytest
import urllib3
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
from zhmcclient.testutils import dpm_mode_cpcs  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_nic_list
from .utils import mock_ansible_module, get_failure_msg, setup_logging

urllib3.disable_warnings()

# Create log file
LOGGING = True

LOG_FILE = 'test_zhmc_nic_list.log' if LOGGING else None


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, nic_properties) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, nics):
        return changed, nics

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_nic_list(nic_list, exp_nic_dict):
    """
    Assert the output of the zhmc_nic_list module

    Parameters:

      nic_list(list): Result of zhmc_nic_list module, as a list of
        dicts of NIC properties as documented (with underscores in their
        names).

      exp_nic_dict(dict): Expected NICs with their properties.
        Key: tuple(CPC name, partition name, NIC name).
        Value: Dict of expected NIC properties (including any artificial
        properties, all with underscores in their names).
    """

    assert isinstance(nic_list, list)

    exp_nic_keys = list(exp_nic_dict.keys())
    nic_keys = [(item.get('cpc_name', None), item.get('partition_name', None),
                item.get('name', None)) for item in nic_list]
    assert set(nic_keys) == set(exp_nic_keys)

    for nic_item in nic_list:
        nic_name = nic_item.get('name', None)
        part_name = nic_item.get('partition_name', None)
        cpc_name = nic_item.get('cpc_name', None)
        nic_key = (cpc_name, part_name, nic_name)

        assert nic_name is not None, \
            f"Returned NIC {nic_item!r} does not have a 'name' property"

        assert part_name is not None, \
            f"Returned NIC {nic_item!r} does not have a 'part_name' property"

        assert cpc_name is not None, \
            f"Returned NIC {nic_item!r} does not have a 'cpc_name' property"

        assert nic_key in exp_nic_dict, \
            f"Result contains unexpected NIC {nic_name!r} in partition " \
            f"{part_name!r} in CPC {cpc_name!r}"

        exp_nic_properties = exp_nic_dict[nic_key]
        for pname, pvalue in nic_item.items():
            assert '-' not in pname, \
                f"Property {pname!r} in NIC {nic_name!r} is " \
                "returned with hyphens in the property name"
            assert pname in exp_nic_properties, \
                f"Unexpected property {pname!r} in result NIC " \
                f"{nic_name!r}. Expected properties: " \
                f"{list(exp_nic_properties.keys())!r}"
            exp_value = exp_nic_properties[pname]
            assert pvalue == exp_value, \
                f"Incorrect value for property {pname!r} of result NIC " \
                f"{nic_name!r}"
        act_nic_pnames = list(nic_item.keys())
        for pname in exp_nic_properties.keys():
            assert pname in act_nic_pnames, \
                f"Missing property {pname!r} in result NIC " \
                f"{nic_name!r}. Expected properties: " \
                f"{list(exp_nic_properties.keys())!r}"


@pytest.mark.parametrize(
    "property_flags", [
        pytest.param(
            {}, id="property_flags()"),
        pytest.param(
            {'full_properties': True},
            id="property_flags(full_properties=True)"),
        pytest.param(
            {'full_properties': True, 'expand_names': True},
            id="property_flags(full_properties=True,expand_names=True)"),
        pytest.param(
            {'expand_names': True},
            id="property_flags(expand_names=True)"),
    ]
)
@pytest.mark.parametrize(
    "partition_type", [
        pytest.param('ssc', id="partition_type=ssc"),
        pytest.param('linux', id="partition_type=linux"),
    ]
)
@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_nic_list.AnsibleModule", autospec=True)
def test_zhmc_nic_list(
        ansible_mod_cls, check_mode, partition_type, property_flags,
        dpm_mode_cpcs):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_nic_list module with DPM mode CPCs.
    """
    if not dpm_mode_cpcs:
        pytest.skip("HMC definition does not include any CPCs in DPM mode")

    logger = setup_logging(LOGGING, 'test_zhmc_nic_list', LOG_FILE)
    logger.debug("Entered test function with: "
                 "check_mode=%r, partition_type=%r, property_flags=%r",
                 check_mode, partition_type, property_flags)

    for cpc in dpm_mode_cpcs:
        assert cpc.dpm_enabled

        session = cpc.manager.session
        hd = session.hmc_definition
        hmc_host = hd.host
        hmc_auth = dict(userid=hd.userid, password=hd.password,
                        ca_certs=hd.ca_certs, verify=hd.verify)

        # Pick a test partition
        filter_args = {'type': partition_type}
        partitions = cpc.partitions.list(filter_args=filter_args)
        if not partitions:
            pytest.skip(f"CPC {cpc.name} does not have any partitions of "
                        f"type {partition_type}")
        partition = random.choice(partitions)

        logger.debug("Testing with CPC %s, partition %s (type %s)",
                     cpc.name, partition.name, partition_type)

        faked_session = session if hd.mock_file else None

        full_properties = property_flags.get('full_properties', False)
        expand_names = property_flags.get('expand_names', False)

        # Determine the expected NICs
        logger.debug("Listing expected NICs of partition %r", partition.name)
        exp_nics = partition.nics.list(full_properties=full_properties)

        # Determine expected NIC properties
        exp_nic_dict = {}
        for nic in exp_nics:
            exp_properties = {
                'cpc_name': cpc.name,
                'partition_name': partition.name,
                'name': nic.name,
            }
            if full_properties:
                for pname_hmc, pvalue in nic.properties.items():
                    pname = pname_hmc.replace('-', '_')
                    exp_properties[pname] = pvalue
            if full_properties and expand_names:
                port = nic.backing_port()
                adapter = port.manager.parent
                exp_properties['adapter_id'] = \
                    adapter.get_property('adapter-id')
                exp_properties['adapter_name'] = adapter.name
                exp_properties['adapter_port'] = port.get_property('index')
            logger.debug("Expected properties of NIC %r are: %r",
                         nic.name, exp_properties)
            exp_nic_key = (cpc.name, partition.name, nic.name)
            exp_nic_dict[exp_nic_key] = exp_properties

        # Prepare module input parameters (must be all required + optional)
        params = {
            'hmc_host': hmc_host,
            'hmc_auth': hmc_auth,
            'cpc_name': cpc.name,
            'partition_name': partition.name,
            'full_properties': full_properties,
            'expand_names': expand_names,
            'log_file': LOG_FILE,
            '_faked_session': faked_session,
        }

        # Prepare mocks for AnsibleModule object
        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        # Exercise the code to be tested
        with pytest.raises(SystemExit) as exc_info:
            zhmc_nic_list.main()
        exit_code = exc_info.value.args[0]

        # Assert module exit code
        assert exit_code == 0, \
            f"Module failed with exit code {exit_code} and message:\n" \
            f"{get_failure_msg(mod_obj)}"

        # Assert module output
        changed, nic_list = get_module_output(mod_obj)
        assert changed is False

        assert_nic_list(nic_list, exp_nic_dict)

    logger.debug("Leaving test function")
