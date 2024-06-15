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

import pytest
from unittest import mock
import requests.packages.urllib3
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_cpc_list
from .utils import mock_ansible_module, get_failure_msg

requests.packages.urllib3.disable_warnings()

# Print debug messages
DEBUG = False

LOG_FILE = 'zhmc_cpc_list.log' if DEBUG else None

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
    Return the module output as a tuple (changed, user_properties) (i.e.
    the arguments of the call to exit_json()).
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


def assert_cpc_list(
        cpc_list, include_unmanaged_cpcs, exp_cpc_dict, exp_um_cpc_dict):
    """
    Assert the output of the zhmc_cpc_list module.

    Parameters:

      cpc_list(list): Result of zhmc_cpc_list module, as a list of dicts of CPC
        properties as documented (with underscores in their names).

      include_unmanaged_cpcs(bool): Include unmanaged CPCs.

      exp_cpc_dict(dict): Expected managed CPCs with their properties.
        Key: CPC name.
        Value: Dict of expected CPC properties (including any artificial
        properties, all with underscores in their names).

      exp_um_cpc_dict(dict): Expected unmanaged CPCs with their properties.
        Key: CPC name.
        Value: Dict of expected CPC properties (including any artificial
        properties, all with underscores in their names).
    """

    assert isinstance(cpc_list, list)

    exp_len = len(exp_cpc_dict)
    if include_unmanaged_cpcs:
        exp_len += len(exp_um_cpc_dict)
    assert len(cpc_list) == exp_len

    for cpc_item in cpc_list:

        assert 'name' in cpc_item, \
            f"Returned CPC {cpc_item!r} does not have a 'name' property"
        cpc_name = cpc_item['name']

        assert 'is_managed' in cpc_item, \
            f"Returned CPC {cpc_item!r} does not have a 'is_managed' property"
        is_managed = cpc_item['is_managed']

        if is_managed:
            assert cpc_name in exp_cpc_dict, \
                f"Result contains unexpected managed CPC: {cpc_name!r}"

            exp_cpc_properties = exp_cpc_dict[cpc_name]
            for pname, pvalue in cpc_item.items():

                assert '-' not in pname, \
                    f"Property {pname!r} in CPC {cpc_name!r} is returned " \
                    "with hyphens in the property name"

                # Handle artificial properties
                if pname == 'is_managed':
                    continue

                # Verify normal properties
                assert pname in exp_cpc_properties, \
                    f"Unexpected property {pname!r} in CPC {cpc_name!r}"

                if pname not in VOLATILE_CPC_PROPERTIES:
                    exp_value = exp_cpc_properties[pname]
                    assert pvalue == exp_value, \
                        f"Incorrect value for property {pname!r} of CPC " \
                        f"{cpc_name!r}"

        else:
            assert cpc_name in exp_um_cpc_dict, \
                f"Result contains unexpected unmanaged CPC: {cpc_name!r}"


@pytest.mark.parametrize(
    "property_flags", [
        pytest.param({}, id="property_flags()"),
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
    """
    Test the zhmc_cpc_list module with managed and unmanaged CPCs.
    """

    hd = hmc_session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    client = zhmcclient.Client(hmc_session)

    faked_session = hmc_session if hd.mock_file else None

    full_properties = property_flags.get('full_properties', False)

    # Determine the expected managed CPCs on the HMC
    exp_cpcs = client.cpcs.list(full_properties=full_properties)
    exp_cpc_dict = {}
    for cpc in exp_cpcs:
        exp_properties = {}
        for pname_hmc, pvalue in cpc.properties.items():
            pname = pname_hmc.replace('-', '_')
            exp_properties[pname] = pvalue
        exp_cpc_dict[cpc.name] = exp_properties

    # Determine the expected unmanaged CPCs on the HMC
    exp_um_cpcs = client.consoles.console.list_unmanaged_cpcs()
    exp_um_cpc_dict = {}
    for cpc in exp_um_cpcs:
        exp_properties = {}
        for pname_hmc, pvalue in cpc.properties.items():
            pname = pname_hmc.replace('-', '_')
            exp_properties[pname] = pvalue
        exp_um_cpc_dict[cpc.name] = exp_properties

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'include_unmanaged_cpcs': include_unmanaged_cpcs,
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

    assert_cpc_list(
        cpc_list, include_unmanaged_cpcs, exp_cpc_dict, exp_um_cpc_dict)
