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
End2end tests for zhmc_ldap_server_definition module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import uuid
import pytest
from unittest import mock
import random
from pprint import pformat
import requests.packages.urllib3
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_ldap_server_definition
from .utils import mock_ansible_module, get_failure_msg

requests.packages.urllib3.disable_warnings()

# Print debug messages
DEBUG = False

LOG_FILE = 'zhmc_ldap_server_definition.log' if DEBUG else None

# Properties in the returned LDAP server definition facts that are not always
# present, but only under certain conditions. The comments state the condition
# under which the property is present.
LSD_CONDITIONAL_PROPS = (
    'bind-password',  # not returned by retrieval
)


# A standard test LDAP server definition, as the Ansible module input
# properties (i.e. using underscores, and limited to valid input parameters)
STD_LSD_MODULE_INPUT_PROPS = {
    # 'name': provided in separate module input parameter
    'description': "zhmc test LDAP server definition",
    'primary_hostname_ipaddr': '10.11.12.13',
    'search_distinguished_name': 'test_user{0}',
}


# A standard test LDAP server definition, as the input properties for
# LDAPServerDefinitionManager.create() (i.e. using dashes, and limited to valid
# input parameters)
STD_LSD_HMC_INPUT_PROPS = {
    # 'name': updated upon use
    'description': "zhmc test LDAP server definition",
    'primary-hostname-ipaddr': '10.11.12.13',
    'search-distinguished-name': 'test_user{0}',
}


def updated_copy(dict1, dict2):
    dict1c = dict1.copy()
    dict1c.update(dict2)
    return dict1c


def new_lsd_name():
    lsd_name = f'test_{uuid.uuid4()}'
    return lsd_name


def diffcase(name):
    """Return name in different case"""
    ret = ''
    for c in name:
        if c.islower():
            c = c.upper()
        elif c.isupper():
            c = c.lower()
        ret += c
    return ret


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, user_properties) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, ldap_server_definition):
        return changed, ldap_server_definition

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_lsd_props(lsd_props, exp_lsd_props, where):
    """
    Assert the properties of the output object of the
    zhmc_ldap_server_definition module
    """

    assert isinstance(lsd_props, dict), where  # Dict of LDAP srv.def. props

    # Assert presence of properties in the output
    for prop_name in zhmc_ldap_server_definition.ZHMC_LSD_PROPERTIES:
        prop_name_hmc = prop_name.replace('_', '-')
        if prop_name_hmc in LSD_CONDITIONAL_PROPS:
            continue
        where_prop = where + f", property {prop_name!r}"
        assert prop_name_hmc in lsd_props, where_prop

    # Assert the expected property values for non-artificial properties
    artificial_prop_names = (
        'permissions',
        'associated-system-defined-user-role-name',
    )
    for prop_name in exp_lsd_props:
        if prop_name in artificial_prop_names:
            continue
        exp_value = exp_lsd_props[prop_name]
        act_value = lsd_props[prop_name]
        where_prop = where + f", property {prop_name!r}"
        assert act_value == exp_value, where_prop


@pytest.mark.parametrize(
    "diff_case", [
        pytest.param(False, id="diff_case=False"),
        pytest.param(True, id="diff_case=True"),
    ]
)
@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_ldap_server_definition.AnsibleModule",
            autospec=True)
def test_zhmc_ldap_server_definition_facts(
        ansible_mod_cls, check_mode, diff_case,
        hmc_session):  # noqa: F811, E501
    """
    Test the zhmc_ldap_server_definition module with state=facts.
    """

    hd = hmc_session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    client = zhmcclient.Client(hmc_session)
    console = client.consoles.console

    faked_session = hmc_session if hd.mock_file else None

    # Determine a random existing LDAP server definition of the desired type
    # to test.
    lsds = console.ldap_server_definitions.list()
    lsd = random.choice(lsds)

    where = f"LDAP server definition '{lsd.name}'"

    # Prepare module input parameters (must be all required + optional)
    name = diffcase(lsd.name) if diff_case else lsd.name
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'name': name,
        'state': 'facts',
        'log_file': LOG_FILE,
        '_faked_session': faked_session,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_ldap_server_definition.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, \
        f"{where}: Module failed with exit code {exit_code} and message:\n" \
        f"{get_failure_msg(mod_obj)}"

    # Assert module output
    changed, lsd_props = get_module_output(mod_obj)
    assert changed is False, where
    assert_lsd_props(lsd_props, lsd.properties, where)


LSD_ABSENT_PRESENT_TESTCASES = [
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - initial_lsd_props (dict): HMC-formatted properties for initial
    #    LDAP server definition, in addition to STD_LSD_HMC_INPUT_PROPS,
    #    or None for no initial LDAP server definition.
    # - input_state (str): 'state' input parameter for
    #   zhmc_ldap_server_definition module.
    # - input_props (dict): 'properties' input parameter for
    #   zhmc_ldap_server_definition module.
    # - exp_lsd_props (dict): HMC-formatted properties for expected
    #   properties of created LDAP server definition.
    # - exp_changed (bool): Boolean for expected 'changed' flag.

    (
        "Present with non-existing LDAP server definition",
        None,
        'present',
        STD_LSD_MODULE_INPUT_PROPS,
        STD_LSD_HMC_INPUT_PROPS,
        True,
    ),
    (
        "Present with existing LDAP server definition, no properties changed",
        {},
        'present',
        None,
        STD_LSD_HMC_INPUT_PROPS,
        False,
    ),
    (
        "Present with existing LDAP server definition, some properties changed",
        {
            'description': 'bla',
        },
        'present',
        STD_LSD_MODULE_INPUT_PROPS,
        STD_LSD_HMC_INPUT_PROPS,
        True,
    ),
    (
        "Absent with existing LDAP server definition",
        {},
        'absent',
        None,
        None,
        True,
    ),
    (
        "Absent with non-existing LDAP server definition",
        None,
        'absent',
        None,
        None,
        False,
    ),
]


@pytest.mark.parametrize(
    "diff_case", [
        pytest.param(False, id="diff_case=False"),
        pytest.param(True, id="diff_case=True"),
    ]
)
@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@pytest.mark.parametrize(
    "desc, initial_lsd_props, input_state, "
    "input_props, exp_lsd_props, exp_changed",
    LSD_ABSENT_PRESENT_TESTCASES)
@mock.patch("plugins.modules.zhmc_ldap_server_definition.AnsibleModule",
            autospec=True)
def test_zhmc_ldap_server_definition_absent_present(
        ansible_mod_cls,
        desc, initial_lsd_props, input_state,
        input_props, exp_lsd_props, exp_changed,
        check_mode, diff_case,
        hmc_session):  # noqa: F811, E501
    """
    Test the zhmc_ldap_server_definition module with state=absent/present.
    """

    hd = hmc_session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    faked_session = hmc_session if hd.mock_file else None

    client = zhmcclient.Client(hmc_session)
    console = client.consoles.console

    # Create a LDAP server definition name that does not exist
    lsd_name = new_lsd_name()

    where = f"LDAP server definition '{lsd_name}'"

    # Create initial LDAP server definition, if specified so
    if initial_lsd_props is not None:
        lsd_props = STD_LSD_HMC_INPUT_PROPS.copy()
        lsd_props.update(initial_lsd_props)
        lsd_props['name'] = lsd_name

        try:
            console.ldap_server_definitions.create(lsd_props)
        except zhmcclient.HTTPError as exc:
            if exc.http_status == 403 and exc.reason == 1:
                # User is not permitted to create LDAP server definitions
                pytest.skip(f"HMC user '{hd.userid}' is not permitted to "
                            "create initial test LDAP server definition")
            else:
                raise
    else:
        lsd_props = None

    try:

        # Prepare module input parameters (must be all required + optional)
        name = diffcase(lsd_name) if diff_case else lsd_name
        params = {
            'hmc_host': hmc_host,
            'hmc_auth': hmc_auth,
            'name': name,
            'state': input_state,
            'log_file': LOG_FILE,
            '_faked_session': faked_session,
        }
        if input_props is not None:
            params['properties'] = input_props
        else:
            params['properties'] = {}

        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        # Exercise the code to be tested
        with pytest.raises(SystemExit) as exc_info:
            zhmc_ldap_server_definition.main()
        exit_code = exc_info.value.args[0]

        if exit_code != 0:
            msg = get_failure_msg(mod_obj)
            if msg.startswith('HTTPError: 403,1'):
                pytest.skip(f"HMC user '{hd.userid}' is not permitted to "
                            "create test LDAP server definition")
            raise AssertionError(
                f"{where}: Module failed with exit code {exit_code} and "
                f"message:\n{msg}")

        changed, output_props = get_module_output(mod_obj)
        if changed != exp_changed:
            lsd_props_sorted = \
                dict(sorted(lsd_props.items(), key=lambda x: x[0])) \
                if lsd_props is not None else None
            input_props_sorted = \
                dict(sorted(input_props.items(), key=lambda x: x[0])) \
                if input_props is not None else None
            output_props_sorted = \
                dict(sorted(output_props.items(), key=lambda x: x[0])) \
                if output_props is not None else None
            lsd_props_str = pformat(lsd_props_sorted, indent=2)
            input_props_str = pformat(input_props_sorted, indent=2)
            output_props_str = pformat(output_props_sorted, indent=2)
            raise AssertionError(
                f"Unexpected change flag returned: actual: {changed}, "
                f"expected: {exp_changed}\n"
                f"Initial LDAP server definition properties:\n{lsd_props_str}\n"
                f"Module input properties:\n{input_props_str}\n"
                "Resulting LDAP server definition properties:\n"
                f"{output_props_str}")
        if input_state == 'present':
            assert_lsd_props(output_props, exp_lsd_props, where)

    finally:
        # Delete LDAP server definition, if it exists
        try:
            # We invalidate the name cache of our client, because the LDAP
            # server definition was possibly deleted by the Ansible module and
            # not through our client instance.
            console.ldap_server_definitions.invalidate_cache()
            lsd = console.ldap_server_definitions.find_by_name(lsd_name)
        except zhmcclient.NotFound:
            lsd = None
        if lsd:
            lsd.delete()
