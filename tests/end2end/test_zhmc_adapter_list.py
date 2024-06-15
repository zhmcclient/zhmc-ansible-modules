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
End2end tests for zhmc_adapter_list module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
from unittest import mock
import requests.packages.urllib3
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
from zhmcclient.testutils import dpm_mode_cpcs  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_adapter_list
from .utils import mock_ansible_module, get_failure_msg

requests.packages.urllib3.disable_warnings()

# Print debug messages
DEBUG = False

LOG_FILE = 'zhmc_adapter_list.log' if DEBUG else None


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, user_properties) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, adapters):
        return changed, adapters

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_adapter_list(adapter_list, exp_adapter_dict):
    """
    Assert the output of the zhmc_adapter_list module

    Parameters:

      adapter_list(list): Result of zhmc_adapter_list module, as a list of
        dicts of adapter properties as documented (with underscores in their
        names).

      exp_adapter_dict(dict): Expected adapters with their properties.
        Key: tuple(CPC name, adapter ID).
        Value: Dict of expected adapter properties (including any artificial
        properties, all with underscores in their names).
    """

    assert isinstance(adapter_list, list)

    exp_cpc_adapter_keys = list(exp_adapter_dict.keys())
    cpc_adapter_keys = [(a.get('cpc_name', None), a.get('adapter_id', None))
                        for a in adapter_list]
    assert set(cpc_adapter_keys) == set(exp_cpc_adapter_keys)

    for adapter_item in adapter_list:
        adapter_id = adapter_item.get('adapter_id', None)
        cpc_name = adapter_item.get('cpc_name', None)
        cpc_adapter_key = (cpc_name, adapter_id)

        assert adapter_id is not None, \
            f"Returned adapter {adapter_item!r} does not have an " \
            "'adapter_id' property"

        assert cpc_adapter_key in exp_adapter_dict, \
            f"Result contains unexpected adapter ID {adapter_id!r} in CPC " \
            f"{cpc_name!r}"

        exp_adapter_properties = exp_adapter_dict[cpc_adapter_key]
        for pname, pvalue in adapter_item.items():
            assert '-' not in pname, \
                f"Property {pname!r} in adapter ID {adapter_id!r} is " \
                "returned with hyphens in the property name"
            assert pname in exp_adapter_properties, \
                f"Unexpected property {pname!r} in result adapter ID " \
                f"{adapter_id!r}"
            exp_value = exp_adapter_properties[pname]
            assert pvalue == exp_value, \
                f"Incorrect value for property {pname!r} of result adapter " \
                f"ID {adapter_id!r}"


@pytest.mark.parametrize(
    "with_cpc", [
        pytest.param(False, id="with_cpc=False"),
        pytest.param(True, id="with_cpc=True"),
    ]
)
@pytest.mark.parametrize(
    "filters", [  # These are Ansible module parameters, using underscores
        pytest.param(None, id="filters(None)"),
        pytest.param({'type': 'osd'}, id="filters(type=osd)"),
        pytest.param({'adapter_family': 'osa'}, id="filters(family=osa)"),
        pytest.param({'name': '.*'}, id="filters(name=.*)"),
    ]
)
@pytest.mark.parametrize(
    "property_flags", [
        pytest.param({}, id="property_flags()"),
        pytest.param({'additional_properties': ['description']},
                     id="property_flags(additional_properties=[description])"),
        pytest.param({'full_properties': True},
                     id="property_flags(full_properties=True)"),
    ]
)
@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_adapter_list.AnsibleModule", autospec=True)
def test_zhmc_adapter_list(
        ansible_mod_cls, check_mode, property_flags, filters, with_cpc,
        dpm_mode_cpcs):  # noqa: F811, E501
    """
    Test the zhmc_adapter_list module with DPM mode CPCs.
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

        full_properties = property_flags.get('full_properties', False)
        additional_properties = property_flags.get(
            'additional_properties', [])

        # Determine the expected adapters on the HMC
        if DEBUG:
            print("Debug: Listing expected adapters")
        av = client.query_api_version()
        hmc_version_info = [int(x) for x in av['hmc-version'].split('.')]
        api_version_info = [av['api-major-version'], av['api-minor-version']]
        if filters:
            filter_args_module = dict(filters)
            filter_args_list = {}
            for fkey, fval in filters.items():
                filter_args_list[fkey.replace('_', '-')] = fval
        else:
            filter_args_module = {}
            filter_args_list = {}

        if hmc_version_info < [2, 16, 0]:
            # Use the "List Adapters of a CPC" operation.
            if additional_properties:
                # Get full properties instead of specific additional properties
                # since "List Adapters of a CPC" does not support
                # additional-properties on these HMC versions.
                _full_properties = True
            else:
                _full_properties = full_properties
            if with_cpc:
                exp_adapters = cpc.adapters.list(
                    filter_args=filter_args_list,
                    full_properties=_full_properties)
            else:
                cpcs_ = client.cpcs.list()
                exp_adapters = []
                for cpc_ in cpcs_:
                    _adapters = cpc_.adapters.list(
                        filter_args=filter_args_list,
                        full_properties=_full_properties)
                    exp_adapters.extend(_adapters)
        else:
            # Use the "List Permitted Adapters" operation.
            if additional_properties and api_version_info < [4, 10]:
                # Get full properties instead of specific additional properties
                # since "List Adapters of a CPC" does not support
                # additional-properties on these early 2.16 API versions.
                _full_properties = True
                _additional_properties = None
            else:
                _full_properties = full_properties
                _additional_properties = additional_properties
            if with_cpc:
                filter_args_list['cpc-name'] = cpc.name
            exp_adapters = console.list_permitted_adapters(
                filter_args=filter_args_list,
                additional_properties=_additional_properties,
                full_properties=_full_properties)

        # Expected adapter properties dict.
        # Key: tuple(cpc name, adapter ID). Adapter ID instead of adapter name
        #      is used to tolerate the error that systems have duplicate adapter
        #      names.
        # Value: Dict of adapter properties using HMC notation (hyphens), plus
        #      'cpc-name'.
        exp_adapter_dict = {}
        for adapter in exp_adapters:
            if DEBUG:
                prop_names = list(adapter.properties.keys())
                print(f"Debug: Expected properties of adapter {adapter.name!r} "
                      f"on CPC {cpc.name!r}: {prop_names!r}")
            cpc = adapter.manager.parent
            exp_properties = {
                'cpc_name': cpc.name
            }
            for pname_hmc, pvalue in adapter.properties.items():
                pname = pname_hmc.replace('-', '_')
                exp_properties[pname] = pvalue
            exp_cpc_adapter_key = (cpc.name, adapter.properties['adapter-id'])
            exp_adapter_dict[exp_cpc_adapter_key] = exp_properties

        # Check that regexp is supported for the 'name' filter. This is done by
        # ensuring that the expected adapters are as expected.
        if filters == {'name': '.*'} and with_cpc:
            all_adapters = cpc.adapters.list()
            all_adapter_ids = [ad.properties['adapter-id']
                               for ad in all_adapters].sort()
            exp_adapter_ids = \
                [item[1] for item in exp_adapter_dict.keys()].sort()
            assert exp_adapter_ids == all_adapter_ids, \
                "cpc.adapters.list() with 'name' filter does not seem to " \
                "support regular expressions"

        # Prepare module input parameters (must be all required + optional)
        params = {
            'hmc_host': hmc_host,
            'hmc_auth': hmc_auth,
            'cpc_name': cpc.name if with_cpc else None,
            'name': filter_args_module.get('name', None),
            'adapter_id': filter_args_module.get('adapter_id', None),
            'adapter_family': filter_args_module.get('adapter_family', None),
            'type': filter_args_module.get('type', None),
            'status': filter_args_module.get('status', None),
            'additional_properties': additional_properties,
            'full_properties': full_properties,
            'log_file': LOG_FILE,
            '_faked_session': faked_session,
        }

        # Prepare mocks for AnsibleModule object
        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        # Exercise the code to be tested
        with pytest.raises(SystemExit) as exc_info:
            zhmc_adapter_list.main()
        exit_code = exc_info.value.args[0]

        # Assert module exit code
        assert exit_code == 0, \
            f"Module failed with exit code {exit_code} and message:\n" \
            f"{get_failure_msg(mod_obj)}"

        # Assert module output
        changed, adapter_list = get_module_output(mod_obj)
        assert changed is False

        assert_adapter_list(adapter_list, exp_adapter_dict)
