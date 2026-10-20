# Copyright 2026 IBM Corp. All Rights Reserved.
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
End2end tests for zhmc_storage_group_list module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import random
from unittest import mock
import pytest
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_storage_group_list
from .utils import mock_ansible_module, get_failure_msg, get_hmc_auth, \
    available_dpm_cpcs, underscored_properties
from .conftest import LOG_FILE


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, storage_groups)
    (i.e. the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, storage_groups):
        return changed, storage_groups

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_storage_group_list(act_stogroup_list, exp_stogroup_dict):
    """
    Assert the output of the zhmc_storage_group_list module.

    Parameters:

      act_stogroup_list (list of dict): Actual result of the module,
        as a list of properties (name: value), including any artificial
        properties. The property names must be as returned by the module.

      exp_stogroup_dict (dict of dict): Expected properties,
        as a dict (key: properties) where key is the object name and properties
        is a dict (name: value), including any artificial properties. The
        property names must be as returned by the zhmcclient list method.
        (i.e. with hyphens).
    """
    assert isinstance(act_stogroup_list, list)
    assert isinstance(exp_stogroup_dict, dict)

    assert len(act_stogroup_list) == len(exp_stogroup_dict), (
        "Unexpected number of storage groups:\n"
        f"Actual objects: {act_stogroup_list!r}\n"
        f"Expected objects: {exp_stogroup_dict!r}\n"
    )
    for act_stogroup_properties in act_stogroup_list:
        assert isinstance(act_stogroup_properties, dict)

        # Check for the key property
        assert 'name' in act_stogroup_properties, (
            "Returned storage group does not have a 'name' "
            f"property: {act_stogroup_properties!r}")
        stogroup_name = act_stogroup_properties['name']
        assert stogroup_name in exp_stogroup_dict, (
            f"Unexpected returned storage group {stogroup_name!r}")

        exp_stogroup_properties = exp_stogroup_dict[stogroup_name]
        assert isinstance(exp_stogroup_properties, dict)
        exp_stogroup_properties = underscored_properties(exp_stogroup_properties)

        exp_stogroup_pnames = list(exp_stogroup_properties.keys())
        act_stogroup_pnames = list(act_stogroup_properties.keys())

        # Check the actually returned objects against the expected properties.
        # This discovers unexpected properties.
        # Note that the underlying zhmcclient list method implements
        # additional_properties by returning all properties. However, the check
        # for unexpected properties still works because both the Ansible module
        # under test and the test function use the same zhmcclient list method.
        for pname, act_value in act_stogroup_properties.items():
            assert '-' not in pname, (
                f"Property {pname!r} in returned "
                f"storage group {stogroup_name!r} "
                "has hyphens in the property name")
            assert pname in exp_stogroup_properties, (
                f"Unexpected property {pname!r} in returned "
                f"storage group {stogroup_name!r}:\n"
                f"Expected properties: {exp_stogroup_pnames}\n"
                f"Actual properties: {act_stogroup_pnames}")
            exp_value = exp_stogroup_properties[pname]
            assert act_value == exp_value, (
                f"Incorrect value for property {pname!r} of returned "
                f"storage group {stogroup_name!r}:\n"
                f"Expected value: {exp_value!r}\n"
                f"Actual value: {act_value!r}")

        # Check the expected properties against the actually returned objects.
        # This discovers missing properties.
        for pname, exp_value in exp_stogroup_properties.items():
            assert pname in act_stogroup_properties, (
                f"Missing property {pname!r} in returned "
                f"storage group {stogroup_name!r}:\n"
                f"Expected properties: {exp_stogroup_pnames}\n"
                f"Actual properties: {act_stogroup_pnames}")
            act_value = act_stogroup_properties[pname]
            assert act_value == exp_value, (
                f"Incorrect value for property {pname!r} of returned "
                f"storage group {stogroup_name!r}:\n"
                f"Expected value: {exp_value!r}\n"
                f"Actual value: {act_value!r}")


@pytest.mark.parametrize(
    "property_flags", [
        pytest.param({}, id="property_flags()"),
        pytest.param({'additional_properties': ['description']},
                     id="property_flags(additional_properties=[description])"),
        pytest.param({'full_properties': True},
                     id="property_flags(full_properties=True)"),
    ]
)
@pytest.mark.parametrize(
    "filter_args", [
        pytest.param({'use_name_filter': True},
                     id="filter_args(use_name_filter=True)"),
        pytest.param({'use_cpc_name_filter': True},
                     id="filter_args(use_cpc_name_filter=True)"),
        pytest.param({'type': 'fcp'},
                     id="filter_args(type=fcp)"),
        pytest.param({'fulfillment_state': 'complete'},
                     id="filter_args(fulfillment_state=complete)"),
    ]
)
@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_storage_group_list.AnsibleModule",
            autospec=True)
def test_zhmc_storage_group_list(
        ansible_mod_cls, check_mode, filter_args, property_flags,
        hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_storage_group_list module.
    """

    hmc_host = hmc_session.host
    hmc_auth = get_hmc_auth(hmc_session)
    hd = hmc_session.hmc_definition
    faked_session = hmc_session if hd.mock_file else None

    client = zhmcclient.Client(hmc_session)
    console = client.consoles.console

    # Get the module arguments for the test.
    # We need to use the defaults defined in the module argument spec
    additional_properties = property_flags.get('additional_properties', [])
    full_properties = property_flags.get('full_properties', False)
    type = filter_args.get('type', None)
    fulfillment_state = filter_args.get('fulfillment_state', None)
    use_name_filter = filter_args.get('use_name_filter', False)
    use_cpc_name_filter = filter_args.get('use_cpc_name_filter', False)

    # The testcases require that the CPC associated with the storage group
    # is available. Skip this test if there is no available DPM mode CPC.
    cpcs = available_dpm_cpcs(client.cpcs.list())
    if not cpcs:
        pytest.skip("No available DPM mode CPCs")

    cpc_by_uri = {cpc.uri: cpc for cpc in cpcs}

    # Pick a random storage group and its associated CPC
    all_storage_groups = console.storage_groups.list()
    if len(all_storage_groups) == 0:
        pytest.skip("This HMC has no storage groups")
    picked_storage_group = random.choice(all_storage_groups)
    picked_cpc_uri = picked_storage_group.get_property('cpc-uri')
    picked_cpc = cpc_by_uri[picked_cpc_uri]

    # Determine the expected list of storage groups
    filter_args = {}
    if use_cpc_name_filter:
        filter_args['cpc-uri'] = picked_cpc_uri
    if use_name_filter:
        filter_args['name'] = picked_storage_group.name
    if type:
        filter_args['type'] = type
    if fulfillment_state:
        filter_args['fulfillment-state'] = fulfillment_state
    exp_storage_groups = console.storage_groups.list(
        filter_args=filter_args,
        additional_properties=additional_properties,
        full_properties=full_properties)
    exp_storage_group_dict = {}
    for storage_group in exp_storage_groups:
        cpc_uri = storage_group.get_property('cpc-uri')
        cpc_name = cpc_by_uri[cpc_uri].get_property('name')
        exp_properties = {
            'cpc_name': cpc_name
        }
        exp_properties.update(storage_group.properties)
        exp_storage_group_dict[storage_group.name] = exp_properties

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'name': picked_storage_group.name if use_name_filter else None,
        'cpc_name': picked_cpc.name if use_cpc_name_filter else None,
        'type': type,
        'fulfillment_state': fulfillment_state,
        'additional_properties': additional_properties,
        'full_properties': full_properties,
        'log_file': LOG_FILE,
        '_faked_session': faked_session,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_storage_group_list.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, \
        f"Module failed with exit code {exit_code} and message:\n" \
        f"{get_failure_msg(mod_obj)}"

    # Assert module output
    changed, storage_group_list = get_module_output(mod_obj)
    assert changed is False

    assert_storage_group_list(storage_group_list, exp_storage_group_dict)
