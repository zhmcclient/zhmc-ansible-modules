# Copyright 2026 IBM Corp. All Rights Reserved.
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
End2end tests for zhmc_storage_group_list module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import random
from unittest import mock
import pytest
import urllib3
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_storage_group_list
from .utils import mock_ansible_module, get_failure_msg

urllib3.disable_warnings()

# Print debug messages
DEBUG = False

LOG_FILE = 'zhmc_storage_group_list.log' if DEBUG else None


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, user_properties) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, storage_groups):
        return changed, storage_groups

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_storage_group_list(storage_group_list, exp_storage_group_dict):
    """
    Assert the output of the zhmc_storage_group_list module.

    Parameters:

      storage_group_list(list): Result of zhmc_storage_group_list module, as a
        list of dicts of CPC properties as documented (with underscores in
        their names).

      exp_storage_group_dict(dict): Expected storage groups with their
        properties.
        Key: Storage group name.
        Value: Dict of expected storage group properties (including any
        artificial properties, all with underscores in their names).
    """

    assert isinstance(storage_group_list, list)

    exp_len = len(exp_storage_group_dict)
    assert len(storage_group_list) == exp_len

    for storage_group_item in storage_group_list:

        assert 'name' in storage_group_item, (
            f"Returned storage group item {storage_group_item!r} does not "
            "have a 'name' property")
        sg_name = storage_group_item['name']

        assert sg_name in exp_storage_group_dict, \
            f"Result contains unexpected storage group: {sg_name!r}"

        exp_storage_group_properties = exp_storage_group_dict[sg_name]

        for pname, pvalue in storage_group_item.items():

            assert '-' not in pname, (
                f"Property {pname!r} in storage group {sg_name!r} is "
                "returned with hyphens in the property name")

            assert pname in exp_storage_group_properties, (
                f"Unexpected property {pname!r} in storage group "
                f"{sg_name!r}")

            exp_value = exp_storage_group_properties[pname]
            assert pvalue == exp_value, (
                f"Incorrect value for property {pname!r} of storage group "
                f"{sg_name!r}")


@pytest.mark.parametrize(
    "property_args", [
        pytest.param({}, id="property_args()"),
        pytest.param({'full_properties': True},
                     id="property_args(full_properties=True)"),
    ]
)
@pytest.mark.parametrize(
    "filter_args", [
        pytest.param({'use_name_filter': True},
                     id="filter_args(use_name_filter=True)"),
        pytest.param({'use_cpc_name_filter': True},
                     id="filter_args(use_cpc_name_filter=True)"),
        pytest.param({'type': 'fcp'},
                     id="filter_args(type=fcp)"),
        pytest.param({'fulfillment_state': 'complete'},
                     id="filter_args(fulfillment_state=complete)"),
    ]
)
@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_storage_group_list.AnsibleModule",
            autospec=True)
def test_zhmc_storage_group_list(
        ansible_mod_cls, check_mode, filter_args, property_args,
        hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_storage_group_list module.
    """

    hd = hmc_session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    # Get the module arguments for the test.
    # We need to use the defaults defined in the module argument spec
    full_properties = property_args.get('full_properties', False)
    type = filter_args.get('type', None)
    fulfillment_state = filter_args.get('fulfillment_state', None)

    use_name_filter = filter_args.get('use_name_filter', False)
    use_cpc_name_filter = filter_args.get('use_cpc_name_filter', False)

    client = zhmcclient.Client(hmc_session)
    console = client.consoles.console

    faked_session = hmc_session if hd.mock_file else None

    cpcs = client.cpcs.list()
    cpc_by_uri = {cpc.uri: cpc for cpc in cpcs}

    # Pick a random storage group and its associated CPC
    all_storage_groups = console.storage_groups.list()
    if len(all_storage_groups) == 0:
        pytest.skip("This HMC has no storage groups")
    picked_storage_group = random.choice(all_storage_groups)
    picked_cpc_uri = picked_storage_group.get_property('cpc-uri')
    picked_cpc = cpc_by_uri[picked_cpc_uri]

    # Prepare the expected storage group result
    filter_args = {}
    if use_cpc_name_filter:
        filter_args['cpc-uri'] = picked_cpc_uri
    if use_name_filter:
        filter_args['name'] = picked_storage_group.name
    if type:
        filter_args['type'] = type
    if fulfillment_state:
        filter_args['fulfillment-state'] = fulfillment_state
    exp_storage_groups = console.storage_groups.list(
        filter_args=filter_args, full_properties=full_properties)
    exp_storage_group_dict = {}
    for storage_group in exp_storage_groups:
        cpc_uri = storage_group.get_property('cpc-uri')
        cpc_name = cpc_by_uri[cpc_uri].get_property('name')
        exp_properties = {'cpc_name': cpc_name}
        for pname_hmc, pvalue in storage_group.properties.items():
            pname = pname_hmc.replace('-', '_')
            exp_properties[pname] = pvalue
        exp_storage_group_dict[storage_group.name] = exp_properties

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'name': picked_storage_group.name if use_name_filter else None,
        'cpc_name': picked_cpc.name if use_cpc_name_filter else None,
        'type': type,
        'fulfillment_state': fulfillment_state,
        'full_properties': full_properties,
        'log_file': LOG_FILE,
        '_faked_session': faked_session,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_storage_group_list.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, \
        f"Module failed with exit code {exit_code} and message:\n" \
        f"{get_failure_msg(mod_obj)}"

    # Assert module output
    changed, storage_group_list = get_module_output(mod_obj)
    assert changed is False

    assert_storage_group_list(
        storage_group_list, exp_storage_group_dict)
