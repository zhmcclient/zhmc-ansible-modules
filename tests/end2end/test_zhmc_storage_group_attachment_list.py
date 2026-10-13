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
End2end tests for zhmc_storage_group_attachment_list module.
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

from plugins.modules import zhmc_storage_group_attachment_list
from .utils import mock_ansible_module, get_failure_msg

urllib3.disable_warnings()

# Print debug messages
DEBUG = False

LOG_FILE = 'zhmc_storage_group_attachment_list.log' if DEBUG else None


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


def assert_partition_list(partition_list, exp_partition_dict):
    """
    Assert the output of the zhmc_storage_group_attachment_list module.

    Parameters:

      partition_list(list): Result of zhmc_storage_group_attachment_list module,
        as a list of dicts of partition properties as documented (with
        underscores in their names).

      exp_partition_dict(dict): Expected partitions with their properties.
        Key: partition name.
        Value: Dict of expected partition properties (all with underscores in
        their names).
    """

    assert isinstance(partition_list, list)

    exp_len = len(exp_partition_dict)
    assert len(partition_list) == exp_len

    for partition_item in partition_list:

        assert 'name' in partition_item, (
            f"Returned partition item {partition_item!r} does not have a "
            "'name' property")
        part_name = partition_item['name']

        assert part_name in exp_partition_dict, \
            f"Result contains unexpected partition: {part_name!r}"

        exp_partition_properties = exp_partition_dict[part_name]

        for pname, pvalue in partition_item.items():

            assert '-' not in pname, (
                f"Property {pname!r} in partition {part_name!r} is "
                "returned with hyphens in the property name")

            assert pname in exp_partition_properties, (
                f"Unexpected property {pname!r} in partition {part_name!r}")

            exp_value = exp_partition_properties[pname]
            assert pvalue == exp_value, (
                f"Incorrect value for property {pname!r} of partition "
                f"{part_name!r}")


@pytest.mark.parametrize(
    "filter_args", [
        pytest.param({},
                     id="filter_args()"),
        pytest.param({'use_partition_name_filter': True},
                     id="filter_args(use_partition_name_filter=True)"),
        pytest.param({'use_partition_status_filter': True},
                     id="filter_args(use_partition_status_filter=True)"),
    ]
)
@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_storage_group_attachment_list.AnsibleModule",
            autospec=True)
def test_zhmc_storage_group_attachment_list(
        ansible_mod_cls, check_mode, filter_args,
        hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_storage_group_attachment_list module.
    """
    hd = hmc_session.hmc_definition
    hmc_host = hmc_session.host
    userid = hmc_session.userid
    password = hmc_session._password  # pylint: disable=protected-access
    ca_certs = hmc_session.verify_cert \
        if isinstance(hmc_session.verify_cert, str) else None
    verify = bool(hmc_session.verify_cert)
    hmc_auth = dict(userid=userid, password=password, ca_certs=ca_certs,
                    verify=verify)

    use_partition_name_filter = filter_args.get(
        'use_partition_name_filter', False)
    use_partition_status_filter = filter_args.get(
        'use_partition_status_filter', False)

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

    # Prepare the expected partition result
    filter_kwargs = {}
    if use_partition_name_filter:
        filter_kwargs['name'] = ".*"
    if use_partition_status_filter:
        filter_kwargs['status'] = "active"

    exp_partitions = picked_storage_group.list_attached_partitions(
        **filter_kwargs)
    exp_partition_dict = {}
    for part in exp_partitions:
        exp_properties = {'cpc_name': picked_cpc.name}
        for pname_hmc, pvalue in part.properties.items():
            pname = pname_hmc.replace('-', '_')
            exp_properties[pname] = pvalue
        exp_partition_dict[part.name] = exp_properties

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'cpc_name': picked_cpc.name,
        'name': picked_storage_group.name,
        'partition_name': filter_kwargs.get('name', None),
        'partition_status': filter_kwargs.get('status', None),
        'log_file': LOG_FILE,
        '_faked_session': faked_session,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_storage_group_attachment_list.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, \
        f"Module failed with exit code {exit_code} and message:\n" \
        f"{get_failure_msg(mod_obj)}"

    # Assert module output
    changed, partition_list = get_module_output(mod_obj)
    assert changed is False

    assert_partition_list(
        partition_list, exp_partition_dict)
