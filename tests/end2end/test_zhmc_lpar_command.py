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
End2end tests for zhmc_lpar_command module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import random
import re
from unittest import mock
import pytest
import urllib3
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
from zhmcclient.testutils import classic_mode_cpcs  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_lpar_command
from .utils import mock_ansible_module, get_failure_msg

urllib3.disable_warnings()

LOGGING = False
LOG_FILE = 'zhmc_lpar_command.log' if LOGGING else None


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, messages) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, output):
        return changed, output

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


TESTCASES_ZHMC_LPAR_COMMAND = [
    # Testcases for test_zhmc_lpar_command(), each with these items:
    # * desc (str): Testcase description
    # * in_params (dict): Input parameters passed to module, except for
    #   hmc_host, hmc_auth, cpc, name, command, log_file.
    # * act_mode (str): LPAR activation-mode property, for selecting the LPAR
    # * os_type (str): LPAR os-type property, for selecting the LPAR
    # * command (str): Command to be executed
    # * exp_output (list): Expected command output lines, as a list of regexp

    (
        "Simple z/VM command",
        {
            'is_priority': False,
        },
        "zvm",
        "z/VM",
        "Q CPLEVEL",
        [
            ".* Q CPLEVEL",
            ".* z/VM Version .* Release .* service level .*",
            ".* Generated at .*",
            ".* IPL at .*",
        ]
    ),
    (
        "Simple z/OS command",
        {
            'is_priority': False,
        },
        "esa390",
        "z/OS",
        "D T",
        [
            "D T",
            "RESPONSE=GR1 .* TIME=.*",
            "RESPONSE=TIME=.* DATE=.*",
        ]
    ),
    # TODO: Find out how to deal with Linux password prompt
    # (
    #     "Simple Linux command",
    #     {
    #         'is_priority': False,
    #     },
    #     "linux",
    #     "Linux",
    #     "uname -a",
    #     [
    #         "uname -a",
    #         "Kernel Version .* s390x",
    #     ]
    # ),
]


@pytest.mark.parametrize(
    "desc, in_params, act_mode, os_type, command, exp_output",
    TESTCASES_ZHMC_LPAR_COMMAND
)
@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_lpar_command.AnsibleModule", autospec=True)
def test_zhmc_lpar_command(
        ansible_mod_cls, check_mode,
        desc, in_params, act_mode, os_type, command, exp_output,
        classic_mode_cpcs):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name,unused-argument
    """
    Test the zhmc_lpar_command module with classic mode CPCs.
    """
    if not classic_mode_cpcs:
        pytest.skip("HMC definition does not include any CPCs in classic mode")

    for cpc in classic_mode_cpcs:
        assert not cpc.dpm_enabled

        session = cpc.manager.session
        hd = session.hmc_definition
        hmc_host = hd.host
        hmc_auth = dict(userid=hd.userid, password=hd.password,
                        ca_certs=hd.ca_certs, verify=hd.verify)
        faked_session = session if hd.mock_file else None
        console = cpc.manager.console

        # Requires HMC 2.14.0 or later
        mode_lpars = console.list_permitted_lpars(
            filter_args={'cpc-name': cpc.name, 'activation-mode': act_mode},
            additional_properties=['os-type'])

        if not mode_lpars:
            pytest.skip(f"CPC {cpc.name} does not have any LPARs with "
                        f"activation mode {act_mode}")

        loaded_lpars = []
        for lpar in mode_lpars:
            lpar_status = lpar.get_property('status')
            if lpar_status in ('operating', 'exceptions'):
                loaded_lpars.append(lpar)

        if not loaded_lpars:
            pytest.skip(f"CPC {cpc.name} does not have any LPARs with "
                        f"activation mode {act_mode} in a loaded state")

        test_lpars = []
        for lpar in loaded_lpars:
            lpar_os_type = lpar.get_property('os-type')
            if lpar_os_type == os_type:
                test_lpars.append(lpar)

        test_lpar_names = [lpar.name for lpar in test_lpars]
        lpar = random.choice(test_lpars)
        print(f"Using LPAR {lpar.name} (from {', '.join(test_lpar_names)})")

        # Prepare module input parameters (must be all required + optional)
        params = {
            'hmc_host': hmc_host,
            'hmc_auth': hmc_auth,
            'cpc_name': cpc.name,
            'name': lpar.name,
            'command': command,
            'log_file': LOG_FILE,
            '_faked_session': faked_session,
        }
        params.update(in_params)

        # Prepare mocks for AnsibleModule object
        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        # Exercise the code to be tested
        with pytest.raises(SystemExit) as exc_info:
            zhmc_lpar_command.main()
        exit_code = exc_info.value.args[0]

        # Assert module exit code
        assert exit_code == 0, \
            f"Module failed with exit code {exit_code} and message:\n" \
            f"{get_failure_msg(mod_obj)}"

        # Assert module output
        changed, output = get_module_output(mod_obj)
        assert changed is True

        assert len(output) == len(exp_output), (
            "Unexpected number of lines in command output:\n"
            f"  Actual output lines:\n{output}\n"
            f"  Expected output lines (regexp):\n{exp_output}\n"
        )
        for i, line in enumerate(output):
            exp_regexp = f"^{exp_output[i]}$"
            assert re.match(exp_regexp, line), (
                f"Output line #{i} does not match expected regexp:\n"
                f"  Actual output line: {line}\n"
                f"  Expected output line (regexp): {exp_regexp}\n"
            )
