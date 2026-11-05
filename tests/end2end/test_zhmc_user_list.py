# Copyright 2023 IBM Corp. All Rights Reserved.
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
End2end tests for zhmc_user_list module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest import mock
import pytest
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_user_list
from .utils import mock_ansible_module, get_failure_msg, get_hmc_auth, \
    underscored_properties
from .conftest import LOG_FILE


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, users)
    (i.e. the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, users):
        return changed, users

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_user_list(act_user_list, exp_user_dict):
    """
    Assert the output of the zhmc_user_list module.

    Parameters:

      act_user_list (list of dict): Actual result of the module,
        as a list of properties (name: value), including any artificial
        properties. The property names must be as returned by the module.

      exp_user_dict (dict of dict): Expected properties,
        as a dict (key: properties) where key is the object name and properties
        is a dict (name: value), including any artificial properties. The
        property names must be as returned by the zhmcclient list method.
        (i.e. with hyphens).
    """
    assert isinstance(act_user_list, list)
    assert isinstance(exp_user_dict, dict)

    assert len(act_user_list) == len(exp_user_dict), (
        "Unexpected number of users:\n"
        f"Actual objects: {act_user_list!r}\n"
        f"Expected objects: {exp_user_dict!r}\n"
    )
    for act_user_properties in act_user_list:
        assert isinstance(act_user_properties, dict)

        # Check for the key property
        assert 'name' in act_user_properties, (
            "Returned user does not have a 'name' "
            f"property: {act_user_properties!r}")
        user_name = act_user_properties['name']
        assert user_name in exp_user_dict, (
            f"Unexpected returned user {user_name!r}")

        user_type = act_user_properties.get('type', None)

        exp_user_properties = exp_user_dict[user_name]
        assert isinstance(exp_user_properties, dict)
        exp_user_properties = underscored_properties(exp_user_properties)

        exp_user_pnames = list(exp_user_properties.keys())
        act_user_pnames = list(act_user_properties.keys())

        # Check the actually returned objects against the expected properties.
        # This discovers unexpected properties.
        # Note that the underlying zhmcclient list method implements
        # additional_properties by returning all properties. However, the check
        # for unexpected properties still works because both the Ansible module
        # under test and the test function use the same zhmcclient list method.
        for pname, act_value in act_user_properties.items():
            assert '-' not in pname, (
                f"Property {pname!r} in returned "
                f"user {user_name!r} "
                "has hyphens in the property name")
            assert pname in exp_user_properties, (
                f"Unexpected property {pname!r} in returned "
                f"user {user_name!r}:\n"
                f"Expected properties: {exp_user_pnames}\n"
                f"Actual properties: {act_user_pnames}")
            if user_type == 'pattern-based' and \
                    pname in ('object_uri', 'object_id'):
                # Pattern-based users are re-created upon every login
                # and each such user has a different object ID.
                continue
            exp_value = exp_user_properties[pname]
            assert act_value == exp_value, (
                f"Incorrect value for property {pname!r} of returned "
                f"user {user_name!r}:\n"
                f"Expected value: {exp_value!r}\n"
                f"Actual value: {act_value!r}")

        # Check the expected properties against the actually returned objects.
        # This discovers missing properties.
        for pname, exp_value in exp_user_properties.items():
            assert pname in act_user_properties, (
                f"Missing property {pname!r} in returned "
                f"user {user_name!r}:\n"
                f"Expected properties: {exp_user_pnames}\n"
                f"Actual properties: {act_user_pnames}")
            if user_type == 'pattern-based' and \
                    pname in ('object_uri', 'object_id'):
                # Pattern-based users are re-created upon every login
                # and each such user has a different object ID.
                continue
            act_value = act_user_properties[pname]
            assert act_value == exp_value, (
                f"Incorrect value for property {pname!r} of returned "
                f"user {user_name!r}:\n"
                f"Expected value: {exp_value!r}\n"
                f"Actual value: {act_value!r}")


def add_artificial_properties(user_properties, console, user):
    """
    Add artificial properties to the user_properties dict.

    This is a straight forward implementation to make sure the test functions
    remain simple.
    """

    # Handle User Role references
    all_uroles_by_uri = {ur.uri: ur for ur in console.user_roles.list()}
    uroles = [all_uroles_by_uri[uri] for uri in user.properties['user-roles']]
    user_properties['user-role-names'] = [ur.name for ur in uroles]

    # Handle User Pattern reference
    if user.properties['type'] == 'pattern-based':

        # This property exists only for type='pattern-based', and will not be
        # None.
        user_pattern_uri = user.properties['user-pattern-uri']
        if user_pattern_uri is None:  # Defensive programming
            user_properties['user-pattern-name'] = None
        else:
            user_pattern = \
                console.user_patterns.resource_object(user_pattern_uri)
            user_properties['user-pattern-name'] = user_pattern.name

        # This property exists only for type='pattern-based' and if the user
        # is template-based, and may be None.
        user_template_uri = user.properties['user-template-uri']
        if user_template_uri is None:
            user_properties['user-template-name'] = None
        else:
            user_template = console.users.resource_object(user_template_uri)
            user_properties['user-template-name'] = user_template.name

    # Handle Password Rule reference
    password_rule_uri = user.properties['password-rule-uri']
    # This property always exists. It will be non-Null for auth-type='local'.
    if password_rule_uri is None:
        user_properties['password-rule-name'] = None
    else:
        password_rule = console.password_rules.resource_object(
            password_rule_uri)
        user_properties['password-rule-name'] = password_rule.name

    # Handle LDAP Server Definition reference
    ldap_srv_def_uri = user.properties['ldap-server-definition-uri']
    # This property always exists and is non-Null for auth.-type='ldap'.
    if ldap_srv_def_uri is None:
        user_properties['ldap-server-definition-name'] = None
    else:
        ldap_srv_def = console.ldap_server_definitions.resource_object(
            ldap_srv_def_uri)
        user_properties['ldap-server-definition-name'] = ldap_srv_def.name

    # Handle primary MFA Server Definition reference
    pri_mfa_srv_def_uri = user.properties['primary-mfa-server-definition-uri']
    # This property always exists and is non-Null for auth.-type='mfa'.
    if pri_mfa_srv_def_uri is None:
        user_properties['primary-mfa-server-definition-name'] = None
    else:
        pri_mfa_srv_def = console.mfa_server_definitions.resource_object(
            pri_mfa_srv_def_uri)
        user_properties['primary-mfa-server-definition-name'] = \
            pri_mfa_srv_def.name

    # Handle backup MFA Server Definition reference
    bac_mfa_srv_def_uri = user.properties['backup-mfa-server-definition-uri']
    # This property always exists and is non-Null for auth.-type='mfa'.
    if bac_mfa_srv_def_uri is None:
        user_properties['backup-mfa-server-definition-name'] = None
    else:
        bac_mfa_srv_def = console.mfa_server_definitions.resource_object(
            bac_mfa_srv_def_uri)
        user_properties['backup-mfa-server-definition-name'] = \
            bac_mfa_srv_def.name

    # Handle default Group reference
    default_group_uri = user.properties['default-group-uri']
    # This property always exists, and may be None
    if default_group_uri is None:
        user_properties['default-group-name'] = None
    else:
        default_group = console.users.resource_object(default_group_uri)
        user_properties['default-group-name'] = default_group.name


@pytest.mark.parametrize(
    "property_flags", [
        pytest.param({}, id="property_flags()"),
        pytest.param({'expand_names': True},
                     id="expand_names=True)"),
        pytest.param({'additional_properties': ['description']},
                     id="property_flags(additional_properties=[description])"),
        pytest.param({'additional_properties': ['description'],
                      'expand_names': True},
                     id="property_flags(additional_properties=[description],"
                     "expand_names=True)"),
        pytest.param({'full_properties': True},
                     id="property_flags(full_properties=True)"),
        pytest.param({'full_properties': True, 'expand_names': True},
                     id="property_flags(full_properties=True,"
                     "expand_names=True)"),
    ]
)
@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_user_list.AnsibleModule",
            autospec=True)
def test_zhmc_user_list(
        ansible_mod_cls, check_mode, property_flags,
        hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_user_list module.
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
    expand_names = property_flags.get('expand_names', False)

    # Determine the expected list of users.
    exp_users = console.users.list(
        additional_properties=additional_properties,
        full_properties=full_properties)
    exp_user_dict = {}
    for user in exp_users:
        exp_properties = dict(user.properties)
        if full_properties and expand_names:
            add_artificial_properties(exp_properties, console, user)
        exp_user_dict[user.name] = exp_properties

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
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
        zhmc_user_list.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, \
        f"Module failed with exit code {exit_code} and message:\n" \
        f"{get_failure_msg(mod_obj)}"

    # Assert module output
    changed, user_list = get_module_output(mod_obj)
    assert changed is False

    assert_user_list(user_list, exp_user_dict)
