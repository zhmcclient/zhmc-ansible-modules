# Copyright 2019,2020 IBM Corp. All Rights Reserved.
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
End2end tests for zhmc_user module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import uuid
from unittest import mock
import random
from pprint import pformat
import pytest
import urllib3
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.module_utils.common import params_deepcopy
from plugins.modules import zhmc_user
from .utils import mock_ansible_module, get_failure_msg

urllib3.disable_warnings()

# Print debug messages
DEBUG = False

LOG_FILE = 'zhmc_user.log' if DEBUG else None

# Properties in the returned user facts that are not always present, but
# only under certain conditions. This includes artificial properties whose base
# properties are not always present, or that depend on expand being set. The
# comments state the condition under which the property is present.
USER_CONDITIONAL_PROPS = (
    'user-pattern-uri',  # type == 'pattern-based'
    'user-pattern-name',  # artificial: type == 'pattern-based'
    'user-pattern',  # artificial: type == 'pattern-based' and expand
    'user-template-uri',  # type == 'template'
    'user-template-name',  # artificial: type == 'template'
    'disabled',  # type != 'template'
    'password-rule-uri',  # auth-type == 'local'
    'password-rule-name',  # artificial: auth-type == 'local'
    'password-rule',  # artificial: auth-type == 'local' and expand
    'password-expires',  # artificial: auth-type == 'local', but this is not
    # stated in HMC WS-API book
    'password',  # never present
    'force-password-change',  # auth-type == 'local'
    'ldap-server-definition-uri',  # auth-type == 'ldap'
    'ldap-server-definition-name',  # artificial: auth-type == 'ldap'
    'ldap-server-definition',  # artificial: auth-type == 'ldap' and expand
    'userid-on-ldap-server',  # auth-type == 'ldap' and type != 'template'
    'min-pw-change-time',  # auth-type == 'local'
    'user-role-objects',  # artificial: expand
    'default-group',  # artificial: expand
    'default-group-name',  # artificial, not yet implemented (TODO: Implement)
    'force-shared-secret-key-change',  # multi-factor-auth-required == True
    'primary-mfa-server-definition-uri',  # mfa-types contains "mfa-server"
    'backup-mfa-server-definition-uri',  # mfa-types contains "mfa-server"
    'mfa-policy',  # mfa-types contains "mfa-server"
    'mfa-userid',  # type != "template" and mfa-types contains "mfa-server"
    'mfa-userid-override',  # type == "template" and mfa-types contains "mfa-server"
)

# A standard test user, as specified for the 'properties' module input parm
STD_USER_INPUT_PROPERTIES = {
    'type': 'standard',
    # 'name': provided in separate module input parameter
    # 'default_group_name': no default group (artificial property)
    'description': "zhmc test user",
    'disabled': False,
    'user_role_names': ['hmc-all-system-managed-objects'],  # (artificial prop)
    'authentication_type': 'local',
    'password_rule_name': 'Standard',  # (artificial property)
    # 'password' is added when needed (otherwise updating to the same password
    # causes HTTPError: 400,311: "The logon password does not conform to the
    # password rule in effect for the user"
    'force_password_change': True,
    # 'ldap_server_definition_name': no LDAP (artificial property)
    # 'userid_on_ldap_server': no LDAP
    'session_timeout': 0,
    'verify_timeout': 15,
    'idle_timeout': 0,
    'min_pw_change_time': 0,
    'max_failed_logins': 3,
    'disable_delay': 1,
    'inactivity_timeout': 0,
    'disruptive_pw_required': True,
    'disruptive_text_required': True,
    'allow_remote_access': False,
    'allow_management_interfaces': False,
    'max_web_services_api_sessions': 100,
    'web_services_api_session_idle_timeout': 360,
    'multi_factor_authentication_required': False,
    # 'force_shared_secret_key_change': no multi factor auth
    'email_address': None,
}

STD_USER_INPUT_PROPERTIES_WITH_PW = dict(STD_USER_INPUT_PROPERTIES)
STD_USER_INPUT_PROPERTIES_WITH_PW['password'] = "Bumerang9x"

# A standard test user consistent with STD_USER_INPUT_PROPERTIES, but
# specified with HMC properties.
STD_USER_PROPERTIES = {
    'type': STD_USER_INPUT_PROPERTIES['type'],
    # 'name': updated upon use
    # 'default-group-uri': no default group
    'description': STD_USER_INPUT_PROPERTIES['description'],
    'disabled': STD_USER_INPUT_PROPERTIES['disabled'],
    # 'user-roles': updated upon use
    'authentication-type': STD_USER_INPUT_PROPERTIES['authentication_type'],
    # 'password-rule-uri': updated upon use
    # 'password': is added when needed
    'force-password-change':
    STD_USER_INPUT_PROPERTIES['force_password_change'],
    # 'ldap-server-definition-uri': no LDAP
    # 'userid-on-ldap-server': no LDAP
    'session-timeout': STD_USER_INPUT_PROPERTIES['session_timeout'],
    'verify-timeout': STD_USER_INPUT_PROPERTIES['verify_timeout'],
    'idle-timeout': STD_USER_INPUT_PROPERTIES['idle_timeout'],
    'min-pw-change-time': STD_USER_INPUT_PROPERTIES['min_pw_change_time'],
    'max-failed-logins': STD_USER_INPUT_PROPERTIES['max_failed_logins'],
    'disable-delay': STD_USER_INPUT_PROPERTIES['disable_delay'],
    'inactivity-timeout': STD_USER_INPUT_PROPERTIES['inactivity_timeout'],
    'disruptive-pw-required':
    STD_USER_INPUT_PROPERTIES['disruptive_pw_required'],
    'disruptive-text-required':
    STD_USER_INPUT_PROPERTIES['disruptive_text_required'],
    'allow-remote-access':
    STD_USER_INPUT_PROPERTIES['allow_remote_access'],
    'allow-management-interfaces':
    STD_USER_INPUT_PROPERTIES['allow_management_interfaces'],
    'max-web-services-api-sessions':
    STD_USER_INPUT_PROPERTIES['max_web_services_api_sessions'],
    'web-services-api-session-idle-timeout':
    STD_USER_INPUT_PROPERTIES['web_services_api_session_idle_timeout'],
    'multi-factor-authentication-required':
    STD_USER_INPUT_PROPERTIES['multi_factor_authentication_required'],
    # 'force-shared-secret-key-change': no multi factor auth
    'email-address': STD_USER_INPUT_PROPERTIES['email_address'],
}

STD_USER_PROPERTIES_WITH_PW = dict(STD_USER_PROPERTIES)
STD_USER_PROPERTIES_WITH_PW['password'] = "Bumerang9x"


def new_user_name():
    """Return random unique user name"""
    user_name = f'test_{uuid.uuid4()}'
    return user_name


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, user_properties) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, user):
        return changed, user

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_user_props(user_props, expand, where):
    """
    Assert the output object of the zhmc_user module
    """
    assert isinstance(user_props, dict), where  # Dict of User properties

    # Assert presence of normal properties in the output
    for prop_name in zhmc_user.ZHMC_USER_PROPERTIES:
        prop_name_hmc = prop_name.replace('_', '-')
        if prop_name_hmc in USER_CONDITIONAL_PROPS:
            continue
        assert prop_name_hmc in user_props, where

    user_type = user_props['type']
    auth_type = user_props['authentication-type']

    # Assert presence of the conditional and artificial properties

    if user_type == 'pattern-based':
        assert 'user-pattern-uri' in user_props, where
        assert 'user-pattern-name' in user_props, where
        if expand:
            assert 'user-pattern' in user_props, where

    if auth_type == 'local':
        assert 'password-rule-uri' in user_props, where
        assert 'password-rule-name' in user_props, where
        if expand:
            assert 'password-rule' in user_props, where

    if auth_type == 'ldap':
        assert 'ldap-server-definition-uri' in user_props, where
        assert 'ldap-server-definition-name' in user_props, where
        if expand:
            assert 'ldap-server-definition' in user_props, where

    assert 'user-roles' in user_props, where  # Base property with the URIs
    assert 'user-role-names' in user_props, where
    if expand:
        assert 'user-role-objects' in user_props, where

    # Assert that none of the write-only properties is in the output object
    for prop_name in zhmc_user.WRITEONLY_PROPERTIES_HYPHEN:
        assert prop_name not in user_props, where


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@pytest.mark.parametrize(
    "expand", [
        pytest.param(False, id="expand=False"),
        pytest.param(True, id="expand=True"),
    ]
)
@pytest.mark.parametrize(
    "user_type, auth_type", [
        pytest.param('standard', 'local', id="user_type=standard,auth_type=local"),
        pytest.param('standard', 'ldap', id="user_type=standard,auth_type=ldap"),
        pytest.param('template', 'ldap', id="user_type=template,auth_type=ldap"),
        pytest.param('pattern-based', 'local', id="user_type=pattern-based,auth_type=local"),
        pytest.param('pattern-based', 'ldap', id="user_type=pattern-based,auth_type=ldap"),
        pytest.param('system-defined', 'local', id="user_type=system-defined,auth_type=local"),
    ]
)
@mock.patch("plugins.modules.zhmc_user.AnsibleModule", autospec=True)
def test_zhmc_user_facts(
        ansible_mod_cls, user_type, auth_type, expand, check_mode,
        hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_user module with state=facts.
    """

    hd = hmc_session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    client = zhmcclient.Client(hmc_session)
    console = client.consoles.console

    faked_session = hmc_session if hd.mock_file else None

    # Determine a random existing user of the desired type to test.
    users = console.users.list()
    typed_users = [u for u in users
                   if u.get_property('authentication-type') == auth_type
                   and u.get_property('type') == user_type]
    if len(typed_users) == 0:
        pytest.skip(f"HMC has no users with type '{user_type}' and "
                    f"authentication-type '{auth_type}'")
    user = random.choice(typed_users)

    where = f"user '{user.name}'"

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'name': user.name,
        'state': 'facts',
        'properties': None,
        'expand': expand,
        'log_file': LOG_FILE,
        '_faked_session': faked_session,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_user.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, \
        f"{where}: Module failed with exit code {exit_code} and message:\n" \
        f"{get_failure_msg(mod_obj)}"

    # Assert module output
    changed, user_props = get_module_output(mod_obj)
    assert changed is False, where
    assert_user_props(user_props, expand, where)


USER_ABSENT_PRESENT_TESTCASES = [
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - initial_user_props (dict): HMC-formatted properties for initial user,
    #   in addition to STD_USER_PROPERTIES, or None for no initial user.
    # - initial_related_names (dict): Names of related resources, using the
    #   artificial Ansible properties.
    # - input_props (dict): 'properties' input parameter for zhmc_user module.
    # - exp_user_props (dict): HMC-formatted properties for expected
    #   properties of created user.
    # - exp_changed (bool): Boolean for expected 'changed' flag.

    (
        "Present with non-existing user",
        None,
        None,
        'present',
        STD_USER_INPUT_PROPERTIES_WITH_PW,
        STD_USER_PROPERTIES,
        True,
    ),
    (
        "Present with existing user, no properties changed",
        {},
        {
            'password_rule_name': 'Standard',
        },
        'present',
        STD_USER_INPUT_PROPERTIES,
        STD_USER_PROPERTIES,
        True,  # due to password
    ),
    (
        "Present with existing user, some properties changed",
        {
            'session-timeout': 30,
        },
        {
            'password_rule_name': 'Standard',
        },
        'present',
        STD_USER_INPUT_PROPERTIES,
        STD_USER_PROPERTIES,
        True,
    ),
    (
        "Absent with existing user",
        {},
        {
            'password_rule_name': 'Standard',
        },
        'absent',
        None,
        None,
        True,
    ),
    (
        "Absent with non-existing user",
        None,
        None,
        'absent',
        None,
        None,
        False,
    ),
]


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@pytest.mark.parametrize(
    "desc, initial_user_props, initial_related_names, input_state, "
    "input_props, exp_user_props, exp_changed",
    USER_ABSENT_PRESENT_TESTCASES)
@mock.patch("plugins.modules.zhmc_user.AnsibleModule", autospec=True)
def test_zhmc_user_absent_present(
        ansible_mod_cls,
        desc, initial_user_props, initial_related_names, input_state,
        input_props, exp_user_props, exp_changed,
        check_mode,
        hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name,unused-argument
    """
    Test the zhmc_user module with state=absent/present.
    """

    hd = hmc_session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    faked_session = hmc_session if hd.mock_file else None

    expand = False  # Expansion is tested elsewhere
    client = zhmcclient.Client(hmc_session)
    console = client.consoles.console

    # Create a user name that does not exist
    user_name = new_user_name()

    where = f"user '{user_name}'"

    # Create initial user, if specified so
    if initial_user_props is not None:
        user_props = STD_USER_PROPERTIES_WITH_PW.copy()
        user_props.update(initial_user_props)
        user_props['name'] = user_name
        if user_props['authentication-type'] == 'local':
            assert 'password' in user_props, where
            assert 'password_rule_name' in initial_related_names, where
            password_rule_name = initial_related_names['password_rule_name']
            password_rule = console.password_rules.find_by_name(
                password_rule_name)
            user_props['password-rule-uri'] = password_rule.uri
        if user_props['authentication-type'] == 'ldap':
            assert 'ldap_server_definition_name' in initial_related_names, where
            ldap_srv_def_name = \
                initial_related_names['ldap_server_definition_name']
            ldap_srv_def = console.ldap_server_definitions.find_by_name(
                ldap_srv_def_name)
            user_props['ldap-server-definition-uri'] = ldap_srv_def.uri
        try:
            console.users.create(user_props)
        except zhmcclient.HTTPError as exc:
            if exc.http_status == 403 and exc.reason == 1:
                # User is not permitted to create users
                pytest.skip(f"HMC user '{hd.userid}' is not permitted to "
                            "create initial test user")
            raise
    else:
        user_props = None

    try:

        # Prepare module input parameters (must be all required + optional)
        params = {
            'hmc_host': hmc_host,
            'hmc_auth': hmc_auth,
            'name': user_name,
            'state': input_state,
            'properties': input_props,
            'expand': expand,
            'log_file': LOG_FILE,
            '_faked_session': faked_session,
        }

        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        # Save the input params
        saved_params = params_deepcopy(params)

        # Exercise the code to be tested
        with pytest.raises(SystemExit) as exc_info:
            zhmc_user.main()
        exit_code = exc_info.value.args[0]

        assert exit_code == 0, \
            f"{where}: Module failed with exit code {exit_code} and " \
            f"message:\n{get_failure_msg(mod_obj)}"

        # Check that the input params have not been changed
        assert params == saved_params

        changed, output_props = get_module_output(mod_obj)
        if changed != exp_changed:
            user_props_sorted = \
                dict(sorted(user_props.items(), key=lambda x: x[0])) \
                if user_props is not None else None
            input_props_sorted = \
                dict(sorted(input_props.items(), key=lambda x: x[0])) \
                if input_props is not None else None
            output_props_sorted = \
                dict(sorted(output_props.items(), key=lambda x: x[0])) \
                if output_props is not None else None
            user_props_str = pformat(user_props_sorted, indent=2)
            input_props_str = pformat(input_props_sorted, indent=2)
            output_props_str = pformat(output_props_sorted, indent=2)
            raise AssertionError(
                "Unexpected change flag returned: "
                f"actual: {changed}, expected: {exp_changed}\n"
                f"Initial user properties:\n{user_props_str}\n"
                f"Module input properties:\n{input_props_str}\n"
                f"Resulting user properties:\n{output_props_str}")
        if input_state == 'present':
            assert_user_props(output_props, expand, where)

    finally:
        # Delete user, if it exists
        try:
            # We invalidate the name cache of our client, because the user
            # was possibly deleted by the Ansible module and not through our
            # client instance.
            console.users.invalidate_cache()
            user = console.users.find_by_name(user_name)
        except zhmcclient.NotFound:
            user = None
        if user:
            user.delete()


UPDATE_USER_ROLES_TESTCASES = [
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - initial_urole_names (list): Names of user roles on the initial user.
    # - input_urole_names (list): 'user_role_names' input property for update
    #   of the user.
    # - exp_urole_names (list): Expected user role names after update of the
    #   user.
    # - exp_exc_type (type): Expected exception type, or None for success.
    # - exp_changed (bool): Expected 'changed' flag.

    (
        "No initial user role, no input user role",
        [],
        [],
        [],
        None,
        False,
    ),
    (
        "No initial user role, one input user role",
        [],
        ['hmc-access-administrator-tasks'],
        ['hmc-access-administrator-tasks'],
        None,
        True,
    ),
    (
        "One initial user role, no input user role",
        ['hmc-access-administrator-tasks'],
        [],
        [],
        None,
        True,
    ),
    (
        "One initial user role, another input user role",
        ['hmc-access-administrator-tasks'],
        ['hmc-all-system-managed-objects'],
        ['hmc-all-system-managed-objects'],
        None,
        True,
    ),
    (
        "One initial user role, the same input user role",
        ['hmc-access-administrator-tasks'],
        ['hmc-access-administrator-tasks'],
        ['hmc-access-administrator-tasks'],
        None,
        False,
    ),
    (
        "One initial user role, the same and another input user role",
        ['hmc-access-administrator-tasks'],
        ['hmc-access-administrator-tasks', 'hmc-all-system-managed-objects'],
        ['hmc-access-administrator-tasks', 'hmc-all-system-managed-objects'],
        None,
        True,
    ),
]


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@pytest.mark.parametrize(
    "desc, initial_urole_names, input_urole_names, exp_urole_names, "
    "exp_exc_type, exp_changed",
    UPDATE_USER_ROLES_TESTCASES)
@mock.patch("plugins.modules.zhmc_user.AnsibleModule", autospec=True)
def test_zhmc_update_user_roles(
        ansible_mod_cls,
        desc, initial_urole_names, input_urole_names, exp_urole_names,
        exp_exc_type, exp_changed,
        check_mode,
        hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name,unused-argument
    """
    Test the zhmc_user module with updating user roles on existing users.
    """

    hd = hmc_session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    faked_session = hmc_session if hd.mock_file else None

    expand = False  # Expansion is tested elsewhere
    client = zhmcclient.Client(hmc_session)
    console = client.consoles.console

    user_name = new_user_name()
    where = f"user '{user_name}'"

    try:
        # Create a user with a unique new name
        user_create_props = dict(STD_USER_PROPERTIES_WITH_PW)
        user_create_props['name'] = user_name
        pwrule = console.password_rules.find(name='Standard')
        user_create_props['password-rule-uri'] = pwrule.uri

        try:
            user = console.users.create(user_create_props)
        except zhmcclient.HTTPError as exc:
            if exc.http_status == 403 and exc.reason == 1:
                # User is not permitted to create users
                pytest.skip(f"HMC user '{hd.userid}' is not permitted to "
                            "create initial test user")
            raise

        # Add the initial user roles to the user
        for urole_name in initial_urole_names:
            urole = console.user_roles.find(name=urole_name)
            user.add_user_role(urole)

        # Prepare module input parameters (must be all required + optional)
        params = {
            'hmc_host': hmc_host,
            'hmc_auth': hmc_auth,
            'name': user_name,
            'state': 'present',
            'properties': {
                'user_role_names': input_urole_names,
            },
            'expand': False,
            'log_file': LOG_FILE,
            '_faked_session': faked_session,
        }

        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        # Exercise the code to be tested
        with pytest.raises(SystemExit) as exc_info:
            zhmc_user.main()
        exit_code = exc_info.value.args[0]

        assert exit_code == 0, \
            f"{where}: Module failed with exit code {exit_code} and " \
            f"message:\n{get_failure_msg(mod_obj)}"

        changed, output_props = get_module_output(mod_obj)
        output_urole_names = output_props['user-role-names']

        if changed != exp_changed:
            initial_uroles_sorted = sorted(initial_urole_names)
            input_uroles_sorted = sorted(input_urole_names)
            output_uroles_sorted = sorted(output_urole_names)
            intial_uroles_str = pformat(initial_uroles_sorted, indent=2)
            input_uroles_str = pformat(input_uroles_sorted, indent=2)
            output_uroles_str = pformat(output_uroles_sorted, indent=2)
            raise AssertionError(
                "Unexpected change flag returned: "
                f"actual: {changed}, expected: {exp_changed}\n"
                f"Initial user roles:\n{intial_uroles_str}\n"
                f"Module input user roles:\n{input_uroles_str}\n"
                f"Resulting user roles:\n{output_uroles_str}")

        assert_user_props(output_props, expand, where)

        assert set(output_urole_names) == set(exp_urole_names)

    finally:
        # Delete user
        try:
            # We invalidate the name cache of our client, because the user
            # was possibly deleted by the Ansible module and not through our
            # client instance.
            console.users.invalidate_cache()
            user = console.users.find_by_name(user_name)
        except zhmcclient.NotFound:
            user = None
        if user:
            user.delete()
