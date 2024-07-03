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

from unittest import mock
import pytest
import urllib3
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
from zhmcclient.testutils import dpm_mode_cpcs  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_partition_list
from .utils import mock_ansible_module, get_failure_msg, setup_logging

urllib3.disable_warnings()

# Create log file
LOGGING = False

LOG_FILE = 'test_zhmc_partition_list.log' if LOGGING else None


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
    Assert the output of the zhmc_partition_list module

    Parameters:

      partition_list(list): Result of zhmc_partition_list module, as a list of
        dicts of partition properties as documented (with underscores in their
        names).

      exp_partition_dict(dict): Expected partitions with their properties.
        Key: tuple(CPC name, partition name).
        Value: Dict of expected partition properties (including any artificial
        properties, all with underscores in their names).
    """

    assert isinstance(partition_list, list)

    exp_part_keys = list(exp_partition_dict.keys())
    part_keys = [(ri.get('cpc_name', None), ri.get('name', None))
                 for ri in partition_list]
    assert set(part_keys) == set(exp_part_keys)

    for partition_item in partition_list:
        partition_name = partition_item.get('name', None)
        cpc_name = partition_item.get('cpc_name', None)
        part_key = (cpc_name, partition_name)

        assert partition_name is not None, \
            f"Returned partition {partition_item!r} does not have a 'name' " \
            "property"

        assert cpc_name is not None, \
            f"Returned partition {partition_item!r} does not have a " \
            "'cpc_name' property"

        assert part_key in exp_partition_dict, \
            f"Result contains unexpected partition {partition_name!r} in CPC " \
            f"{cpc_name!r}"

        exp_partition_properties = exp_partition_dict[part_key]
        for pname, pvalue in partition_item.items():
            assert '-' not in pname, \
                f"Property {pname!r} in partition {partition_name!r} is " \
                "returned with hyphens in the property name"
            assert pname in exp_partition_properties, \
                f"Unexpected property {pname!r} in result partition " \
                f"{partition_name!r}. Expected properties: " \
                f"{list(exp_partition_properties.keys())!r}"
            exp_value = exp_partition_properties[pname]
            assert pvalue == exp_value, \
                f"Incorrect value for property {pname!r} of result partition " \
                f"{partition_name!r}"


@pytest.mark.parametrize(
    "with_cpc", [
        pytest.param(False, id="with_cpc=False"),
        pytest.param(True, id="with_cpc=True"),
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
@mock.patch("plugins.modules.zhmc_partition_list.AnsibleModule", autospec=True)
def test_zhmc_partition_list(
        ansible_mod_cls, check_mode, property_flags, with_cpc,
        dpm_mode_cpcs):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_partition_list module with DPM mode CPCs.
    """
    if not dpm_mode_cpcs:
        pytest.skip("HMC definition does not include any CPCs in DPM mode")

    logger = setup_logging(LOGGING, 'test_zhmc_partition_list', LOG_FILE)
    logger.debug("Entered test function with: "
                 "check_mode=%r, property_flags=%r, with_cpc=%r",
                 check_mode, property_flags, with_cpc)

    for cpc in dpm_mode_cpcs:
        assert cpc.dpm_enabled

        logger.debug("Testing with CPC %s", cpc.name)

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

        # Determine the expected partitions on the HMC
        logger.debug("Listing expected partitions")
        hmc_version = client.query_api_version()['hmc-version']
        hmc_version_info = [int(x) for x in hmc_version.split('.')]
        if hmc_version_info < [2, 14, 0] or additional_properties:
            # List the LPARs in the traditional way
            if hmc_version_info < [2, 16, 0] and additional_properties:
                # Get full properties instead of specific additional properties
                # since "List Partitions of a CPC" does not support
                # additional-properties on these HMC versions.
                _additional_properties = None
                _full_properties = True
            else:
                _additional_properties = additional_properties
                _full_properties = full_properties
            if with_cpc:
                exp_partitions = cpc.partitions.list(
                    additional_properties=_additional_properties,
                    full_properties=_full_properties)
            else:
                cpcs_ = client.cpcs.list()
                exp_partitions = []
                for cpc_ in cpcs_:
                    _partitions = cpc_.partitions.list(
                        additional_properties=_additional_properties,
                        full_properties=_full_properties)
                    exp_partitions.extend(_partitions)
        else:
            # List the LPARs using the new operation
            if with_cpc:
                filter_args = {'cpc-name': cpc.name}
            else:
                filter_args = None
            exp_partitions = console.list_permitted_partitions(
                filter_args=filter_args,
                full_properties=full_properties)

        exp_partition_dict = {}
        se_versions = {}
        logger.debug("Processing expected partitions")
        for partition in exp_partitions:
            logger.debug("Expected properties of partition %r on CPC %r are: "
                         "%r",
                         partition.name, cpc.name, dict(partition.properties))
            cpc = partition.manager.parent
            try:
                se_version = se_versions[cpc.name]
            except KeyError:
                try:
                    se_version = partition.properties['se-version']
                except KeyError:
                    logger.debug("Getting expected se-version of CPC %r",
                                 cpc.name)
                    se_version = cpc.get_property('se-version')
                se_versions[cpc.name] = se_version
            exp_properties = {
                'cpc_name': cpc.name,
                'se_version': se_version,
            }
            for pname_hmc, pvalue in partition.properties.items():
                pname = pname_hmc.replace('-', '_')
                exp_properties[pname] = pvalue
            exp_part_key = (cpc.name, partition.name)
            exp_partition_dict[exp_part_key] = exp_properties

        # Prepare module input parameters (must be all required + optional)
        params = {
            'hmc_host': hmc_host,
            'hmc_auth': hmc_auth,
            'cpc_name': cpc.name if with_cpc else None,
            'additional_properties': additional_properties,
            'full_properties': full_properties,
            'log_file': LOG_FILE,
            '_faked_session': faked_session,
        }

        # Prepare mocks for AnsibleModule object
        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        # Exercise the code to be tested
        with pytest.raises(SystemExit) as exc_info:
            zhmc_partition_list.main()
        exit_code = exc_info.value.args[0]

        # Assert module exit code
        assert exit_code == 0, \
            f"Module failed with exit code {exit_code} and message:\n" \
            f"{get_failure_msg(mod_obj)}"

        # Assert module output
        changed, partition_list = get_module_output(mod_obj)
        assert changed is False

        assert_partition_list(partition_list, exp_partition_dict)

    logger.debug("Leaving test function")
