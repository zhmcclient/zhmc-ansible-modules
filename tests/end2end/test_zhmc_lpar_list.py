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
End2end tests for zhmc_lpar_list module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import mock
import requests.packages.urllib3
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
from zhmcclient.testutils import classic_mode_cpcs  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_lpar_list
from .utils import mock_ansible_module, get_failure_msg

requests.packages.urllib3.disable_warnings()

# Print debug messages
DEBUG = False

LOG_FILE = 'zhmc_lpar_list.log' if DEBUG else None


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, user_properties) (i.e.
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


def assert_lpar_list(lpar_list, cpc_name, se_version, exp_lpars_dict):
    """
    Assert the output of the zhmc_lpar_list module
    """

    assert isinstance(lpar_list, list)

    exp_lpar_names = list(exp_lpars_dict)
    assert len(lpar_list) == len(exp_lpar_names)

    for lpar_item in lpar_list:

        assert 'name' in lpar_item, \
            "Returned LPAR {ri!r} does not have a 'name' property". \
            format(ri=lpar_item)
        lpar_name = lpar_item['name']

        assert lpar_name in exp_lpars_dict, \
            "Result contains unexpected LPAR: {rn!r}". \
            format(rn=lpar_name)

        exp_lpar = exp_lpars_dict[lpar_name]

        for pname, pvalue in lpar_item.items():

            # Verify artificial properties
            if pname == 'cpc_name':
                assert pvalue == cpc_name
                continue
            if pname == 'se_version':
                assert pvalue == se_version
                continue

            # Verify normal properties
            pname_hmc = pname.replace('_', '-')
            assert pname_hmc in exp_lpar.properties, \
                "Unexpected property {pn!r} in result LPAR {rn!r}, expected properties: {ep!r}". \
                format(pn=pname_hmc, rn=lpar_name, ep=', '.join(exp_lpar.properties.keys()))
            exp_value = exp_lpar.properties[pname_hmc]
            assert pvalue == exp_value, \
                "Incorrect value for property {pn!r} of result LPAR {rn!r}". \
                format(pn=pname_hmc, rn=lpar_name)


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
@mock.patch("plugins.modules.zhmc_lpar_list.AnsibleModule", autospec=True)
def test_user_lpar_list(
        ansible_mod_cls, check_mode, with_cpc, classic_mode_cpcs):  # noqa: F811, E501
    """
    Test listing of LPARs of the classic mode CPCs on the HMC.
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

        client = zhmcclient.Client(session)
        console = client.consoles.console

        faked_session = session if hd.mock_file else None

        # Determine the expected LPARs on the HMC
        if with_cpc:
            filter_args = {'cpc-name': cpc.name}
            exp_lpars = console.list_permitted_lpars(filter_args=filter_args)
        else:
            exp_lpars = console.list_permitted_lpars()
        exp_lpars_dict = {}
        for lpar in exp_lpars:
            lpar.pull_full_properties()
            exp_lpars_dict[lpar.name] = lpar

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
            zhmc_lpar_list.main()
        exit_code = exc_info.value.args[0]

        # Assert module exit code
        assert exit_code == 0, \
            "Module failed with exit code {e} and message:\n{m}". \
            format(e=exit_code, m=get_failure_msg(mod_obj))

        # Assert module output
        changed, lpar_list = get_module_output(mod_obj)
        assert changed is False

        cpc_name = cpc.name
        se_version = cpc.get_property('se-version')
        assert_lpar_list(lpar_list, cpc_name, se_version, exp_lpars_dict)
