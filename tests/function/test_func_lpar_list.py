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
Function tests for the 'zhmc_lpar_list' Ansible module.
"""

# pylint: disable=bad-option-value,redundant-u-string-prefix

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import mock

from zhmcclient import Client
from zhmcclient_mock import FakedSession

from plugins.modules import zhmc_lpar_list

from .func_utils import mock_ansible_module

# Faked Console that is used for all tests
# (with property names as specified in HMC data model)
# It must have at least the minimum required HMC version 2.14.0.
FAKED_CONSOLE_NAME = 'faked-hmc-name'
FAKED_CONSOLE_HMC_VERSION = '2.14.0'
FAKED_CONSOLE_API_VERSION = '2.20'
FAKED_CONSOLE_URI = '/api/console'
FAKED_CONSOLE = {
    'object-uri': FAKED_CONSOLE_URI,
    'class': 'console',
    'name': FAKED_CONSOLE_NAME,
    'description': 'Console HMC1',
    'version': FAKED_CONSOLE_HMC_VERSION,
}

# FakedSession() init arguments
FAKED_SESSION_KWARGS = dict(
    host='fake-host',
    hmc_name=FAKED_CONSOLE_NAME,
    hmc_version=FAKED_CONSOLE_HMC_VERSION,
    api_version=FAKED_CONSOLE_API_VERSION,
)

# Faked CPC in classic mode.
# (with property names as specified in HMC data model)
# Note that its SE version may be older than the minimum required HMC version.
FAKED_CPC_1_NAME = 'cpc-name-1'
FAKED_CPC_1_OID = 'fake-cpc-1'
FAKED_CPC_1_URI = '/api/cpcs/' + FAKED_CPC_1_OID
FAKED_CPC_1 = {
    'object-id': FAKED_CPC_1_OID,
    'object-uri': FAKED_CPC_1_URI,
    'class': 'cpc',
    'name': FAKED_CPC_1_NAME,
    'description': 'CPC #1 in classic mode',
    'status': 'active',
    'dpm-enabled': True,
    'is-ensemble-member': False,
    'iml-mode': 'esa390',
    'se-version': '2.13.0',
    'has-unacceptable-status': False,
}

# Faked LPAR that is used for these tests.
# The LPAR is an SSC type LPAR with a small subset of properties.
FAKED_LPAR_1_NAME = 'LPAR1'
FAKED_LPAR_1_OID = 'fake-lpar1'
FAKED_LPAR_1_URI = '/api/logical-partitions/' + FAKED_LPAR_1_OID
FAKED_LPAR_1 = {
    'object-id': FAKED_LPAR_1_OID,
    'object-uri': FAKED_LPAR_1_URI,
    'parent': FAKED_CPC_1_URI,
    'class': 'logical-partition',
    'name': FAKED_LPAR_1_NAME,
    'description': 'Lpar #1',
    'acceptable-status': ['operating'],
    'status': ['operating'],
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
    Return the module output as a tuple (changed, lpars) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, lpars):
        return changed, lpars

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


class TestLparList(object):
    """
    All tests for LPAR List.
    """

    def setup_method(self):
        """
        Using the zhmcclient mock support, set up a CPC.
        """
        self.session = FakedSession(**FAKED_SESSION_KWARGS)
        self.client = Client(self.session)
        self.console = self.session.hmc.consoles.add(FAKED_CONSOLE)
        self.faked_cpc = self.session.hmc.cpcs.add(FAKED_CPC_1)
        self.cpc = self.client.cpcs.find_by_name(FAKED_CPC_1_NAME)
        self.faked_lpars = []
        self.faked_lpars.append(self.session.hmc.cpcs.add(FAKED_LPAR_1))

    @pytest.mark.parametrize(
        "check_mode", [False, True])
    @pytest.mark.parametrize(
        "cpc_name", [None, FAKED_CPC_1_NAME])
    @mock.patch("plugins.modules.zhmc_lpar_list.AnsibleModule",
                autospec=True)
    def test_lpar_list(self, ansible_mod_cls, cpc_name, check_mode):
        """
        Tests for LPAR list.
        """

        # Set some expectations for this test from its parametrization
        exp_changed = False
        exp_exit_code = 0

        # Prepare module input parameters
        params = {
            'hmc_host': 'fake-host',
            'hmc_auth': dict(userid='fake-userid',
                             password='fake-password'),
            'cpc_name': cpc_name,
            'log_file': None,
            '_faked_session': self.session,
        }

        # Prepare mocks for AnsibleModule object
        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        # Exercise the code to be tested
        with pytest.raises(SystemExit) as exc_info:
            zhmc_lpar_list.main()
        exit_code = exc_info.value.args[0]

        # Assert module exit code
        assert exit_code == exp_exit_code, \
            "Module has unexpected exit code {0} (expected {1}). " \
            "Error message:\n{2}". \
            format(exit_code, exp_exit_code, get_failure_msg(mod_obj))

        # Assert module output
        changed, lpar_list = get_module_output(mod_obj)
        assert changed == exp_changed

        # Assert returned list of LPARs
        exp_lpars = self.cpc.lpars.list()
        lpar_names = []
        for lpar_props in lpar_list:
            assert 'name' in lpar_props
            lpar_names.append(lpar_props['name'])
        exp_lpar_names = [lpar.name for lpar in exp_lpars]
        assert lpar_names == exp_lpar_names

        # Assert returned LPAR properties
        for lpar_props in lpar_list:
            lpar_name = lpar_props['name']
            exp_lpars_1 = [lpar for lpar in exp_lpars
                           if lpar.name == lpar_name]
            assert len(exp_lpars_1) == 1
            exp_lpar = exp_lpars_1[0]
            for pname, pvalue in lpar_props.items():
                pname_hmc = pname.replace('_', '-')
                exp_value = exp_lpar.get_property(pname_hmc)
                assert pvalue == exp_value, \
                    "For property: {0!r}".format(pname)
