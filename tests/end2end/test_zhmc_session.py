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
End2end tests for zhmc_session module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
from unittest import mock
import pytest
import urllib3
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_session, zhmc_cpc_list
from plugins.module_utils.common import parse_hmc_host
from .utils import mock_ansible_module, get_failure_msg

urllib3.disable_warnings()

# Print debug messages
DEBUG = False

LOG_FILE = 'zhmc_session.log' if DEBUG else None

# Regexp pattern to compare actual HMC session IDs against
SESSION_ID_PATTERN = re.compile(r'[a-z0-9]{45,55}')

# Indicator to take parameter from the hmc_definition
FROM_HMC_DEFINITION = 'FROM_HMC_DEFINITION'


def get_session_module_output(mod_obj):
    """
    Return the zhmc_session module output as a tuple (changed, user_properties)
    (i.e. the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, hmc_auth, hmc_host):
        return changed, hmc_auth, hmc_host

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def get_cpc_list_module_output(mod_obj):
    """
    Return the zhmc_cpc_list module output as a tuple (changed, user_properties)
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


TESTCASES_ZHMC_SESSION_SINGLE = [
    # Testcases for test_zhmc_session(), each with these items:
    # * desc (str): Testcase description
    # * check_mode (bool): Check mode flag passed to module
    # * in_params (dict): Input parameters passed to module
    # * exp_exit_code (int): Expected exit code from module
    # * exp_msg_pattern (str): Exp. regexp pattern for error message, if failure
    # * exp_changed (bool): Expected changed flag returned from module
    # * exp_hmc_auth (dict): Expected hmc_auth module result, if success

    (
        "Successful create",
        True,
        {
            'hmc_auth': {
                'userid': FROM_HMC_DEFINITION,
                'password': FROM_HMC_DEFINITION,
                'ca_certs': FROM_HMC_DEFINITION,
                'verify': FROM_HMC_DEFINITION,
                'session_id': None,
            },
            'action': 'create',
        },
        0, None,
        False,
        {
            'ca_certs': FROM_HMC_DEFINITION,
            'verify': FROM_HMC_DEFINITION,
            'session_id': SESSION_ID_PATTERN,
        }
    ),
    (
        "Failing create with missing userid",
        True,
        {
            'hmc_auth': {
                # 'userid' not specified
                'password': FROM_HMC_DEFINITION,
                'ca_certs': FROM_HMC_DEFINITION,
                'verify': FROM_HMC_DEFINITION,
                'session_id': None,
            },
            'action': 'create',
        },
        1, "ParameterError.*'userid'.*missing",
        False,
        None
    ),
    (
        "Failing create with missing password",
        True,
        {
            'hmc_auth': {
                'userid': FROM_HMC_DEFINITION,
                # 'password' not specified
                'ca_certs': FROM_HMC_DEFINITION,
                'verify': FROM_HMC_DEFINITION,
                'session_id': None,
            },
            'action': 'create',
        },
        1, "ParameterError.*'password'.*missing",
        False,
        None
    ),
    (
        "Failing create with session_id provided",
        True,
        {
            'hmc_auth': {
                'userid': FROM_HMC_DEFINITION,
                'password': FROM_HMC_DEFINITION,
                'ca_certs': FROM_HMC_DEFINITION,
                'verify': FROM_HMC_DEFINITION,
                'session_id': 'abc',  # Incorrectly provided
            },
            'action': 'create',
        },
        1, "ParameterError.*'session_id' item specified",
        False,
        None
    ),
    (
        "Failed delete with session ID because userid also provided",
        True,
        {
            'hmc_auth': {
                'userid': FROM_HMC_DEFINITION,
                'ca_certs': FROM_HMC_DEFINITION,
                'verify': FROM_HMC_DEFINITION,
                'session_id': 'abc',  # invalid values are tolerated
            },
            'action': 'delete',
        },
        1,
        "ParameterError.*'hmc_auth' has the 'session_id' item.* but "
        ".'userid'. are present",
        False,
        {
            'ca_certs': None,
            'verify': None,
            'session_id': None,
        }
    ),
    (
        "Successful delete with session ID and ca_cert/verify parms",
        True,
        {
            'hmc_auth': {
                'ca_certs': FROM_HMC_DEFINITION,
                'verify': FROM_HMC_DEFINITION,
                'session_id': 'abc',  # invalid values are tolerated
            },
            'action': 'delete',
        },
        0, None,
        False,
        {
            'ca_certs': None,
            'verify': None,
            'session_id': None,
        }
    ),
]


@pytest.mark.parametrize(
    "desc, check_mode, in_params, exp_exit_code, exp_msg_pattern, "
    "exp_changed, exp_hmc_auth",
    TESTCASES_ZHMC_SESSION_SINGLE
)
@mock.patch("plugins.modules.zhmc_session.AnsibleModule", autospec=True)
def test_zhmc_session_single(
        ansible_mod_cls, desc, check_mode, in_params, exp_exit_code,
        exp_msg_pattern, exp_changed, exp_hmc_auth,
        hmc_definition):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name,unused-argument
    """
    Test specific input parameters on single invocations of the zhmc_session
    module.
    """

    if hmc_definition.mock_file:
        pytest.skip("zhmc_session module needs real HMC for end2end test")

    hmc_host = hmc_definition.host

    action = in_params['action']

    if action == 'delete':
        parsed_hmc_host = parse_hmc_host(hmc_host)
        if isinstance(parsed_hmc_host, list):
            hmc_host = parsed_hmc_host[0]

    # Set hm_auth module input parameter from testcase definition
    hmc_auth = {}
    in_hmc_auth = in_params['hmc_auth']
    if 'userid' in in_hmc_auth:
        hmc_auth['userid'] = hmc_definition.userid \
            if in_hmc_auth['userid'] == FROM_HMC_DEFINITION \
            else in_hmc_auth['userid']
    if 'password' in in_hmc_auth:
        hmc_auth['password'] = hmc_definition.password \
            if in_hmc_auth['password'] == FROM_HMC_DEFINITION \
            else in_hmc_auth['password']
    if 'ca_certs' in in_hmc_auth:
        hmc_auth['ca_certs'] = hmc_definition.ca_certs \
            if in_hmc_auth['ca_certs'] == FROM_HMC_DEFINITION \
            else in_hmc_auth['ca_certs']
    if 'verify' in in_hmc_auth:
        hmc_auth['verify'] = hmc_definition.verify \
            if in_hmc_auth['verify'] == FROM_HMC_DEFINITION \
            else in_hmc_auth['verify']
    if 'session_id' in in_hmc_auth:
        hmc_auth['session_id'] = in_hmc_auth['session_id']

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'action': action,
        'log_file': LOG_FILE,
        '_faked_session': None,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_session.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == exp_exit_code, \
        "message: " + get_failure_msg(mod_obj)

    # Assert module failure message, if failed
    if exp_exit_code != 0:
        assert exp_msg_pattern  # That would be a testcase definition failure
        msg = get_failure_msg(mod_obj)

        assert re.match(exp_msg_pattern, msg)

    # Assert module result, if success
    if exp_exit_code == 0:
        changed, res_hmc_auth, res_hmc_host = get_session_module_output(mod_obj)
        assert changed == exp_changed

        assert set(res_hmc_auth.keys()) == set(exp_hmc_auth.keys())

        if 'userid' in exp_hmc_auth:
            assert 'userid' in res_hmc_auth
            if exp_hmc_auth['userid'] == FROM_HMC_DEFINITION:
                assert res_hmc_auth['userid'] == hmc_definition.userid
            else:
                assert res_hmc_auth['userid'] == exp_hmc_auth['userid']

        if 'ca_certs' in exp_hmc_auth:
            assert 'ca_certs' in res_hmc_auth
            if exp_hmc_auth['ca_certs'] == FROM_HMC_DEFINITION:
                assert res_hmc_auth['ca_certs'] == hmc_definition.ca_certs
            else:
                assert res_hmc_auth['ca_certs'] == exp_hmc_auth['ca_certs']

        if 'verify' in exp_hmc_auth:
            assert 'verify' in res_hmc_auth
            if exp_hmc_auth['verify'] == FROM_HMC_DEFINITION:
                assert res_hmc_auth['verify'] == hmc_definition.verify
            else:
                assert res_hmc_auth['verify'] == exp_hmc_auth['verify']

        if 'session_id' in exp_hmc_auth:
            assert 'session_id' in res_hmc_auth
            if isinstance(exp_hmc_auth['session_id'], re.Pattern):
                assert exp_hmc_auth['session_id'].match(
                    res_hmc_auth['session_id'])
            else:
                assert exp_hmc_auth['session_id'] == res_hmc_auth['session_id']

        if action == 'create':
            assert isinstance(res_hmc_host, str)
            if isinstance(hmc_host, list):
                assert res_hmc_host in hmc_host
            else:
                assert isinstance(hmc_host, str)
                assert res_hmc_host == hmc_host
        else:  # action 'delete'
            assert res_hmc_host is None


@mock.patch("plugins.modules.zhmc_session.AnsibleModule", autospec=True)
@mock.patch("plugins.modules.zhmc_cpc_list.AnsibleModule", autospec=True)
def test_zhmc_session_sequence(
        cpc_list_mod_cls, session_mod_cls, hmc_definition):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test a sequence of playbook tasks with create, use, delete of sessions
    with the zhmc_session module.
    """

    if hmc_definition.mock_file:
        pytest.skip("zhmc_session module needs real HMC for end2end test")

    check_mode = False

    # Task 1: Create a session using zhmc_session with action=create

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_definition.host,
        'hmc_auth': {
            'userid': hmc_definition.userid,
            'password': hmc_definition.password,
            'session_id': None,
            'ca_certs': hmc_definition.ca_certs,
            'verify': hmc_definition.verify,
        },
        'action': 'create',
        'log_file': LOG_FILE,
        '_faked_session': None,
    }
    mod_obj = mock_ansible_module(session_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_session.main()

    exit_code = exc_info.value.args[0]
    assert exit_code == 0, \
        "message: " + get_failure_msg(mod_obj)

    changed, res_hmc_auth, res_hmc_host = get_session_module_output(mod_obj)
    assert changed is False

    assert set(res_hmc_auth.keys()) == {'session_id', 'ca_certs', 'verify'}

    session_id = res_hmc_auth['session_id']
    assert SESSION_ID_PATTERN.match(session_id)
    assert res_hmc_auth['ca_certs'] is None or \
        isinstance(res_hmc_auth['ca_certs'], str)
    assert res_hmc_auth['verify'] in (True, False)

    assert isinstance(res_hmc_host, str)
    if isinstance(hmc_definition.host, list):
        assert res_hmc_host in hmc_definition.host
    else:
        assert isinstance(hmc_definition.host, str)
        assert res_hmc_host == hmc_definition.host

    actual_hmc_host = res_hmc_host

    # Task 2: List CPCs using the session from task 1

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': actual_hmc_host,
        'hmc_auth': {
            'userid': None,
            'password': None,
            'session_id': session_id,
            'ca_certs': hmc_definition.ca_certs,
            'verify': hmc_definition.verify,
        },
        'include_unmanaged_cpcs': False,
        'full_properties': False,
        'log_file': LOG_FILE,
        '_faked_session': None,
    }
    mod_obj = mock_ansible_module(cpc_list_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_cpc_list.main()

    exit_code = exc_info.value.args[0]
    assert exit_code == 0, \
        "message: " + get_failure_msg(mod_obj)

    changed, cpcs = get_cpc_list_module_output(mod_obj)
    assert changed is False
    assert isinstance(cpcs, list)

    # Task 3: Delete the session from task 1

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': actual_hmc_host,
        'hmc_auth': {
            'userid': None,
            'password': None,
            'session_id': session_id,
            'ca_certs': None,
            'verify': None,
        },
        'action': 'delete',
        'log_file': LOG_FILE,
        '_faked_session': None,
    }
    mod_obj = mock_ansible_module(session_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_session.main()

    exit_code = exc_info.value.args[0]
    assert exit_code == 0, \
        "message: " + get_failure_msg(mod_obj)

    changed, res_hmc_auth, res_hmc_host = get_session_module_output(mod_obj)
    assert changed is False

    assert set(res_hmc_auth.keys()) == {'session_id', 'ca_certs', 'verify'}

    assert res_hmc_auth['session_id'] is None
    assert res_hmc_auth['ca_certs'] is None
    assert res_hmc_auth['verify'] is None

    assert res_hmc_host is None
