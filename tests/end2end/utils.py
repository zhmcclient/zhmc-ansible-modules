#!/usr/bin/env python
# Copyright 2017 IBM Corp. All Rights Reserved.
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
Utility functions for end2end testing.
"""


def mock_ansible_module(ansible_mod_cls, params, check_mode):
    """
    Prepare mocks for AnsibleModule object.
    """
    mod_obj = ansible_mod_cls.return_value
    mod_obj.params = params
    mod_obj.check_mode = check_mode
    mod_obj.fail_json.configure_mock(side_effect=SystemExit(1))
    mod_obj.exit_json.configure_mock(side_effect=SystemExit(0))
    return mod_obj


def get_failure_msg(mod_obj):
    """
    Return the module failure message, as a string (i.e. the 'msg' argument
    of the call to fail_json()).
    If the module succeeded, return None.
    """

    def func(msg):
        return msg

    if not mod_obj.fail_json.called:
        return None
    call_args = mod_obj.fail_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, partition_properties) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, partition):
        return changed, partition

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])
