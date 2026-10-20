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
End2end tests for zhmc_lpar_list module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest import mock
import pytest
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
from zhmcclient.testutils import classic_mode_cpcs  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_lpar_list
from .utils import mock_ansible_module, get_failure_msg, get_hmc_auth, \
    underscored_properties
from .conftest import LOG_FILE


# Names of LPAR properties (with underscores) that are volatile, i.e. that may
# change their values on subsequent retrievals even when no other change is
# performed.
VOLATILE_LPAR_PROPERTIES = [
    'program_status_word_information',
    'has_operating_system_messages',
    'has_important_unviewed_operating_system_messages',
    'current_processing_weight',
    'current_aap_processing_weight',
    'current_ifl_processing_weight',
    'current_ziip_processing_weight',
    'current_cf_processing_weight',
    'power_wattage',
]


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, lpars)
    (i.e. the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, lpars):
        return changed, lpars

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_lpar_list(act_lpar_list, exp_lpar_dict):
    """
    Assert the output of the zhmc_lpar_list module.

    Parameters:

      act_lpar_list (list of dict): Actual result of the module,
        as a list of properties (name: value), including any artificial
        properties. The property names must be as returned by the module.

      exp_lpar_dict (dict of dict): Expected properties,
        as a dict (key: properties) where key is a tuple(CPC name, LPAR name)
        and properties is a dict (name: value), including any artificial
        properties. The property names must be as returned by the zhmcclient
        list method (i.e. with hyphens).
    """
    assert isinstance(act_lpar_list, list)
    assert isinstance(exp_lpar_dict, dict)

    assert len(act_lpar_list) == len(exp_lpar_dict), (
        "Unexpected number of LPARs:\n"
        f"Actual objects: {act_lpar_list!r}\n"
        f"Expected objects: {exp_lpar_dict!r}\n"
    )
    for act_lpar_properties in act_lpar_list:
        assert isinstance(act_lpar_properties, dict)

        # Check for the key properties
        assert 'cpc_name' in act_lpar_properties, (
            "Returned LPAR does not have a 'cpc_name' "
            f"property: {act_lpar_properties!r}")
        cpc_name = act_lpar_properties['cpc_name']
        assert 'name' in act_lpar_properties, (
            "Returned LPAR does not have a 'name' "
            f"property: {act_lpar_properties!r}")
        lpar_name = act_lpar_properties['name']
        lpar_key = (cpc_name, lpar_name)

        assert lpar_key in exp_lpar_dict, (
            f"Unexpected returned LPAR {lpar_key!r}")

        exp_lpar_properties = exp_lpar_dict[lpar_key]
        assert isinstance(exp_lpar_properties, dict)
        exp_lpar_properties = underscored_properties(exp_lpar_properties)

        exp_lpar_pnames = list(exp_lpar_properties.keys())
        act_lpar_pnames = list(act_lpar_properties.keys())

        # Check the actually returned objects against the expected properties.
        # This discovers unexpected properties.
        for pname, act_value in act_lpar_properties.items():
            assert '-' not in pname, (
                f"Property {pname!r} in returned "
                f"LPAR {lpar_key!r} "
                "has hyphens in the property name")
            assert pname in exp_lpar_properties, (
                f"Unexpected property {pname!r} in returned "
                f"LPAR {lpar_key!r}:\n"
                f"Expected properties: {exp_lpar_pnames}\n"
                f"Actual properties: {act_lpar_pnames}")
            if pname not in VOLATILE_LPAR_PROPERTIES:
                exp_value = exp_lpar_properties[pname]
                assert act_value == exp_value, (
                    f"Incorrect value for property {pname!r} of returned "
                    f"LPAR {lpar_key!r}:\n"
                    f"Expected value: {exp_value!r}\n"
                    f"Actual value: {act_value!r}")

        # Check the expected properties against the actually returned objects.
        # This discovers missing properties.
        for pname, exp_value in exp_lpar_properties.items():
            assert pname in act_lpar_properties, (
                f"Missing property {pname!r} in returned "
                f"LPAR {lpar_key!r}:\n"
                f"Expected properties: {exp_lpar_pnames}\n"
                f"Actual properties: {act_lpar_pnames}")
            if pname not in VOLATILE_LPAR_PROPERTIES:
                act_value = act_lpar_properties[pname]
                assert act_value == exp_value, (
                    f"Incorrect value for property {pname!r} of returned "
                    f"LPAR {lpar_key!r}:\n"
                    f"Expected value: {exp_value!r}\n"
                    f"Actual value: {act_value!r}")


@pytest.mark.parametrize(
    "with_cpc", [
        pytest.param(False, id="with_cpc=False"),
        pytest.param(True, id="with_cpc=True"),
    ]
)
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
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_lpar_list.AnsibleModule", autospec=True)
def test_zhmc_lpar_list(
        ansible_mod_cls, check_mode, property_flags, with_cpc,
        test_logger, classic_mode_cpcs):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_lpar_list module with classic mode CPCs.
    """
    if not classic_mode_cpcs:
        pytest.skip("HMC definition does not include any CPCs in classic mode")

    test_logger.debug(
        "Test parameters: check_mode=%r, property_flags=%r, with_cpc=%r",
        check_mode, property_flags, with_cpc)

    for cpc in classic_mode_cpcs:
        assert not cpc.dpm_enabled

        test_logger.debug("Testing with CPC %s", cpc.name)

        session = cpc.manager.session

        hmc_host = session.host
        hmc_auth = get_hmc_auth(session)
        hd = session.hmc_definition
        faked_session = session if hd.mock_file else None

        client = zhmcclient.Client(session)
        console = client.consoles.console

        # Get the module arguments for the test.
        # We need to use the defaults defined in the module argument spec
        additional_properties = property_flags.get('additional_properties', [])
        full_properties = property_flags.get('full_properties', False)

        # Determine the expected LPARs on the HMC
        hmc_version = client.query_api_version()['hmc-version']
        hmc_version_info = [int(x) for x in hmc_version.split('.')]
        if hmc_version_info < [2, 14, 0]:
            # Use the "List Logical Partitions of a CPC" operation.
            if with_cpc:
                exp_lpars = cpc.lpars.list(
                    additional_properties=additional_properties,
                    full_properties=full_properties)
            else:
                cpcs_ = client.cpcs.list()
                exp_lpars = []
                for cpc_ in cpcs_:
                    lpars_ = cpc_.lpars.list(
                        additional_properties=additional_properties,
                        full_properties=full_properties)
                    exp_lpars.extend(lpars_)
        else:
            # Use the "List Permitted Logical Partitions" operation.
            if with_cpc:
                filter_args = {'cpc-name': cpc.name}
            else:
                filter_args = None
            exp_lpars = console.list_permitted_lpars(
                filter_args=filter_args,
                additional_properties=additional_properties,
                full_properties=full_properties)

        # Prepare the expected data for comparison
        exp_lpar_dict = {}
        se_versions = {}  # Cache the SE versions (key: CPC name)
        for lpar in exp_lpars:
            cpc_ = lpar.manager.parent
            try:
                se_version = se_versions[cpc_.name]
            except KeyError:
                try:
                    se_version = lpar.properties['se-version']
                except KeyError:
                    se_version = cpc_.get_property('se-version')
                se_versions[cpc_.name] = se_version
            exp_properties = {
                'cpc_name': cpc_.name,
                'cpc_uri': cpc_.uri,
                'se_version': se_version,
            }
            exp_properties.update(lpar.properties)
            exp_lpar_key = (cpc_.name, lpar.name)
            exp_lpar_dict[exp_lpar_key] = exp_properties

        # Prepare module input parameters (must be all required + optional)
        params = {
            'hmc_host': hmc_host,
            'hmc_auth': hmc_auth,
            'cpc_name': cpc.name if with_cpc else None,
            'additional_properties': additional_properties,
            'full_properties': full_properties,
            'log_file': LOG_FILE,
            '_faked_session': faked_session,
        }

        # Prepare mocks for AnsibleModule object
        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        # Exercise the code to be tested
        with pytest.raises(SystemExit) as exc_info:
            zhmc_lpar_list.main()
        exit_code = exc_info.value.args[0]

        # Assert module exit code
        assert exit_code == 0, \
            f"Module failed with exit code {exit_code} and message:\n" \
            f"{get_failure_msg(mod_obj)}"

        # Assert module output
        changed, lpar_list = get_module_output(mod_obj)
        assert changed is False

        assert_lpar_list(lpar_list, exp_lpar_dict)
