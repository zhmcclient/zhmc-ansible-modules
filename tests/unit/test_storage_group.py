#!/usr/bin/env python
# Copyright 2026 IBM Corp. All Rights Reserved.
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
Unit tests for the 'zhmc_storage_group' Ansible module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest import mock
import pytest

from plugins.modules import zhmc_storage_group
from plugins.module_utils import common as module_utils


@pytest.mark.parametrize(
    "state", ['absent', 'present', 'discover', 'facts', 'accept_mismatched'])
@pytest.mark.parametrize(
    "check_mode", [False, True])
@mock.patch("plugins.modules.zhmc_storage_group.perform_task",
            autospec=True)
@mock.patch("plugins.modules.zhmc_storage_group.AnsibleModule",
            autospec=True)
def test_main_success(
        ansible_mod_cls, perform_task_func, check_mode, state):
    """
    Test main() with all module states.
    """

    # Module invocation
    params = {
        'hmc_host': 'fake-host',
        'hmc_auth': dict(userid='fake-userid',
                         password='fake-password'),
        'cpc_name': 'fake-cpc-name',
        'name': 'fake-name',
        'state': state,
        'properties': None,
        'expand': False,
        'discover_wait': False,
        'discover_timeout': 300,
        'log_file': None,
        '_faked_session': None,
    }

    # Return values of perform_task()
    perform_task_changed = True
    perform_task_result = {'name': 'fake-name'}

    # Prepare mocks
    mod_obj = ansible_mod_cls.return_value
    mod_obj.params = params
    mod_obj.check_mode = check_mode
    mod_obj.fail_json.configure_mock(side_effect=SystemExit(1))
    mod_obj.exit_json.configure_mock(side_effect=SystemExit(0))
    perform_task_func.return_value = (perform_task_changed,
                                      perform_task_result)

    # Exercise code
    with pytest.raises(SystemExit) as exc_info:
        zhmc_storage_group.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0

    # Assert call to AnsibleModule()
    expected_argument_spec = dict(
        hmc_host=dict(required=True, type='raw'),
        hmc_auth=dict(
            required=True,
            type='dict',
            options=dict(
                userid=dict(required=False, type='str', default=None),
                password=dict(required=False, type='str', default=None,
                              no_log=True),
                session_id=dict(required=False, type='str', default=None,
                                no_log=True),
                ca_certs=dict(required=False, type='str', default=None),
                verify=dict(required=False, type='bool', default=True),
            ),
        ),
        cpc_name=dict(required=True, type='str'),
        name=dict(required=True, type='str'),
        state=dict(required=True, type='str',
                   choices=['absent', 'present', 'discover', 'facts',
                            'accept_mismatched']),
        properties=dict(required=False, type='dict', default=None),
        expand=dict(required=False, type='bool', default=False),
        discover_wait=dict(required=False, type='bool', default=False),
        discover_timeout=dict(required=False, type='int', default=300),
        log_file=dict(required=False, type='str', default=None),
        _faked_session=dict(required=False, type='raw'),
    )
    assert ansible_mod_cls.call_args == \
        mock.call(argument_spec=expected_argument_spec,
                  supports_check_mode=True)

    # Assert call to perform_task()
    assert perform_task_func.call_args == mock.call(params, check_mode)

    # Assert call to exit_json()
    assert mod_obj.exit_json.call_args == \
        mock.call(changed=perform_task_changed,
                  storage_group=perform_task_result)

    # Assert no call to fail_json()
    assert mod_obj.fail_json.called is False


@mock.patch("plugins.modules.zhmc_storage_group.open_session",
            autospec=True)
@mock.patch("plugins.modules.zhmc_storage_group.close_session",
            autospec=True)
@mock.patch("zhmcclient.Client", autospec=True)
def test_accept_mismatched_success(client_cls, close_session_func,
                                   open_session_func):
    """
    Test accept_mismatched() on an FCP storage group.
    """
    params = {
        'cpc_name': 'cpc-1',
        'name': 'sg-1',
        'expand': False,
    }
    session = mock.MagicMock()
    open_session_func.return_value = (session, False)

    client_mock = client_cls.return_value
    cpc_mock = mock.MagicMock()
    cpc_mock.uri = '/api/cpcs/1'
    client_mock.cpcs.find.return_value = cpc_mock

    sg_mock = mock.MagicMock()
    sg_mock.cpc = cpc_mock
    sg_mock.prop.return_value = 'fcp'
    sg_mock.get_property.return_value = 'fcp'
    sg_mock.properties = {'name': 'sg-1', 'type': 'fcp'}
    sg_mock.list_attached_partitions.return_value = []
    client_mock.consoles.console.storage_groups.find.return_value = sg_mock

    # Test in non-check mode
    changed, result = zhmc_storage_group.accept_mismatched(params, check_mode=False)

    assert changed is True
    assert result['name'] == 'sg-1'
    sg_mock.accept_mismatched_fcp_storage_volumes.assert_called_once()
    sg_mock.pull_full_properties.assert_called_once()
    close_session_func.assert_called_once_with(session, False)


@mock.patch("plugins.modules.zhmc_storage_group.open_session",
            autospec=True)
@mock.patch("plugins.modules.zhmc_storage_group.close_session",
            autospec=True)
@mock.patch("zhmcclient.Client", autospec=True)
def test_accept_mismatched_check_mode(client_cls, close_session_func,
                                      open_session_func):
    """
    Test accept_mismatched() in check mode.
    """
    params = {
        'cpc_name': 'cpc-1',
        'name': 'sg-1',
        'expand': False,
    }
    session = mock.MagicMock()
    open_session_func.return_value = (session, False)

    client_mock = client_cls.return_value
    cpc_mock = mock.MagicMock()
    cpc_mock.uri = '/api/cpcs/1'
    client_mock.cpcs.find.return_value = cpc_mock

    sg_mock = mock.MagicMock()
    sg_mock.cpc = cpc_mock
    sg_mock.prop.return_value = 'fcp'
    sg_mock.get_property.return_value = 'fcp'
    sg_mock.properties = {'name': 'sg-1', 'type': 'fcp'}
    sg_mock.list_attached_partitions.return_value = []
    client_mock.consoles.console.storage_groups.find.return_value = sg_mock

    # Test in check mode
    changed, result = zhmc_storage_group.accept_mismatched(params, check_mode=True)

    assert changed is True
    assert result['name'] == 'sg-1'
    sg_mock.accept_mismatched_fcp_storage_volumes.assert_not_called()
    close_session_func.assert_called_once_with(session, False)


@mock.patch("plugins.modules.zhmc_storage_group.open_session",
            autospec=True)
@mock.patch("plugins.modules.zhmc_storage_group.close_session",
            autospec=True)
@mock.patch("zhmcclient.Client", autospec=True)
def test_accept_mismatched_not_fcp(client_cls, close_session_func,
                                   open_session_func):
    """
    Test accept_mismatched() raises ParameterError when storage group is not 'fcp'.
    """
    params = {
        'cpc_name': 'cpc-1',
        'name': 'sg-1',
        'expand': False,
    }
    session = mock.MagicMock()
    open_session_func.return_value = (session, False)

    client_mock = client_cls.return_value
    cpc_mock = mock.MagicMock()
    cpc_mock.uri = '/api/cpcs/1'
    client_mock.cpcs.find.return_value = cpc_mock

    sg_mock = mock.MagicMock()
    sg_mock.cpc = cpc_mock
    sg_mock.prop.return_value = 'fc'  # not fcp
    client_mock.consoles.console.storage_groups.find.return_value = sg_mock

    with pytest.raises(module_utils.ParameterError) as exc_info:
        zhmc_storage_group.accept_mismatched(params, check_mode=False)

    assert "is not of type 'fcp'" in str(exc_info.value)
    close_session_func.assert_called_once_with(session, False)
