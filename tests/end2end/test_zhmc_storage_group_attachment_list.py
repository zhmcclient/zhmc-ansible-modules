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
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_storage_group_attachment_list
from .utils import mock_ansible_module, get_failure_msg, available_dpm_cpcs, \
    underscored_properties
from .conftest import LOG_FILE


# Names of partition properties (with underscores) that are volatile, i.e. that
# may change their values on subsequent retrievals even when no other change is
# performed.
VOLATILE_PARTITION_PROPERTIES = [
    'power_wattage',
]


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, partitions)
    (i.e. the arguments of the call to exit_json()).
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


def assert_partition_list(act_partition_list, exp_partition_dict):
    """
    Assert the output of the zhmc_password_rule_list module.

    Parameters:

      act_partition_list (list of dict): Actual result of the module,
        as a list of properties (name: value), including any artificial
        properties. The property names must be as returned by the module.

      exp_partition_dict (dict of dict): Expected properties,
        as a dict (key: properties) where key is the object name and properties
        is a dict (name: value), including any artificial properties. The
        property names must be as returned by the zhmcclient list method.
        (i.e. with hyphens).
    """
    assert isinstance(act_partition_list, list)
    assert isinstance(exp_partition_dict, dict)

    assert len(act_partition_list) == len(exp_partition_dict), (
        "Unexpected number of partitions:\n"
        f"Actual objects: {act_partition_list!r}\n"
        f"Expected objects: {exp_partition_dict!r}\n"
    )
    for act_partition_properties in act_partition_list:
        assert isinstance(act_partition_properties, dict)

        # Check for the key property
        assert 'name' in act_partition_properties, (
            "Returned partition does not have a 'name' "
            f"property: {act_partition_properties!r}")
        partition_name = act_partition_properties['name']
        assert partition_name in exp_partition_dict, (
            f"Unexpected returned partition {partition_name!r}")

        exp_partition_properties = exp_partition_dict[partition_name]
        assert isinstance(exp_partition_properties, dict)
        exp_partition_properties = underscored_properties(exp_partition_properties)

        exp_partition_pnames = list(exp_partition_properties.keys())
        act_partition_pnames = list(act_partition_properties.keys())

        # Check the actually returned objects against the expected properties.
        # This discovers unexpected properties.
        for pname, act_value in act_partition_properties.items():
            assert '-' not in pname, (
                f"Property {pname!r} in returned "
                f"partition {partition_name!r} "
                "has hyphens in the property name")
            assert pname in exp_partition_properties, (
                f"Unexpected property {pname!r} in returned "
                f"partition {partition_name!r}:\n"
                f"Expected properties: {exp_partition_pnames}\n"
                f"Actual properties: {act_partition_pnames}")
            if pname not in VOLATILE_PARTITION_PROPERTIES:
                exp_value = exp_partition_properties[pname]
                assert act_value == exp_value, (
                    f"Incorrect value for property {pname!r} of returned "
                    f"partition {partition_name!r}:\n"
                    f"Expected value: {exp_value!r}\n"
                    f"Actual value: {act_value!r}")

        # Check the expected properties against the actually returned objects.
        # This discovers missing properties.
        for pname, exp_value in exp_partition_properties.items():
            assert pname in act_partition_properties, (
                f"Missing property {pname!r} in returned "
                f"partition {partition_name!r}:\n"
                f"Expected properties: {exp_partition_pnames}\n"
                f"Actual properties: {act_partition_pnames}")
            if pname not in VOLATILE_PARTITION_PROPERTIES:
                act_value = act_partition_properties[pname]
                assert act_value == exp_value, (
                    f"Incorrect value for property {pname!r} of returned "
                    f"partition {partition_name!r}:\n"
                    f"Expected value: {exp_value!r}\n"
                    f"Actual value: {act_value!r}")


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
    password = hmc_session.password
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

    # The testcases require that the CPC associated with the storage group
    # is available. Skip this test if there is no available DPM mode CPC.
    cpcs = available_dpm_cpcs(client.cpcs.list())
    if not cpcs:
        pytest.skip("No available DPM mode CPCs")

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
        exp_properties = {
            'cpc_name': picked_cpc.name,
            'cpc_uri': picked_cpc.uri,
        }
        exp_properties.update(part.properties)
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

    assert_partition_list(partition_list, exp_partition_dict)
