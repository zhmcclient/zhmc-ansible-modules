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
End2end tests for zhmc_storage_volume_list module.
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

from plugins.modules import zhmc_storage_volume_list
from .utils import mock_ansible_module, get_failure_msg

urllib3.disable_warnings()

# Print debug messages
DEBUG = False

LOG_FILE = 'zhmc_storage_volume_list.log' if DEBUG else None


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, user_properties) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, storage_volumes):
        return changed, storage_volumes

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_storage_volume_list(
        storage_volume_list, exp_storage_volume_dict, storage_group_name):
    """
    Assert the output of the zhmc_storage_volume_list module.

    Parameters:

      storage_volume_list(list): Result of zhmc_storage_volume_list module, as a
        list of dicts of CPC properties as documented (with underscores in
        their names).

      exp_storage_volume_dict(dict): Expected storage volumes with their
        properties.
        Key: Storage volume name.
        Value: Dict of expected storage volume properties (including any
        artificial properties, all with underscores in their names).

      storage_group_name(str): Name of the storage group, for messages.
    """

    assert isinstance(storage_volume_list, list)

    sv_names = [sv.get('name', None) for sv in storage_volume_list]
    exp_sv_names = list(exp_storage_volume_dict.keys())

    exp_len = len(exp_storage_volume_dict)
    assert len(storage_volume_list) == exp_len, (
        "Unexpected number of volumes in storage group "
        f"{storage_group_name!r}:\n"
        f"Actual volumes: {sv_names!r}\n"
        f"Expected volumes: {exp_sv_names!r}\n"
    )

    for storage_volume_item in storage_volume_list:

        assert 'name' in storage_volume_item, (
            f"Returned storage volume item {storage_volume_item!r} in storage "
            f"group {storage_group_name!r} does not have a 'name' property")
        sv_name = storage_volume_item['name']

        assert sv_name in exp_storage_volume_dict, (
            f"Result for storage group {storage_group_name!r} contains "
            f"unexpected storage volume: {sv_name!r}")

        exp_storage_volume_properties = exp_storage_volume_dict[sv_name]

        for pname, pvalue in storage_volume_item.items():

            assert '-' not in pname, (
                f"Property {pname!r} in storage volume {sv_name!r} in storage "
                f"group {storage_group_name!r} is returned with hyphens in "
                "the property name")

            assert pname in exp_storage_volume_properties, (
                f"Unexpected property {pname!r} in storage volume "
                f"{sv_name!r} in storage group {storage_group_name!r}")

            exp_value = exp_storage_volume_properties[pname]
            assert pvalue == exp_value, (
                f"Incorrect value for property {pname!r} of storage volume "
                f"{sv_name!r} in storage group {storage_group_name!r}")


@pytest.mark.parametrize(
    "property_args", [
        pytest.param({}, id="property_args()"),
        pytest.param({'full_properties': True},
                     id="property_args(full_properties=True)"),
        pytest.param({'additional_properties': ['uuid']},
                     id="property_args(additional_properties=[uuid])"),
    ]
)
@pytest.mark.parametrize(
    "filter_args", [
        pytest.param({'use_name_filter': True},
                     id="filter_args(use_name_filter=True)"),
        pytest.param({'fulfillment_state': 'complete'},
                     id="filter_args(fulfillment_state=complete)"),
        pytest.param({'maximum_size': 500},
                     id="filter_args(maximum_size=500)"),
        pytest.param({'minimum_size': 10},
                     id="filter_args(minimum_size=10)"),
        pytest.param({'usage': 'boot'},
                     id="filter_args(usage=boot)"),
    ]
)
@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_storage_volume_list.AnsibleModule",
            autospec=True)
def test_zhmc_storage_volume_list(
        ansible_mod_cls, check_mode, filter_args, property_args,
        hmc_session):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_storage_volume_list module.
    """

    hd = hmc_session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    # Get the module arguments for the test.
    # We need to use the defaults defined in the module argument spec
    full_properties = property_args.get('full_properties', False)
    additional_properties = property_args.get('additional_properties', [])
    fulfillment_state = filter_args.get('fulfillment_state', None)
    maximum_size = filter_args.get('maximum_size', None)
    minimum_size = filter_args.get('minimum_size', None)
    usage = filter_args.get('usage', None)

    use_name_filter = filter_args.get('use_name_filter', False)

    client = zhmcclient.Client(hmc_session)
    console = client.consoles.console

    faked_session = hmc_session if hd.mock_file else None

    # Pick a random storage group as a target for the test
    all_storage_groups = console.storage_groups.list()
    if len(all_storage_groups) == 0:
        pytest.skip("This HMC has no storage groups")
    picked_storage_group = random.choice(all_storage_groups)

    # Pick a random storage volume for the volume name filtering
    if use_name_filter:
        all_storage_volumes = picked_storage_group.storage_volumes.list()
        if len(all_storage_volumes) == 0 and use_name_filter:
            pytest.skip(f"Storage group {picked_storage_group.name} picked "
                        "for the test has no volumes")
        picked_storage_volume = random.choice(all_storage_volumes)
        picked_storage_volume_name = picked_storage_volume.name
    else:
        picked_storage_volume_name = None

    filter_args = {}
    if use_name_filter:
        filter_args['name'] = picked_storage_volume_name
    if fulfillment_state:
        filter_args['fulfillment-state'] = fulfillment_state
    if maximum_size:
        filter_args['maximum-size'] = maximum_size
    if minimum_size:
        filter_args['minimum-size'] = minimum_size
    if usage:
        filter_args['usage'] = usage
    exp_storage_volumes = picked_storage_group.storage_volumes.list(
        filter_args=filter_args,
        full_properties=full_properties,
        additional_properties=additional_properties)
    exp_storage_volume_dict = {}
    for storage_volume in exp_storage_volumes:
        exp_properties = {}
        for pname_hmc, pvalue in storage_volume.properties.items():
            pname = pname_hmc.replace('-', '_')
            exp_properties[pname] = pvalue
        exp_storage_volume_dict[storage_volume.name] = exp_properties

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'storage_group_name': picked_storage_group.name,
        'name': picked_storage_volume_name,
        'fulfillment_state': fulfillment_state,
        'maximum_size': maximum_size,
        'minimum_size': minimum_size,
        'usage': usage,
        'full_properties': full_properties,
        'additional_properties': additional_properties,
        'log_file': LOG_FILE,
        '_faked_session': faked_session,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_storage_volume_list.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, \
        f"Module failed with exit code {exit_code} and message:\n" \
        f"{get_failure_msg(mod_obj)}"

    # Assert module output
    changed, storage_volume_list = get_module_output(mod_obj)
    assert changed is False

    assert_storage_volume_list(
        storage_volume_list, exp_storage_volume_dict,
        picked_storage_group.name)
