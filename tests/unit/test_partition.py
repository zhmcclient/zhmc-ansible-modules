#!/usr/bin/env python

"""
Unit tests for the 'zhmc_partition' Ansible module.
"""

import unittest
import mock

from ansible.modules.zhmc import zhmc_partition
from ansible.module_utils.zhmc import utils


class TestZhmcPartitionMain(unittest.TestCase):
    """
    Unit tests for the main() function.
    """

    @mock.patch("ansible.modules.zhmc.zhmc_partition.perform_task",
                autospec=True)
    @mock.patch("ansible.modules.zhmc.zhmc_partition.AnsibleModule",
                autospec=True)
    def test_main_success(self, ansible_mod_cls, perform_task_func):
        """
        Test main() with all required module parameters.
        """

        # Module invocation
        params = {
            'hmc_host': 'fake-host',
            'hmc_userid': 'fake-userid',
            'hmc_password': 'fake-password',
            'cpc_name': 'fake-cpc-name',
            'name': 'fake-name',
            'state': 'absent',
        }
        check_mode = False

        # Return values of perform_task()
        perform_task_changed = True
        perform_task_result = {}

        # Prepare mocks
        mod_obj = ansible_mod_cls.return_value
        mod_obj.params = params
        mod_obj.check_mode = check_mode
        mod_obj.fail_json.configure_mock(side_effect=SystemExit(1))
        mod_obj.exit_json.configure_mock(side_effect=SystemExit(0))
        perform_task_func.return_value = (perform_task_changed,
                                          perform_task_result)

        # Exercise code
        with self.assertRaises(SystemExit) as cm:
            zhmc_partition.main()
        exit_code = cm.exception.args[0]

        # Assert module exit code
        assert(exit_code == 0)

        # Assert call to AnsibleModule()
        expected_argument_spec = dict(
            hmc_host=dict(required=True, type='str'),
            hmc_userid=dict(required=True, type='str'),
            hmc_password=dict(required=True, type='str', no_log=True),
            cpc_name=dict(required=True, type='str'),
            name=dict(required=True, type='str'),
            state=dict(required=True, type='str',
                       choices=['absent', 'stopped', 'active']),
            properties=dict(required=False, type='dict', default={}),
        )
        assert(ansible_mod_cls.call_args ==
               mock.call(argument_spec=expected_argument_spec,
                         supports_check_mode=True))

        # Assert call to perform_task()
        assert(perform_task_func.call_args ==
               mock.call(params, check_mode))

        # Assert call to exit_json()
        assert(mod_obj.exit_json.call_args ==
               mock.call(changed=perform_task_changed,
                         partition=perform_task_result))

        # Assert no call to fail_json()
        assert(mod_obj.fail_json.called is False)

    @mock.patch("ansible.modules.zhmc.zhmc_partition.perform_task",
                autospec=True)
    @mock.patch("ansible.modules.zhmc.zhmc_partition.AnsibleModule",
                autospec=True)
    def test_main_param_error(self, ansible_mod_cls, perform_task_func):
        """
        Test main() with ParameterError being raised in perform_task().
        """

        # Module invocation
        params = {
            'hmc_host': 'fake-host',
            'hmc_userid': 'fake-userid',
            'hmc_password': 'fake-password',
            'cpc_name': 'fake-cpc-name',
            'name': 'fake-name',
            'state': 'absent',
        }
        check_mode = False

        # Exception raised by perform_task()
        perform_task_exc = utils.ParameterError("fake message")

        # Prepare mocks
        mod_obj = ansible_mod_cls.return_value
        mod_obj.params = params
        mod_obj.check_mode = check_mode
        mod_obj.fail_json.configure_mock(side_effect=SystemExit(1))
        mod_obj.exit_json.configure_mock(side_effect=SystemExit(0))
        perform_task_func.mock.configure_mock(side_effect=perform_task_exc)

        # Exercise code
        with self.assertRaises(SystemExit) as cm:
            zhmc_partition.main()
        exit_code = cm.exception.args[0]

        # Assert module exit code
        assert(exit_code == 1)

        # Assert call to perform_task()
        assert(perform_task_func.call_args ==
               mock.call(params, check_mode))

        # Assert call to fail_json()
        assert(mod_obj.fail_json.call_args ==
               mock.call(msg="ParameterError: fake message"))

        # Assert no call to exit_json()
        assert(mod_obj.exit_json.called is False)


class TestZhmcPartitionPerformTask(unittest.TestCase):
    """
    Unit tests for the perform_task() function.
    """

    @mock.patch("ansible.modules.zhmc.zhmc_partition.ensure_absent",
                autospec=True)
    @mock.patch("ansible.modules.zhmc.zhmc_partition.ensure_active",
                autospec=True)
    @mock.patch("ansible.modules.zhmc.zhmc_partition.ensure_stopped",
                autospec=True)
    def test_pt_active(self, ensure_stopped_func, ensure_active_func,
                       ensure_absent_func):
        """
        Test perform_task() with state 'active'.
        """

        # Prepare input arguments
        params = {
            'state': 'active',
        }
        check_mode = True

        # Prepare return values
        changed = False
        result = {
            'fake-prop': 'fake-value',
        }

        # Prepare mocks
        ensure_active_func.return_value = (changed, result)

        # Exercise code
        actual_changed, actual_result = zhmc_partition.perform_task(
            params, check_mode)

        # Assert return values
        assert(actual_changed == changed)
        assert(actual_result == result)

        # Assert call to the desired action function
        assert(ensure_active_func.call_args ==
               mock.call(params, check_mode))

        # Assert no call to the other action functions
        assert(ensure_stopped_func.called is False)
        assert(ensure_absent_func.called is False)

    @mock.patch("ansible.modules.zhmc.zhmc_partition.ensure_absent",
                autospec=True)
    @mock.patch("ansible.modules.zhmc.zhmc_partition.ensure_active",
                autospec=True)
    @mock.patch("ansible.modules.zhmc.zhmc_partition.ensure_stopped",
                autospec=True)
    def test_pt_stopped(self, ensure_stopped_func, ensure_active_func,
                        ensure_absent_func):
        """
        Test perform_task() with state 'stopped'.
        """

        # Prepare input arguments
        params = {
            'state': 'stopped',
        }
        check_mode = True

        # Prepare return values
        changed = True
        result = {
            'fake-prop': 'fake-value',
        }

        # Prepare mocks
        ensure_stopped_func.return_value = (changed, result)

        # Exercise code
        actual_changed, actual_result = zhmc_partition.perform_task(
            params, check_mode)

        # Assert return values
        assert(actual_changed == changed)
        assert(actual_result == result)

        # Assert call to the desired action function
        assert(ensure_stopped_func.call_args ==
               mock.call(params, check_mode))

        # Assert no call to the other action functions
        assert(ensure_active_func.called is False)
        assert(ensure_absent_func.called is False)

    @mock.patch("ansible.modules.zhmc.zhmc_partition.ensure_absent",
                autospec=True)
    @mock.patch("ansible.modules.zhmc.zhmc_partition.ensure_active",
                autospec=True)
    @mock.patch("ansible.modules.zhmc.zhmc_partition.ensure_stopped",
                autospec=True)
    def test_pt_absent(self, ensure_stopped_func, ensure_active_func,
                       ensure_absent_func):
        """
        Test perform_task() with state 'absent'.
        """

        # Prepare input arguments
        params = {
            'state': 'absent',
        }
        check_mode = False

        # Prepare return values
        changed = True
        result = {
            'fake-prop': 'fake-value',
        }

        # Prepare mocks
        ensure_absent_func.return_value = (changed, result)

        # Exercise code
        actual_changed, actual_result = zhmc_partition.perform_task(
            params, check_mode)

        # Assert return values
        assert(actual_changed == changed)
        assert(actual_result == result)

        # Assert call to the desired action function
        assert(ensure_absent_func.call_args ==
               mock.call(params, check_mode))

        # Assert no call to the other action functions
        assert(ensure_active_func.called is False)
        assert(ensure_stopped_func.called is False)


# The other functions of the module are tested with function tests.
