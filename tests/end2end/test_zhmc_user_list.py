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
End2end tests for zhmc_user_list module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import mock
import requests.packages.urllib3
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_user_list
from .utils import mock_ansible_module, get_failure_msg

requests.packages.urllib3.disable_warnings()

# Print debug messages
DEBUG = False

LOG_FILE = 'zhmc_user_list.log' if DEBUG else None


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, user_properties) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, users):
        return changed, users

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_user_list(user_list, exp_user_dict):
    """
    Assert the output of the zhmc_user_list module
    """
    assert isinstance(user_list, list)
    assert len(user_list) == len(exp_user_dict)
    for user_item in user_list:
        assert 'name' in user_item, \
            "Returned user {i!r} does not have a 'name' property". \
            format(i=user_item)
        user_name = user_item['name']
        assert user_name in exp_user_dict, \
            "Unexpected returned user {n!r}". \
            format(n=user_name)
        exp_user = exp_user_dict[user_name]
        for pname, pvalue in user_item.items():
            assert pname in exp_user.properties, \
                "Unexpected property {pn!r} in user {n!r}". \
                format(pn=pname, n=user_name)
            exp_value = exp_user.properties[pname]
            assert pvalue == exp_value, \
                "Incorrect value for property {pn!r} of user {n!r}". \
                format(pn=pname, n=user_name)


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_user_list.AnsibleModule",
            autospec=True)
def test_zhmc_user_list(
        ansible_mod_cls, check_mode, hmc_session):  # noqa: F811, E501
    """
    Test the zhmc_user_list module.
    """

    hd = hmc_session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    client = zhmcclient.Client(hmc_session)
    console = client.consoles.console

    faked_session = hmc_session if hd.mock_file else None

    # Determine the actual list of users on the HMC.
    act_users = console.users.list()
    act_users_dict = {}
    for user in act_users:
        act_users_dict[user.name] = user

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
        zhmc_user_list.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, \
        "Module failed with exit code {e} and message:\n{m}". \
        format(e=exit_code, m=get_failure_msg(mod_obj))

    # Assert module output
    changed, user_list = get_module_output(mod_obj)
    assert changed is False

    assert_user_list(user_list, act_users_dict)
