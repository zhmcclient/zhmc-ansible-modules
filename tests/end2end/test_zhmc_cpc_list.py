# Copyright 2022 IBM Corp. All Rights Reserved.
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
End2end tests for zhmc_cpc_list module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest import mock
import pytest
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_cpc_list
from .utils import mock_ansible_module, get_failure_msg, get_hmc_auth, \
    unavailable_cpcs, underscored_properties
from .conftest import LOG_FILE


# Names of CPC properties (with underscores) that are volatile, i.e. that may
# change their values on subsequent retrievals even when no other change is
# performed.
# Note 1: This property should not be volatile according to its description,
#         but it has been observed to be volatile.
# Note 2: This property should not be volatile according to its description,
#         but its 'last-update' MCL structure field has been observed to be
#         volatile on 2.14 HMCs.
VOLATILE_CPC_PROPERTIES = [
    'cpc_power_consumption',
    'cpc_power_infrastructure',
    'cpc_power_total_partition',
    'cpc_power_unassigned',
    'zcpc_power_consumption',
    'zcpc_ambient_temperature',
    'zcpc_exhaust_temperature',
    'zcpc_humidity',
    'zcpc_dew_point',
    'zcpc_heat_load',
    'zcpc_heat_load_forced_air',
    'zcpc_heat_load_water',
    'last_energy_advice_time',
    'zcpc_minimum_inlet_air_temperature',  # Note 1
    'ec_mcl_description',  # Note 2
]


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, cpcs)
    (i.e. the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, cpcs):
        return changed, cpcs

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_cpc_list(act_cpc_list, exp_cpc_dict):
    """
    Assert the output of the zhmc_cpc_list module.

    Parameters:

      act_cpc_list (list of dict): Actual result of the module,
        as a list of properties (name: value), including any artificial
        properties. The property names must be as returned by the module.

      exp_cpc_dict (dict of dict): Expected properties,
        as a dict (key: properties) where key is the object name and properties
        is a dict (name: value), including any artificial properties. The
        property names must be as returned by the zhmcclient list method.
        (i.e. with hyphens).
    """
    assert isinstance(act_cpc_list, list)
    assert isinstance(exp_cpc_dict, dict)

    assert len(act_cpc_list) == len(exp_cpc_dict), (
        "Unexpected number of CPCs:\n"
        f"Actual objects: {act_cpc_list!r}\n"
        f"Expected objects: {exp_cpc_dict!r}\n"
    )
    for act_cpc_properties in act_cpc_list:
        assert isinstance(act_cpc_properties, dict)

        # Check for the key property
        assert 'name' in act_cpc_properties, (
            "Returned CPC does not have a 'name' "
            f"property: {act_cpc_properties!r}")
        cpc_name = act_cpc_properties['name']
        assert cpc_name in exp_cpc_dict, (
            f"Unexpected returned CPC {cpc_name!r}")

        exp_cpc_properties = exp_cpc_dict[cpc_name]
        assert isinstance(exp_cpc_properties, dict)
        exp_cpc_properties = underscored_properties(exp_cpc_properties)

        exp_cpc_pnames = list(exp_cpc_properties.keys())
        act_cpc_pnames = list(act_cpc_properties.keys())

        # Check the actually returned objects against the expected properties.
        # This discovers unexpected properties.
        for pname, act_value in act_cpc_properties.items():
            assert '-' not in pname, (
                f"Property {pname!r} in returned "
                f"CPC {cpc_name!r} "
                "has hyphens in the property name")
            assert pname in exp_cpc_properties, (
                f"Unexpected property {pname!r} in returned "
                f"CPC {cpc_name!r}:\n"
                f"Expected properties: {exp_cpc_pnames}\n"
                f"Actual properties: {act_cpc_pnames}")
            if pname not in VOLATILE_CPC_PROPERTIES:
                exp_value = exp_cpc_properties[pname]
                assert act_value == exp_value, (
                    f"Incorrect value for property {pname!r} of returned "
                    f"CPC {cpc_name!r}:\n"
                    f"Expected value: {exp_value!r}\n"
                    f"Actual value: {act_value!r}")

        # Check the expected properties against the actually returned objects.
        # This discovers missing properties.
        for pname, exp_value in exp_cpc_properties.items():
            assert pname in act_cpc_properties, (
                f"Missing property {pname!r} in returned "
                f"CPC {cpc_name!r}:\n"
                f"Expected properties: {exp_cpc_pnames}\n"
                f"Actual properties: {act_cpc_pnames}")
            if pname not in VOLATILE_CPC_PROPERTIES:
                act_value = act_cpc_properties[pname]
                assert act_value == exp_value, (
                    f"Incorrect value for property {pname!r} of returned "
                    f"CPC {cpc_name!r}:\n"
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
    "include_unmanaged_cpcs", [
        pytest.param(False, id="include_unmanaged_cpcs=False"),
        pytest.param(True, id="include_unmanaged_cpcs=True"),
        pytest.param(None, id="include_unmanaged_cpcs=None"),
    ]
)
@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_cpc_list.AnsibleModule", autospec=True)
def test_zhmc_cpc_list(
        ansible_mod_cls, check_mode, include_unmanaged_cpcs, property_flags,
        hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_cpc_list module with managed and unmanaged CPCs.
    """

    hmc_host = hmc_session.host
    hmc_auth = get_hmc_auth(hmc_session)
    hd = hmc_session.hmc_definition
    faked_session = hmc_session if hd.mock_file else None

    client = zhmcclient.Client(hmc_session)

    # Get the module arguments for the test.
    # We need to use the defaults defined in the module argument spec
    additional_properties = property_flags.get('additional_properties', [])
    full_properties = property_flags.get('full_properties', False)

    # The testcases with full_properties=True require that all managed CPCs
    # are available. Skip this test if that is not the case.
    if full_properties:
        unavail_cpcs = unavailable_cpcs(client.cpcs.list())
        if unavail_cpcs:
            unavail_cpcs_str = ", ".join([cpc.name for cpc in unavail_cpcs])
            pytest.skip(f"Some CPCs are unavailable: {unavail_cpcs_str}")

    # Determine the expected CPCs on the HMC
    exp_cpcs = client.cpcs.list(
        additional_properties=additional_properties,
        full_properties=full_properties)

    # Prepare the expected data for comparison
    exp_cpc_dict = {}
    for cpc in exp_cpcs:
        exp_properties = {
            "is_managed": True,
        }
        exp_properties.update(cpc.properties)
        exp_cpc_dict[cpc.name] = exp_properties
    if include_unmanaged_cpcs:
        exp_um_cpcs = client.consoles.console.list_unmanaged_cpcs()
        for cpc in exp_um_cpcs:
            exp_properties = {
                "is_managed": False,
            }
            exp_properties.update(cpc.properties)
            exp_cpc_dict[cpc.name] = exp_properties

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'include_unmanaged_cpcs': include_unmanaged_cpcs,
        'additional_properties': additional_properties,
        'full_properties': full_properties,
        'log_file': LOG_FILE,
        '_faked_session': faked_session,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_cpc_list.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, \
        f"Module failed with exit code {exit_code} and message:\n" \
        f"{get_failure_msg(mod_obj)}"

    # Assert module output
    changed, cpc_list = get_module_output(mod_obj)
    assert changed is False

    assert_cpc_list(cpc_list, exp_cpc_dict)
