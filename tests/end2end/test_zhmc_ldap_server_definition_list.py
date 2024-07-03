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
End2end tests for zhmc_ldap_server_definition_list module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest import mock
import pytest
import urllib3
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_ldap_server_definition_list
from .utils import mock_ansible_module, get_failure_msg

urllib3.disable_warnings()

# Print debug messages
DEBUG = False

LOG_FILE = 'zhmc_ldap_server_definition_list.log' if DEBUG else None


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, user_properties) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, ldap_server_definitions):
        return changed, ldap_server_definitions

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_lsd_list(lsd_list, exp_lsd_dict):
    """
    Assert the output of the zhmc_ldap_server_definition_list module
    """
    assert isinstance(lsd_list, list)
    assert len(lsd_list) == len(exp_lsd_dict)
    for lsd_item in lsd_list:
        assert 'name' in lsd_item, \
            f"Returned LDAP server definition {lsd_item!r} does not have a " \
            "'name' property"
        lsd_name = lsd_item['name']
        assert lsd_name in exp_lsd_dict, \
            f"Unexpected returned LDAP server definition {lsd_name!r}"
        exp_lsd = exp_lsd_dict[lsd_name]
        for pname, pvalue in lsd_item.items():
            assert pname in exp_lsd.properties, \
                f"Unexpected property {pname!r} in LDAP server definition " \
                f"{lsd_name!r}"
            exp_value = exp_lsd.properties[pname]
            assert pvalue == exp_value, \
                f"Incorrect value for property {pname!r} of LDAP server " \
                f"definition {lsd_name!r}"


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_ldap_server_definition_list.AnsibleModule",
            autospec=True)
def test_zhmc_ldap_server_definition_list(
        ansible_mod_cls, check_mode, hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_ldap_server_definition_list module.
    """

    hd = hmc_session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    client = zhmcclient.Client(hmc_session)
    console = client.consoles.console

    faked_session = hmc_session if hd.mock_file else None

    # Determine the actual list of LDAP server definitions on the HMC.
    act_lsds = console.ldap_server_definitions.list()
    act_lsds_dict = {}
    for r in act_lsds:
        act_lsds_dict[r.name] = r

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'log_file': LOG_FILE,
        '_faked_session': faked_session,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_ldap_server_definition_list.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, \
        f"Module failed with exit code {exit_code} and message:\n" \
        f"{get_failure_msg(mod_obj)}"

    # Assert module output
    changed, lsd_list = get_module_output(mod_obj)
    assert changed is False

    assert_lsd_list(lsd_list, act_lsds_dict)
