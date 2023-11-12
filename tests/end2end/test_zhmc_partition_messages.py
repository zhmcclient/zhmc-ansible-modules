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
End2end tests for zhmc_partition_messages module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import random
import pytest
import mock
import requests.packages.urllib3
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
from zhmcclient.testutils import dpm_mode_cpcs  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_partition_messages
from .utils import mock_ansible_module, get_failure_msg

requests.packages.urllib3.disable_warnings()

LOGGING = False
LOG_FILE = 'zhmc_partition_messages.log' if LOGGING else None


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, messages) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, messages):
        return changed, messages

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


TESTCASES_ZHMC_PARTITION_MESSAGES = [
    # Testcases for test_zhmc_partition_messages(), each with these items:
    # * desc (str): Testcase description
    # * in_params (dict): Input parameters passed to module, except for
    #   hmc_host, hmc_auth, cpc, name, log_file.
    # * exp_seqnos (dict): Expected message sequence numbers, if success,
    #   or None for no checking

    (
        "Messages unfiltered",
        {
            'begin': None,
            'end': None,
        },
        None
    ),
]


@pytest.mark.parametrize(
    "desc, in_params, exp_seqnos",
    TESTCASES_ZHMC_PARTITION_MESSAGES
)
@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_partition_messages.AnsibleModule", autospec=True)
def test_zhmc_partition_messages(
        ansible_mod_cls, check_mode,
        desc, in_params, exp_seqnos,
        dpm_mode_cpcs):  # noqa: F811, E501
    """
    Test the zhmc_partition_messages module with DPM mode CPCs.
    """
    if not dpm_mode_cpcs:
        pytest.skip("HMC definition does not include any CPCs in DPM mode")

    for cpc in dpm_mode_cpcs:
        assert cpc.dpm_enabled

        session = cpc.manager.session
        hd = session.hmc_definition
        hmc_host = hd.host
        hmc_auth = dict(userid=hd.userid, password=hd.password,
                        ca_certs=hd.ca_certs, verify=hd.verify)
        faked_session = session if hd.mock_file else None

        parts = cpc.partitions.list()
        active_parts = []
        for part in parts:
            part_status = part.get_property('status')
            if part_status in ('active', 'degraded'):
                active_parts.append(part)

        if not active_parts:
            pytest.skip("CPC {c} does not have any partitions in an active "
                        "state".format(c=cpc.name))

        part = random.choice(active_parts)

        # Prepare module input parameters (must be all required + optional)
        params = {
            'hmc_host': hmc_host,
            'hmc_auth': hmc_auth,
            'cpc_name': cpc.name,
            'name': part.name,
            'log_file': LOG_FILE,
            '_faked_session': faked_session,
        }
        params.update(in_params)

        # Prepare mocks for AnsibleModule object
        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        # Exercise the code to be tested
        with pytest.raises(SystemExit) as exc_info:
            zhmc_partition_messages.main()
        exit_code = exc_info.value.args[0]

        # Assert module exit code
        assert exit_code == 0, \
            "Module failed with exit code {e} and message:\n{m}". \
            format(e=exit_code, m=get_failure_msg(mod_obj))

        # Assert module output
        changed, messages = get_module_output(mod_obj)
        assert changed is False

        if exp_seqnos is not None:
            seqnos = [m['sequence_number'] for m in messages]
            assert len(seqnos) == len(exp_seqnos), (
                "Unexpected number of messages:\n"
                "  Actual sequence numbers: {asn}\n"
                "  Expected sequence numbers: {esn}\n".
                format(asn=seqnos, esn=exp_seqnos)
            )
            for i, message in enumerate(messages):
                exp_seqno = exp_seqnos[i]
                seqno = message['sequence_number']
                assert seqno == exp_seqno, (
                    "Unexpected sequence number:\n"
                    "  Actual sequence numbers: {asn}\n"
                    "  Expected sequence numbers: {esn}\n".
                    format(asn=seqnos, esn=exp_seqnos)
                )
