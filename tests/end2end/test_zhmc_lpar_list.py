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
from unittest import mock
import requests.packages.urllib3
import zhmcclient
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
from zhmcclient.testutils import classic_mode_cpcs  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_lpar_list
from .utils import mock_ansible_module, get_failure_msg, setup_logging

requests.packages.urllib3.disable_warnings()

# Create log file
LOGGING = False

LOG_FILE = 'test_zhmc_lpar_list.log' if LOGGING else None

# Names of LPAR properties (with underscores) that are volatile, i.e. that may
# change their values on subsequent retrievals even when no other change is
# performed.
VOLATILE_LPAR_PROPERTIES = [
    'program_status_word_information',
    'has_operating_system_messages',
    'has_important_unviewed_operating_system_messages',
    'current_processing_weight',
    'current_aap_processing_weight',
    'current_ifl_processing_weight',
    'current_ziip_processing_weight',
    'current_cf_processing_weight',
]


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


def assert_lpar_list(lpar_list, exp_lpar_dict):
    """
    Assert the output of the zhmc_lpar_list module

    Parameters:

      lpar_list(list): Result of zhmc_lpar_list module, as a list of
        dicts of LPAR properties as documented (with underscores in their
        names).

      exp_lpar_dict(dict): Expected LPARs with their properties.
        Key: tuple(CPC name, LPAR name).
        Value: Dict of expected LPAR properties (including any artificial
        properties, all with underscores in their names).
    """

    assert isinstance(lpar_list, list)

    exp_lpar_keys = list(exp_lpar_dict.keys())
    lpar_keys = [(ri.get('cpc_name', None), ri.get('name', None))
                 for ri in lpar_list]
    assert set(lpar_keys) == set(exp_lpar_keys)

    for lpar_item in lpar_list:
        lpar_name = lpar_item.get('name', None)
        cpc_name = lpar_item.get('cpc_name', None)
        lpar_key = (cpc_name, lpar_name)

        assert lpar_name is not None, \
            f"Returned LPAR {lpar_item!r} does not have a 'name' property"

        assert cpc_name is not None, \
            f"Returned LPAR {lpar_item!r} does not have a 'cpc_name' property"

        assert lpar_key in exp_lpar_dict, \
            f"Result contains unexpected LPAR {lpar_name!r} in CPC {cpc_name!r}"

        exp_lpar_properties = exp_lpar_dict[lpar_key]
        for pname, pvalue in lpar_item.items():
            assert '-' not in pname, \
                f"Property {pname!r} in LPAR {lpar_name!r} is returned with " \
                "hyphens in the property name"
            assert pname in exp_lpar_properties, \
                f"Unexpected property {pname!r} in result LPAR {lpar_name!r}"
            if pname not in VOLATILE_LPAR_PROPERTIES:
                exp_value = exp_lpar_properties[pname]
                assert pvalue == exp_value, \
                    f"Incorrect value for property {pname!r} of result LPAR " \
                    f"{lpar_name!r}"


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
@mock.patch("plugins.modules.zhmc_lpar_list.AnsibleModule", autospec=True)
def test_zhmc_lpar_list(
        ansible_mod_cls, check_mode, property_flags, with_cpc,
        classic_mode_cpcs):  # noqa: F811, E501
    """
    Test the zhmc_lpar_list module with classic mode CPCs.
    """
    if not classic_mode_cpcs:
        pytest.skip("HMC definition does not include any CPCs in classic mode")

    logger = setup_logging(LOGGING, 'test_zhmc_lpar_list', LOG_FILE)
    logger.debug("Entered test function with: "
                 "check_mode=%r, property_flags=%r, with_cpc=%r",
                 check_mode, property_flags, with_cpc)

    for cpc in classic_mode_cpcs:
        assert not cpc.dpm_enabled

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

        # Determine the expected LPARs on the HMC
        logger.debug("Listing expected LPARs")
        av = client.query_api_version()
        hmc_version_info = [int(x) for x in av['hmc-version'].split('.')]
        api_version_info = [av['api-major-version'], av['api-minor-version']]
        if hmc_version_info < [2, 14, 0]:
            # List the LPARs in the traditional way
            if additional_properties:
                # Get full properties instead of specific additional properties
                # since "List Logical Partitions of a CPC" does not support
                # additional-properties.
                _full_properties = True
            else:
                _full_properties = full_properties
            if with_cpc:
                exp_lpars = cpc.lpars.list(full_properties=_full_properties)
            else:
                cpcs_ = client.cpcs.list(full_properties=_full_properties)
                exp_lpars = []
                for cpc_ in cpcs_:
                    exp_lpars.extend(cpc_.lpars.list(
                        full_properties=full_properties))
        else:
            # List the LPARs using the new operation
            if additional_properties and api_version_info < [4, 10]:
                # Get full properties instead of specific additional properties
                # since "List Permitted Logical Partitions" does not support
                # additional-properties on these early 2.16 HMC versions.
                _additional_properties = None
                _full_properties = True
            else:
                _additional_properties = additional_properties
                _full_properties = full_properties
            if with_cpc:
                filter_args = {'cpc-name': cpc.name}
            else:
                filter_args = None
            exp_lpars = console.list_permitted_lpars(
                filter_args=filter_args,
                additional_properties=_additional_properties,
                full_properties=_full_properties)
        exp_lpar_dict = {}
        se_versions = {}
        logger.debug("Processing expected LPARs")
        for lpar in exp_lpars:
            logger.debug("Expected properties of LPAR %r on CPC %r are: %r",
                         lpar.name, cpc.name, dict(lpar.properties))
            cpc = lpar.manager.parent
            try:
                se_version = se_versions[cpc.name]
            except KeyError:
                try:
                    se_version = lpar.properties['se-version']
                except KeyError:
                    logger.debug("Getting expected se-version of CPC %r",
                                 cpc.name)
                    se_version = cpc.get_property('se-version')
                se_versions[cpc.name] = se_version
            exp_properties = {
                'cpc_name': cpc.name,
                'se_version': se_version,
            }
            for pname_hmc, pvalue in lpar.properties.items():
                pname = pname_hmc.replace('-', '_')
                exp_properties[pname] = pvalue
            exp_lpar_key = (cpc.name, lpar.name)
            exp_lpar_dict[exp_lpar_key] = exp_properties

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
            zhmc_lpar_list.main()
        exit_code = exc_info.value.args[0]

        # Assert module exit code
        assert exit_code == 0, \
            f"Module failed with exit code {exit_code} and message:\n" \
            f"{get_failure_msg(mod_obj)}"

        # Assert module output
        changed, lpar_list = get_module_output(mod_obj)
        assert changed is False

        assert_lpar_list(lpar_list, exp_lpar_dict)

    logger.debug("Leaving test function")
