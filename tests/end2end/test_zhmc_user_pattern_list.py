# Copyright 2024 IBM Corp. All Rights Reserved.
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
End2end tests for zhmc_user_pattern_list module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest import mock
import pytest
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_user_pattern_list
from .utils import mock_ansible_module, get_failure_msg, get_hmc_auth, \
    underscored_properties
from .conftest import LOG_FILE


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, user_patterns)
    (i.e. the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, user_patterns):
        return changed, user_patterns

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_upattern_list(act_upattern_list, exp_upattern_dict):
    """
    Assert the output of the zhmc_user_pattern_list module.

    Parameters:

      act_upattern_list (list of dict): Actual result of the module,
        as a list of properties (name: value), including any artificial
        properties. The property names must be as returned by the module.

      exp_upattern_dict (dict of dict): Expected properties,
        as a dict (key: properties) where key is the object name and properties
        is a dict (name: value), including any artificial properties. The
        property names must be as returned by the zhmcclient list method.
        (i.e. with hyphens).
    """
    assert isinstance(act_upattern_list, list)
    assert isinstance(exp_upattern_dict, dict)

    assert len(act_upattern_list) == len(exp_upattern_dict), (
        "Unexpected number of user patterns:\n"
        f"Actual objects: {act_upattern_list!r}\n"
        f"Expected objects: {exp_upattern_dict!r}\n"
    )
    for act_upattern_properties in act_upattern_list:
        assert isinstance(act_upattern_properties, dict)

        # Check for the key property
        assert 'name' in act_upattern_properties, (
            "Returned user pattern does not have a 'name' "
            f"property: {act_upattern_properties!r}")
        upattern_name = act_upattern_properties['name']
        assert upattern_name in exp_upattern_dict, (
            f"Unexpected returned user pattern {upattern_name!r}")

        exp_upattern_properties = exp_upattern_dict[upattern_name]
        assert isinstance(exp_upattern_properties, dict)
        exp_upattern_properties = underscored_properties(exp_upattern_properties)

        exp_upattern_pnames = list(exp_upattern_properties.keys())
        act_upattern_pnames = list(act_upattern_properties.keys())

        # Check the actually returned objects against the expected properties.
        # This discovers unexpected properties.
        # Note that the underlying zhmcclient list method implements
        # additional_properties by returning all properties. However, the check
        # for unexpected properties still works because both the Ansible module
        # under test and the test function use the same zhmcclient list method.
        for pname, act_value in act_upattern_properties.items():
            assert '-' not in pname, (
                f"Property {pname!r} in returned "
                f"user pattern {upattern_name!r} "
                "has hyphens in the property name")
            assert pname in exp_upattern_properties, (
                f"Unexpected property {pname!r} in returned "
                f"user pattern {upattern_name!r}:\n"
                f"Expected properties: {exp_upattern_pnames}\n"
                f"Actual properties: {act_upattern_pnames}")
            exp_value = exp_upattern_properties[pname]
            assert act_value == exp_value, (
                f"Incorrect value for property {pname!r} of returned "
                f"user pattern {upattern_name!r}:\n"
                f"Expected value: {exp_value!r}\n"
                f"Actual value: {act_value!r}")

        # Check the expected properties against the actually returned objects.
        # This discovers missing properties.
        for pname, exp_value in exp_upattern_properties.items():
            assert pname in act_upattern_properties, (
                f"Missing property {pname!r} in returned "
                f"user pattern {upattern_name!r}:\n"
                f"Expected properties: {exp_upattern_pnames}\n"
                f"Actual properties: {act_upattern_pnames}")
            act_value = act_upattern_properties[pname]
            assert act_value == exp_value, (
                f"Incorrect value for property {pname!r} of returned "
                f"user pattern {upattern_name!r}:\n"
                f"Expected value: {exp_value!r}\n"
                f"Actual value: {act_value!r}")


@pytest.mark.parametrize(
    "property_flags", [
        pytest.param({}, id="property_flags()"),
        pytest.param({'additional_properties': ['uuid']},
                     id="property_args(additional_properties=[uuid])"),
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
@mock.patch("plugins.modules.zhmc_user_pattern_list.AnsibleModule",
            autospec=True)
def test_zhmc_user_pattern_list(
        ansible_mod_cls, check_mode, property_flags,
        hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_user_pattern_list module.
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

    # Determine the expected list of user patterns on the HMC.
    exp_upatterns = console.user_patterns.list(
        additional_properties=additional_properties,
        full_properties=full_properties)
    exp_upattern_dict = {}
    for upattern in exp_upatterns:
        exp_upattern_dict[upattern.name] = dict(upattern.properties)

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'additional_properties': additional_properties,
        'full_properties': full_properties,
        'log_file': LOG_FILE,
        '_faked_session': faked_session,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_user_pattern_list.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, \
        f"Module failed with exit code {exit_code} and message:\n" \
        f"{get_failure_msg(mod_obj)}"

    # Assert module output
    changed, upattern_list = get_module_output(mod_obj)
    assert changed is False

    assert_upattern_list(upattern_list, exp_upattern_dict)
