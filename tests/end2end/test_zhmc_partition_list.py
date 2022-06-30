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
End2end tests for zhmc_partition_list module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import mock
import requests.packages.urllib3
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
from zhmcclient.testutils import dpm_mode_cpcs  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_partition_list
from .utils import mock_ansible_module, get_failure_msg

requests.packages.urllib3.disable_warnings()

# Print debug messages
DEBUG = False

LOG_FILE = 'zhmc_partition_list.log' if DEBUG else None


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, user_properties) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, partitions):
        return changed, partitions

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_partition_list(
        partition_list, cpc_name, se_version, exp_partitions_dict):
    """
    Assert the output of the zhmc_partition_list module
    """

    assert isinstance(partition_list, list)

    exp_partition_names = list(exp_partitions_dict)
    assert len(partition_list) == len(exp_partition_names)

    for partition_item in partition_list:

        assert 'name' in partition_item, \
            "Returned partition {ri!r} does not have a 'name' property". \
            format(ri=partition_item)
        partition_name = partition_item['name']

        assert partition_name in exp_partitions_dict, \
            "Result contains unexpected partition: {rn!r}". \
            format(rn=partition_name)

        exp_partition = exp_partitions_dict[partition_name]

        for pname, pvalue in partition_item.items():

            # Verify artificial properties
            if pname == 'cpc_name':
                assert pvalue == cpc_name
                continue
            if pname == 'se_version':
                assert pvalue == se_version
                continue

            # Verify normal properties
            pname_hmc = pname.replace('_', '-')
            assert pname_hmc in exp_partition.properties, \
                "Unexpected property {pn!r} in result partition {rn!r}". \
                format(pn=pname_hmc, rn=partition_name)
            exp_value = exp_partition.properties[pname_hmc]
            assert pvalue == exp_value, \
                "Incorrect value for property {pn!r} of result partition " \
                "{rn!r}". \
                format(pn=pname_hmc, rn=partition_name)


@pytest.mark.parametrize(
    "with_cpc", [
        pytest.param(False, id="with_cpc=False"),
        pytest.param(True, id="with_cpc=True"),
    ]
)
@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_partition_list.AnsibleModule", autospec=True)
def test_user_partition_list(
        ansible_mod_cls, check_mode, with_cpc, dpm_mode_cpcs):  # noqa: F811, E501
    """
    Test listing of partitions of the DPM mode CPCs on the HMC.
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

        client = zhmcclient.Client(session)
        console = client.consoles.console

        faked_session = session if hd.mock_file else None

        # Determine the expected partitions on the HMC
        if with_cpc:
            filter_args = {'cpc-name': cpc.name}
            exp_partitions = console.list_permitted_partitions(
                filter_args=filter_args)
        else:
            exp_partitions = console.list_permitted_partitions()
        exp_partitions_dict = {}
        for partition in exp_partitions:
            partition.pull_full_properties()
            exp_partitions_dict[partition.name] = partition

        # Prepare module input parameters (must be all required + optional)
        params = {
            'hmc_host': hmc_host,
            'hmc_auth': hmc_auth,
            'log_file': LOG_FILE,
            '_faked_session': faked_session,
        }
        if with_cpc:
            params['cpc_name'] = cpc.name

        # Prepare mocks for AnsibleModule object
        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        # Exercise the code to be tested
        with pytest.raises(SystemExit) as exc_info:
            zhmc_partition_list.main()
        exit_code = exc_info.value.args[0]

        # Assert module exit code
        assert exit_code == 0, \
            "Module failed with exit code {e} and message:\n{m}". \
            format(e=exit_code, m=get_failure_msg(mod_obj))

        # Assert module output
        changed, partition_list = get_module_output(mod_obj)
        assert changed is False

        cpc_name = cpc.name
        se_version = cpc.get_property('se-version')
        assert_partition_list(
            partition_list, cpc_name, se_version, exp_partitions_dict)
