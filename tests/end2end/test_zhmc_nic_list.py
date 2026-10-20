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
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
from zhmcclient.testutils import dpm_mode_cpcs  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_nic_list
from .utils import mock_ansible_module, get_failure_msg, get_hmc_auth, \
    underscored_properties
from .conftest import LOG_FILE


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, nics)
    (i.e. the arguments of the call to exit_json()).
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


def assert_nic_list(act_nic_list, exp_nic_dict):
    """
    Assert the output of the zhmc_nic_list module.

    Parameters:

      act_nic_list (list of dict): Actual result of the module,
        as a list of properties (name: value), including any artificial
        properties. The property names must be as returned by the module.

      exp_nic_dict (dict of dict): Expected properties,
        as a dict (key: properties) where key is a tuple(CPC name, partition
        name, NIC name) and properties is a dict (name: value), including any
        artificial properties. The property names must be as returned by the
        zhmcclient list method (i.e. with hyphens).
    """
    assert isinstance(act_nic_list, list)
    assert isinstance(exp_nic_dict, dict)

    assert len(act_nic_list) == len(exp_nic_dict), (
        "Unexpected number of NICs:\n"
        f"Actual objects: {act_nic_list!r}\n"
        f"Expected objects: {exp_nic_dict!r}\n"
    )
    for act_nic_properties in act_nic_list:
        assert isinstance(act_nic_properties, dict)

        # Check for the key properties
        assert 'cpc_name' in act_nic_properties, (
            "Returned NIC does not have a 'cpc_name' "
            f"property: {act_nic_properties!r}")
        cpc_name = act_nic_properties['cpc_name']
        assert 'partition_name' in act_nic_properties, (
            "Returned NIC does not have a 'partition_name' "
            f"property: {act_nic_properties!r}")
        partition_name = act_nic_properties['partition_name']
        assert 'name' in act_nic_properties, (
            "Returned NIC does not have a 'name' "
            f"property: {act_nic_properties!r}")
        nic_name = act_nic_properties['name']
        nic_key = (cpc_name, partition_name, nic_name)

        assert nic_key in exp_nic_dict, (
            f"Unexpected returned NIC {nic_key!r}")

        exp_nic_properties = exp_nic_dict[nic_key]
        assert isinstance(exp_nic_properties, dict)
        exp_nic_properties = underscored_properties(exp_nic_properties)

        exp_nic_pnames = list(exp_nic_properties.keys())
        act_nic_pnames = list(act_nic_properties.keys())

        # Check the actually returned objects against the expected properties.
        # This discovers unexpected properties.
        for pname, act_value in act_nic_properties.items():
            assert '-' not in pname, (
                f"Property {pname!r} in returned "
                f"NIC {nic_key!r} "
                "has hyphens in the property name")
            assert pname in exp_nic_properties, (
                f"Unexpected property {pname!r} in returned "
                f"NIC {nic_key!r}:\n"
                f"Expected properties: {exp_nic_pnames}\n"
                f"Actual properties: {act_nic_pnames}")
            exp_value = exp_nic_properties[pname]
            assert act_value == exp_value, (
                f"Incorrect value for property {pname!r} of returned "
                f"NIC {nic_key!r}:\n"
                f"Expected value: {exp_value!r}\n"
                f"Actual value: {act_value!r}")

        # Check the expected properties against the actually returned objects.
        # This discovers missing properties.
        for pname, exp_value in exp_nic_properties.items():
            assert pname in act_nic_properties, (
                f"Missing property {pname!r} in returned "
                f"NIC {nic_key!r}:\n"
                f"Expected properties: {exp_nic_pnames}\n"
                f"Actual properties: {act_nic_pnames}")
            act_value = act_nic_properties[pname]
            assert act_value == exp_value, (
                f"Incorrect value for property {pname!r} of returned "
                f"NIC {nic_key!r}:\n"
                f"Expected value: {exp_value!r}\n"
                f"Actual value: {act_value!r}")


@pytest.mark.parametrize(
    "property_flags", [
        pytest.param(
            {}, id="property_flags()"),
        pytest.param(
            {'expand_names': True},
            id="property_flags(expand_names=True)"),
        pytest.param(
            {'additional_properties': ['description']},
            id="property_flags(additional_properties=[description])"),
        pytest.param(
            {'additional_properties': ['description'], 'expand_names': True},
            id="property_flags(additional_properties=[description]),"
            "expand_names=True"),
        pytest.param(
            {'full_properties': True},
            id="property_flags(full_properties=True)"),
        pytest.param(
            {'full_properties': True, 'expand_names': True},
            id="property_flags(full_properties=True,expand_names=True)"),
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
        test_logger, dpm_mode_cpcs):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_nic_list module with DPM mode CPCs.
    """
    if not dpm_mode_cpcs:
        pytest.skip("HMC definition does not include any CPCs in DPM mode")

    test_logger.debug(
        "Test parameters: check_mode=%r, partition_type=%r, property_flags=%r",
        check_mode, partition_type, property_flags)

    for cpc in dpm_mode_cpcs:
        assert cpc.dpm_enabled

        session = cpc.manager.session

        hmc_host = session.host
        hmc_auth = get_hmc_auth(session)
        hd = session.hmc_definition
        faked_session = session if hd.mock_file else None

        # Pick a test partition
        filter_args = {'type': partition_type}
        partitions = cpc.partitions.list(filter_args=filter_args)
        if not partitions:
            pytest.skip(f"CPC {cpc.name} does not have any partitions of "
                        f"type {partition_type}")
        partition = random.choice(partitions)

        test_logger.debug(
            "Testing with CPC %s, partition %s (type %s)",
            cpc.name, partition.name, partition_type)

        # Get the module arguments for the test.
        # We need to use the defaults defined in the module argument spec
        additional_properties = property_flags.get('additional_properties', [])
        full_properties = property_flags.get('full_properties', False)
        expand_names = property_flags.get('expand_names', False)

        # Make sure that the result has the 'name' property of the NIC
        if not full_properties:
            if not additional_properties:
                additional_properties = ['name']
            elif 'name' not in additional_properties:
                additional_properties = list(additional_properties)
                additional_properties.append('name')

        # Determine the expected NICs on the HMC
        exp_nics = partition.nics.list(
            additional_properties=additional_properties,
            full_properties=full_properties)

        # Prepare the expected data for comparison
        exp_nic_dict = {}
        for nic in exp_nics:
            exp_properties = {
                'cpc_name': cpc.name,
                'cpc_uri': cpc.uri,
                'partition_name': partition.name,
                'partition_uri': partition.uri,
            }
            exp_properties.update(nic.properties)
            if expand_names:
                port = nic.backing_port()
                adapter = port.manager.parent
                exp_properties['adapter_id'] = \
                    adapter.get_property('adapter-id')
                exp_properties['adapter_name'] = adapter.name
                exp_properties['adapter_uri'] = adapter.uri
                exp_properties['adapter_port'] = port.get_property('index')
            exp_nic_key = (cpc.name, partition.name, nic.name)
            exp_nic_dict[exp_nic_key] = exp_properties

        # Prepare module input parameters (must be all required + optional)
        params = {
            'hmc_host': hmc_host,
            'hmc_auth': hmc_auth,
            'cpc_name': cpc.name,
            'partition_name': partition.name,
            'additional_properties': additional_properties,
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
