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
End2end tests for zhmc_password_rule_list module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest import mock
import pytest
import urllib3
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_password_rule_list
from .utils import mock_ansible_module, get_failure_msg

urllib3.disable_warnings()

# Print debug messages
DEBUG = False

LOG_FILE = 'zhmc_password_rule_list.log' if DEBUG else None


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, user_properties) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, password_rules):
        return changed, password_rules

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_pwrule_list(pwrule_list, exp_pwrule_dict):
    """
    Assert the output of the zhmc_password_rule_list module.

    Parameters:

      pwrule_list(list): Result of zhmc_password_rule_list module, as a list of
        dicts of password rule properties as documented (with underscores in
        their names).

      exp_pwrule_dict(dict): Expected password rules with their properties.
        Key: password rule name.
        Value: Dict of expected password rule properties (including any
        artificial properties, all with underscores in their names).
    """

    assert isinstance(pwrule_list, list)

    exp_pwrule_names = list(exp_pwrule_dict.keys())
    pwrule_names = [ri.get('name', None) for ri in pwrule_list]
    assert set(pwrule_names) == set(exp_pwrule_names)

    for pwrule_item in pwrule_list:
        pwrule_name = pwrule_item.get('name', None)

        assert pwrule_name is not None, \
            f"Returned password rule {pwrule_item!r} does not have a 'name' " \
            "property"

        assert pwrule_name in exp_pwrule_dict, \
            f"Result contains unexpected password rule {pwrule_name!r}"

        exp_pwrule_properties = exp_pwrule_dict[pwrule_name]
        for pname, pvalue in pwrule_item.items():
            assert '-' not in pname, \
                f"Property {pname!r} in password rule {pwrule_name!r} is " \
                "returned with hyphens in the property name"
            assert pname in exp_pwrule_properties, \
                f"Unexpected property {pname!r} in password rule " \
                f"{pwrule_name!r}"
            exp_value = exp_pwrule_properties[pname]
            assert pvalue == exp_value, \
                f"Incorrect value for property {pname!r} of password rule " \
                f"{pwrule_name!r}"


@pytest.mark.parametrize(
    "property_flags", [
        pytest.param({}, id="property_flags()"),
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
@mock.patch("plugins.modules.zhmc_password_rule_list.AnsibleModule",
            autospec=True)
def test_zhmc_password_rule_list(
        ansible_mod_cls, check_mode, property_flags,
        hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_password_rule_list module.
    """

    hd = hmc_session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    client = zhmcclient.Client(hmc_session)
    console = client.consoles.console

    faked_session = hmc_session if hd.mock_file else None

    full_properties = property_flags.get('full_properties', False)

    # Determine the expected list of password rules.
    exp_pwrules = console.password_rules.list(full_properties=full_properties)
    exp_pwrule_dict = {}
    for pwrule in exp_pwrules:
        exp_properties = {}
        for pname_hmc, pvalue in pwrule.properties.items():
            pname = pname_hmc.replace('-', '_')
            exp_properties[pname] = pvalue
        exp_pwrule_dict[pwrule.name] = exp_properties

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'full_properties': full_properties,
        'log_file': LOG_FILE,
        '_faked_session': faked_session,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_password_rule_list.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, \
        f"Module failed with exit code {exit_code} and message:\n" \
        f"{get_failure_msg(mod_obj)}"

    # Assert module output
    changed, pwrule_list = get_module_output(mod_obj)
    assert changed is False

    assert_pwrule_list(pwrule_list, exp_pwrule_dict)
