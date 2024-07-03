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
End2end tests for zhmc_user_pattern module.
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

from plugins.modules import zhmc_user_pattern
from .utils import mock_ansible_module, get_failure_msg

urllib3.disable_warnings()

# Print debug messages
DEBUG = False

LOG_FILE = 'zhmc_user_pattern.log' if DEBUG else None

# Properties in the returned user pattern facts that are not always present, but
# only under certain conditions. This includes artificial properties whose base
# properties are not always present. The
# comments state the condition under which the property is present.
UPATTERN_CONDITIONAL_PROPS = (
)


# A standard test user pattern, as the Ansible module input properties (i.e.
# using underscores, and limited to valid input parameters)
STD_UPATTERN_MODULE_INPUT_PROPS = {
    # 'name': provided in separate module input parameter
    'description': "zhmc test user pattern",
    'type': "glob-like",
    'pattern': "zhmc*@*ibm.com",
    'retention_time': 7,
    'specific_template_name': None,  # if set to None, will be set in test fct
}


# A standard test user pattern, as the input properties for
# UserPatternManager.create() (i.e. using dashes, and limited to valid input
# parameters)
STD_UPATTERN_HMC_INPUT_PROPS = {
    # 'name': updated upon use
    'description': "zhmc test user pattern",
    'type': 'glob-like',
    'pattern': "zhmc*@*ibm.com",
    'retention-time': 7,
    'specific-template-uri': None,  # if set to None, will be set in test fct
}


def new_upattern_name():
    """Return random unique user pattern name"""
    upattern_name = f'test_{uuid.uuid4()}'
    return upattern_name


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, properties) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, user_pattern):
        return changed, user_pattern

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_upattern_props(upattern_props, exp_upattern_props, where):
    """
    Assert the properties of the output object of the zhmc_user_pattern module

    upattern_props: Actual properties returned by the module, with underscores
      in property names, and including any artificial properties.
    """

    assert isinstance(upattern_props, dict), where  # Dict of User pattern props

    # Assert presence of properties in the output
    for prop_name in zhmc_user_pattern.ZHMC_USER_PATTERN_PROPERTIES:
        prop_name_hmc = prop_name.replace('_', '-')
        if prop_name_hmc in UPATTERN_CONDITIONAL_PROPS:
            continue
        where_prop = where + f", property {prop_name!r}"
        assert prop_name in upattern_props, where_prop

    # Assert values of non-artificial properties in the output
    for prop_name_hmc, exp_value in exp_upattern_props.items():
        prop_name = prop_name_hmc.replace('-', '_')
        act_value = upattern_props[prop_name]
        where_prop = where + f", property {prop_name!r}"
        assert act_value == exp_value, where_prop

    # TODO: Check values of artificial properties in the output


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_user_pattern.AnsibleModule", autospec=True)
def test_zhmc_user_pattern_facts(
        ansible_mod_cls, check_mode, hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_user_pattern module with state=facts.
    """

    hd = hmc_session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    client = zhmcclient.Client(hmc_session)
    console = client.consoles.console

    faked_session = hmc_session if hd.mock_file else None

    # Determine a random existing user pattern of the desired type to test.
    upatterns = console.user_patterns.list()
    upattern = random.choice(upatterns)
    upattern.pull_full_properties()

    where = f"user pattern '{upattern.name}'"

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'name': upattern.name,
        'state': 'facts',
        'properties': None,
        'log_file': LOG_FILE,
        '_faked_session': faked_session,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_user_pattern.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, \
        f"{where}: Module failed with exit code {exit_code} and message:\n" \
        f"{get_failure_msg(mod_obj)}"

    # Assert module output
    changed, upattern_props = get_module_output(mod_obj)
    assert changed is False, where
    assert_upattern_props(upattern_props, upattern.properties, where)


UPATTERN_ABSENT_PRESENT_TESTCASES = [
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - initial_upattern_props (dict): HMC-formatted properties for initial
    #    user pattern, in addition to STD_UPATTERN_HMC_INPUT_PROPS, or None for
    #    no initial user pattern.
    # - input_state (str): 'state' input parameter for module.
    # - input_props (dict): 'properties' input parameter for module.
    # - exp_upattern_props (dict): HMC-formatted properties for expected
    #   properties of created user pattern.
    # - exp_changed (bool): Boolean for expected 'changed' flag.

    (
        "Present with non-existing user pattern",
        None,
        'present',
        STD_UPATTERN_MODULE_INPUT_PROPS,
        STD_UPATTERN_HMC_INPUT_PROPS,
        True,
    ),
    (
        "Present with existing user pattern, no properties changed",
        {},
        'present',
        None,
        STD_UPATTERN_HMC_INPUT_PROPS,
        False,
    ),
    (
        "Present with existing user pattern, some properties changed",
        {
            'description': 'bla',
        },
        'present',
        STD_UPATTERN_MODULE_INPUT_PROPS,
        STD_UPATTERN_HMC_INPUT_PROPS,
        True,
    ),
    (
        "Absent with existing user pattern",
        {},
        'absent',
        None,
        None,
        True,
    ),
    (
        "Absent with non-existing user pattern",
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
    "desc, initial_upattern_props, input_state, "
    "input_props, exp_upattern_props, exp_changed",
    UPATTERN_ABSENT_PRESENT_TESTCASES)
@mock.patch("plugins.modules.zhmc_user_pattern.AnsibleModule", autospec=True)
def test_zhmc_user_pattern_absent_present(
        ansible_mod_cls,
        desc, initial_upattern_props, input_state,
        input_props, exp_upattern_props, exp_changed,
        check_mode,
        hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name,unused-argument
    """
    Test the zhmc_user_pattern module with state=absent/present.
    """

    hd = hmc_session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    faked_session = hmc_session if hd.mock_file else None

    client = zhmcclient.Client(hmc_session)
    console = client.consoles.console

    # Create a user pattern name that does not exist
    upattern_name = new_upattern_name()

    where = f"user pattern '{upattern_name}'"

    # Pick a random user template in case we need it
    user_templates = console.users.findall(type='template')
    if not user_templates:
        pytest.skip("HMC does not have a user template")
    user_template = random.choice(user_templates)

    if input_props is not None:

        # Specify a random user template
        if 'specific_template_name' in input_props and \
                input_props['specific_template_name'] is None:
            input_props = dict(input_props)
            input_props['specific_template_name'] = user_template.name
            if exp_upattern_props is not None:
                exp_upattern_props = dict(exp_upattern_props)
                exp_upattern_props['specific-template-uri'] = user_template.uri

    # Create initial user pattern, if specified so
    if initial_upattern_props is not None:
        upattern_props = STD_UPATTERN_HMC_INPUT_PROPS.copy()
        upattern_props.update(initial_upattern_props)
        upattern_props['name'] = upattern_name

        # Specify a random user template
        if 'specific-template-uri' in upattern_props and \
                upattern_props['specific-template-uri'] is None:
            upattern_props['specific-template-uri'] = user_template.uri
            if exp_upattern_props is not None:
                exp_upattern_props = dict(exp_upattern_props)
                exp_upattern_props['specific-template-uri'] = user_template.uri

        try:
            console.user_patterns.create(upattern_props)
        except zhmcclient.HTTPError as exc:
            if exc.http_status == 403 and exc.reason == 1:
                # User is not permitted to create user patterns
                pytest.skip(f"HMC user '{hd.userid}' is not permitted to "
                            "create initial test user pattern")
            else:
                raise
    else:
        upattern_props = None

    try:

        # Prepare module input parameters (must be all required + optional)
        params = {
            'hmc_host': hmc_host,
            'hmc_auth': hmc_auth,
            'name': upattern_name,
            'state': input_state,
            'properties': input_props,
            'log_file': LOG_FILE,
            '_faked_session': faked_session,
        }

        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        # Exercise the code to be tested
        with pytest.raises(SystemExit) as exc_info:
            zhmc_user_pattern.main()
        exit_code = exc_info.value.args[0]

        if exit_code != 0:
            msg = get_failure_msg(mod_obj)
            if msg.startswith('HTTPError: 403,1'):
                pytest.skip(f"HMC user '{hd.userid}' is not permitted to "
                            "create test user pattern")
            raise AssertionError(
                f"{where}: Module failed with exit code {exit_code} and "
                f"message:\n{msg}")

        changed, output_props = get_module_output(mod_obj)
        if changed != exp_changed:
            upattern_props_sorted = \
                dict(sorted(upattern_props.items(), key=lambda x: x[0])) \
                if upattern_props is not None else None
            input_props_sorted = \
                dict(sorted(input_props.items(), key=lambda x: x[0])) \
                if input_props is not None else None
            output_props_sorted = \
                dict(sorted(output_props.items(), key=lambda x: x[0])) \
                if output_props is not None else None
            upattern_props_str = pformat(upattern_props_sorted, indent=2)
            input_props_str = pformat(input_props_sorted, indent=2)
            output_props_str = pformat(output_props_sorted, indent=2)
            raise AssertionError(
                "Unexpected change flag returned: "
                f"actual: {changed}, expected: {exp_changed}\n"
                f"Initial user pattern properties:\n{upattern_props_str}\n"
                f"Module input properties:\n{input_props_str}\n"
                f"Resulting user pattern properties:\n{output_props_str}")
        if input_state == 'present':
            assert_upattern_props(output_props, exp_upattern_props, where)

    finally:
        # Delete user pattern, if it exists
        try:
            # We invalidate the name cache of our client, because the user pattern
            # was possibly deleted by the Ansible module and not through our
            # client instance.
            console.user_patterns.invalidate_cache()
            upattern = console.user_patterns.find_by_name(upattern_name)
        except zhmcclient.NotFound:
            upattern = None
        if upattern:
            upattern.delete()
