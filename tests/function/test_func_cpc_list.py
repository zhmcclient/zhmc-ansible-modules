#!/usr/bin/env python
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
Function tests for the 'zhmc_cpc_list' Ansible module.
"""

# pylint: disable=bad-option-value,redundant-u-string-prefix

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import mock

from zhmcclient import Client
from zhmcclient_mock import FakedSession

from plugins.modules import zhmc_cpc_list

from .func_utils import mock_ansible_module

# FakedSession() init arguments
FAKED_SESSION_KWARGS = dict(
    host='fake-host',
    hmc_name='faked-hmc-name',
    hmc_version='2.13.1',
    api_version='1.8'
)

# Faked Console that is used for all tests
# (with property names as specified in HMC data model)
FAKED_CONSOLE_URI = '/api/console'
FAKED_CONSOLE = {
    'object-uri': FAKED_CONSOLE_URI,
    'class': 'console',
    'name': 'hmc-1',
    'description': 'Console HMC1',
    'version': '2.13.0',
}

# Faked CPC in DPM mode.
# (with property names as specified in HMC data model)
FAKED_CPC_1_OID = 'fake-cpc-1'
FAKED_CPC_1_URI = '/api/cpcs/' + FAKED_CPC_1_OID
FAKED_CPC_1 = {
    'object-id': FAKED_CPC_1_OID,
    'object-uri': FAKED_CPC_1_URI,
    'class': 'cpc',
    'name': 'cpc-name-1',
    'description': 'CPC #1 in DPM mode',
    'status': 'active',
    'dpm-enabled': True,
    'is-ensemble-member': False,
    'iml-mode': 'dpm',
    'se-version': '2.13.0',
    'has-unacceptable-status': False,
}

# Faked CPC in classic mode.
# (with property names as specified in HMC data model)
FAKED_CPC_2_OID = 'fake-cpc-2'
FAKED_CPC_2_URI = '/api/cpcs/' + FAKED_CPC_2_OID
FAKED_CPC_2 = {
    'object-id': FAKED_CPC_2_OID,
    'object-uri': FAKED_CPC_2_URI,
    'class': 'cpc',
    'name': 'cpc-name-2',
    'description': 'CPC #2 in classic mode',
    'status': 'operating',
    'dpm-enabled': False,
    'is-ensemble-member': False,
    'iml-mode': 'esa390',
    'se-version': '2.14.0',
    'has-unacceptable-status': False,
}


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
    Return the module output as a tuple (changed, cpcs) (i.e.
    the arguments of the call to exit_json()).
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


class TestPartition(object):
    """
    All tests for partitions.
    """

    def setup_method(self):
        """
        Using the zhmcclient mock support, set up a CPC.
        """
        self.session = FakedSession(**FAKED_SESSION_KWARGS)
        self.client = Client(self.session)
        self.console = self.session.hmc.consoles.add(FAKED_CONSOLE)
        self.faked_cpcs = []
        self.faked_cpcs.append(self.session.hmc.cpcs.add(FAKED_CPC_1))
        self.faked_cpcs.append(self.session.hmc.cpcs.add(FAKED_CPC_2))
        self.cpcs = self.client.cpcs.list()

    @pytest.mark.parametrize(
        "check_mode", [False, True])
    @mock.patch("plugins.modules.zhmc_cpc_list.AnsibleModule",
                autospec=True)
    def test_cpc_list(self, ansible_mod_cls, check_mode):
        """
        Tests for CPC list.
        """

        # Set some expectations for this test from its parametrization
        exp_changed = False
        exp_exit_code = 0

        # Prepare module input parameters
        params = {
            'hmc_host': 'fake-host',
            'hmc_auth': dict(userid='fake-userid',
                             password='fake-password'),
            'log_file': None,
            '_faked_session': self.session,
        }

        # Prepare mocks for AnsibleModule object
        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        # Exercise the code to be tested
        with pytest.raises(SystemExit) as exc_info:
            zhmc_cpc_list.main()
        exit_code = exc_info.value.args[0]

        # Assert module exit code
        assert exit_code == exp_exit_code, \
            "Module has unexpected exit code {0} (expected {1}). " \
            "Error message:\n{2}". \
            format(exit_code, exp_exit_code, get_failure_msg(mod_obj))

        # Assert module output
        changed, cpc_list = get_module_output(mod_obj)
        assert changed == exp_changed

        # Assert returned list of CPCs
        exp_managed_cpcs = self.client.cpcs.list()
        exp_unmanaged_cpcs = self.client.consoles.console.list_unmanaged_cpcs()
        managed_cpc_names = []
        unmanaged_cpc_names = []
        for cpc_props in cpc_list:
            assert 'name' in cpc_props
            assert 'is_managed' in cpc_props
            if cpc_props['is_managed']:
                managed_cpc_names.append(cpc_props['name'])
            else:
                unmanaged_cpc_names.append(cpc_props['name'])
        exp_managed_cpc_names = [cpc.name for cpc in exp_managed_cpcs]
        exp_unmanaged_cpc_names = [cpc.name for cpc in exp_unmanaged_cpcs]
        assert managed_cpc_names == exp_managed_cpc_names
        assert unmanaged_cpc_names == exp_unmanaged_cpc_names

        # Assert returned CPC properties
        for cpc_props in cpc_list:
            cpc_name = cpc_props['name']
            if cpc_props['is_managed']:
                exp_cpcs = [cpc for cpc in exp_managed_cpcs
                            if cpc.name == cpc_name]
            else:
                exp_cpcs = [cpc for cpc in exp_unmanaged_cpcs
                            if cpc.name == cpc_name]
            assert len(exp_cpcs) == 1
            exp_cpc = exp_cpcs[0]
            for pname, pvalue in cpc_props.items():
                if pname in ('is_managed',):
                    continue
                pname_hmc = pname.replace('_', '-')
                exp_value = exp_cpc.get_property(pname_hmc)
                assert pvalue == exp_value, \
                    "For property: {0!r}".format(pname)
