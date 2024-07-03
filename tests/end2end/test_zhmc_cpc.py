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
End2end tests for zhmc_cpc module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest import mock
import pytest
import urllib3
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
from zhmcclient.testutils import all_cpcs  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_cpc
from .utils import mock_ansible_module, get_failure_msg, setup_logging, \
    skip_warn

urllib3.disable_warnings()

DEBUG = False  # Print debug messages

# Logging for zhmcclient HMC interactions and test functions
LOGGING = False
LOG_FILE = 'test_zhmc_cpc.log' if LOGGING else None


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, cpc) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, cpc):
        return changed, cpc

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


CPC_FACTS_TESTCASES = [
    # The list items are tuples with the following items:
    # - desc (string): description of the testcase.
    # - select_properties (list): Input for select_properties module parm
    # - exp_prop_names (list): Names of expected properties in module
    #   result (HMC-formatted) in case of module success. The module may
    #   return more then those listed.
    # - not_prop_names (list): Names of unexpected properties in module
    #   result (HMC-formatted) in case of module success. The module must
    #   not return those listed.
    # - exp_msg (string): Expected message pattern in case of module failure,
    #   or None for module success.
    # - exp_changed (bool): Boolean for expected 'changed' flag.
    # - run: Indicates whether the test should be run, or 'pdb' for debugger.

    (
        "Default input parms = full properties",
        None,
        [
            'name',
            'object-uri',
            'description',
            'status',
            'dpm-enabled',
        ],
        [],
        None,
        False,
        True,
    ),
    (
        "select empty list of properties",
        [],
        [
            'name',             # always returned
            'object-uri',       # always returned
        ],
        [
            'description',
            'status',
            'dpm-enabled',
        ],
        None,
        False,
        True,
    ),
    (
        "select one property",
        ['description'],
        [
            'name',
            'object-uri',
            'description',
        ],
        [
            'status',
            'dpm-enabled',
        ],
        None,
        False,
        True,
    ),
    (
        "select two properties",
        ['description', 'status'],
        [
            'name',
            'object-uri',
            'description',
            'status',
        ],
        [
            'dpm-enabled',
        ],
        None,
        False,
        True,
    ),
    (
        "select property with underscore",
        ['dpm_enabled'],
        [
            'name',
            'object-uri',
        ],
        [
            'description',
            'status',
        ],
        None,
        False,
        True,
    ),
    (
        "select property with hyphen",
        ['dpm-enabled'],
        [
            'name',
            'object-uri',
        ],
        [
            'description',
            'status',
        ],
        None,
        False,
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
    "desc, select_properties, exp_prop_names, not_prop_names, "
    "exp_msg, exp_changed, run",
    CPC_FACTS_TESTCASES)
@mock.patch("plugins.modules.zhmc_cpc.AnsibleModule", autospec=True)
def test_zhmc_cpc_facts(
        ansible_mod_cls,
        desc, select_properties, exp_prop_names, not_prop_names,
        exp_msg, exp_changed, run,
        check_mode, all_cpcs):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name,unused-argument
    """
    Test the zhmc_cpc module with state=facts on any CPCs.
    """
    if not all_cpcs:
        pytest.skip("HMC definition does not include any CPCs")

    if not run:
        skip_warn("Testcase is disabled in testcase definition")

    setup_logging(LOGGING, 'test_zhmc_cpc_facts', LOG_FILE)

    for cpc in all_cpcs:

        session = cpc.manager.session
        hd = session.hmc_definition
        hmc_host = hd.host
        hmc_auth = dict(userid=hd.userid, password=hd.password,
                        ca_certs=hd.ca_certs, verify=hd.verify)

        faked_session = session if hd.mock_file else None

        where = f"CPC '{cpc.name}'"

        # Prepare module input parameters (must be all required + optional)
        params = {
            'hmc_host': hmc_host,
            'hmc_auth': hmc_auth,
            'name': cpc.name,
            'state': 'facts',
            'select_properties': select_properties,
            'activation_profile_name': None,
            'properties': None,
            'bundle_level': None,
            'upgrade_timeout': 10800,
            'accept_firmware': True,
            'log_file': LOG_FILE,
            '_faked_session': faked_session,
        }

        # Prepare mocks for AnsibleModule object
        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        # Exercise the code to be tested
        with pytest.raises(SystemExit) as exc_info:
            zhmc_cpc.main()
        exit_code = exc_info.value.args[0]

        # Assert module exit code
        assert exit_code == 0, \
            f"{where}: Module failed with exit code {exit_code} and " \
            f"message:\n{get_failure_msg(mod_obj)}"

        # Assert module output
        changed, cpc_properties = get_module_output(mod_obj)
        assert changed is False, \
            f"{where}: Module returned changed={changed}"

        # Check the presence and absence of properties in the result
        cpc_prop_names = list(cpc_properties.keys())
        for pname in exp_prop_names:
            assert pname in cpc_prop_names
        for pname in not_prop_names:
            assert pname not in cpc_prop_names
