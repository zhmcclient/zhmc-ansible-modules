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
End2end tests for zhmc_storage_volume_list module.
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

from plugins.modules import zhmc_storage_volume_list
from .utils import mock_ansible_module, get_failure_msg, get_hmc_auth, \
    available_dpm_cpcs, underscored_properties
from .conftest import LOG_FILE


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, storage_volumes)
    (i.e. the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, storage_volumes):
        return changed, storage_volumes

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_storage_volume_list(
        act_stovol_list, exp_stovol_dict, stogroup_name):
    """
    Assert the output of the zhmc_storage_group_list module.

    Parameters:

      act_stovol_list (list of dict): Actual result of the module,
        as a list of properties (name: value), including any artificial
        properties. The property names must be as returned by the module.

      exp_stovol_dict (dict of dict): Expected properties,
        as a dict (key: properties) where key is the object name and properties
        is a dict (name: value), including any artificial properties. The
        property names must be as returned by the zhmcclient list method.
        (i.e. with hyphens).

      stogroup_name (str): Name of the parent storage group, for messages.
    """
    assert isinstance(act_stovol_list, list)
    assert isinstance(exp_stovol_dict, dict)

    assert len(act_stovol_list) == len(exp_stovol_dict), (
        f"Unexpected number of volumes in storage group {stogroup_name!r}:\n"
        f"Actual objects: {act_stovol_list!r}\n"
        f"Expected objects: {exp_stovol_dict!r}\n"
    )
    for act_stovol_properties in act_stovol_list:
        assert isinstance(act_stovol_properties, dict)

        # Check for the key property
        assert 'name' in act_stovol_properties, (
            f"Returned storage volume in storage group {stogroup_name!r} "
            f"does not have a 'name' property: {act_stovol_properties!r}")
        stovol_name = act_stovol_properties['name']
        assert stovol_name in exp_stovol_dict, (
            f"Unexpected returned storage volume {stovol_name!r} in "
            f"storage group {stogroup_name!r} ")

        exp_stovol_properties = exp_stovol_dict[stovol_name]
        assert isinstance(exp_stovol_properties, dict)
        exp_stovol_properties = underscored_properties(exp_stovol_properties)

        exp_stovol_pnames = list(exp_stovol_properties.keys())
        act_stovol_pnames = list(act_stovol_properties.keys())

        # Check the actually returned objects against the expected properties.
        # This discovers unexpected properties.
        # Note that the underlying zhmcclient list method implements
        # additional_properties by returning all properties. However, the check
        # for unexpected properties still works because both the Ansible module
        # under test and the test function use the same zhmcclient list method.
        for pname, act_value in act_stovol_properties.items():
            assert '-' not in pname, (
                f"Property {pname!r} in returned "
                f"storage volume {stovol_name!r} "
                f"in storage group {stogroup_name!r} "
                "has hyphens in the property name")
            assert pname in exp_stovol_properties, (
                f"Unexpected property {pname!r} in returned "
                f"storage volume {stovol_name!r} "
                f"in storage group {stogroup_name!r}:\n"
                f"Expected properties: {exp_stovol_pnames}\n"
                f"Actual properties: {act_stovol_pnames}")
            exp_value = exp_stovol_properties[pname]
            assert act_value == exp_value, (
                f"Incorrect value for property {pname!r} of returned "
                f"storage volume {stovol_name!r} "
                f"in storage group {stogroup_name!r}:\n"
                f"Expected value: {exp_value!r}\n"
                f"Actual value: {act_value!r}")

        # Check the expected properties against the actually returned objects.
        # This discovers missing properties.
        for pname, exp_value in exp_stovol_properties.items():
            assert pname in act_stovol_properties, (
                f"Missing property {pname!r} in returned "
                f"storage volume {stovol_name!r} "
                f"in storage group {stogroup_name!r}:\n"
                f"Expected properties: {exp_stovol_pnames}\n"
                f"Actual properties: {act_stovol_pnames}")
            act_value = act_stovol_properties[pname]
            assert act_value == exp_value, (
                f"Incorrect value for property {pname!r} of returned "
                f"storage volume {stovol_name!r} "
                f"in storage group {stogroup_name!r}:\n"
                f"Expected value: {exp_value!r}\n"
                f"Actual value: {act_value!r}")


@pytest.mark.parametrize(
    "property_flags", [
        pytest.param({}, id="property_flags()"),
        pytest.param({'additional_properties': ['uuid']},
                     id="property_flags(additional_properties=[uuid])"),
        pytest.param({'full_properties': True},
                     id="property_flags(full_properties=True)"),
    ]
)
@pytest.mark.parametrize(
    "filter_args", [
        pytest.param({'use_name_filter': True},
                     id="filter_args(use_name_filter=True)"),
        pytest.param({'fulfillment_state': 'complete'},
                     id="filter_args(fulfillment_state=complete)"),
        pytest.param({'maximum_size': 500},
                     id="filter_args(maximum_size=500)"),
        pytest.param({'minimum_size': 10},
                     id="filter_args(minimum_size=10)"),
        pytest.param({'usage': 'boot'},
                     id="filter_args(usage=boot)"),
    ]
)
@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_storage_volume_list.AnsibleModule",
            autospec=True)
def test_zhmc_storage_volume_list(
        ansible_mod_cls, check_mode, filter_args, property_flags,
        hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_storage_volume_list module.
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
    fulfillment_state = filter_args.get('fulfillment_state', None)
    maximum_size = filter_args.get('maximum_size', None)
    minimum_size = filter_args.get('minimum_size', None)
    usage = filter_args.get('usage', None)
    use_name_filter = filter_args.get('use_name_filter', False)

    # The testcases require that the CPC associated with the storage group
    # is available. Skip this test if there is no available DPM mode CPC.
    cpcs = available_dpm_cpcs(client.cpcs.list())
    if not cpcs:
        pytest.skip("No available DPM mode CPCs")

    cpc_by_uri = {cpc.uri: cpc for cpc in cpcs}

    # Pick a random storage group as a target for the test
    all_storage_groups = console.storage_groups.list()
    if len(all_storage_groups) == 0:
        pytest.skip("This HMC has no storage groups")
    picked_storage_group = random.choice(all_storage_groups)
    picked_cpc_uri = picked_storage_group.get_property('cpc-uri')
    picked_cpc = cpc_by_uri[picked_cpc_uri]

    # Pick a random storage volume for the volume name filtering
    if use_name_filter:
        all_storage_volumes = picked_storage_group.storage_volumes.list()
        if len(all_storage_volumes) == 0 and use_name_filter:
            pytest.skip(f"Storage group {picked_storage_group.name} picked "
                        "for the test has no volumes")
        picked_storage_volume = random.choice(all_storage_volumes)
        picked_storage_volume_name = picked_storage_volume.name
    else:
        picked_storage_volume_name = None

    # Determine the expected list of storage volumes
    filter_args = {}
    if use_name_filter:
        filter_args['name'] = picked_storage_volume_name
    if fulfillment_state:
        filter_args['fulfillment-state'] = fulfillment_state
    if maximum_size:
        filter_args['maximum-size'] = maximum_size
    if minimum_size:
        filter_args['minimum-size'] = minimum_size
    if usage:
        filter_args['usage'] = usage
    exp_storage_volumes = picked_storage_group.storage_volumes.list(
        filter_args=filter_args,
        additional_properties=additional_properties,
        full_properties=full_properties)
    exp_storage_volume_dict = {}
    for stovol in exp_storage_volumes:
        exp_storage_volume_dict[stovol.name] = dict(stovol.properties)

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'cpc_name': picked_cpc.name,
        'storage_group_name': picked_storage_group.name,
        'name': picked_storage_volume_name,
        'fulfillment_state': fulfillment_state,
        'maximum_size': maximum_size,
        'minimum_size': minimum_size,
        'usage': usage,
        'additional_properties': additional_properties,
        'full_properties': full_properties,
        'log_file': LOG_FILE,
        '_faked_session': faked_session,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_storage_volume_list.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, \
        f"Module failed with exit code {exit_code} and message:\n" \
        f"{get_failure_msg(mod_obj)}"

    # Assert module output
    changed, storage_volume_list = get_module_output(mod_obj)
    assert changed is False

    assert_storage_volume_list(
        storage_volume_list, exp_storage_volume_dict,
        picked_storage_group.name)
