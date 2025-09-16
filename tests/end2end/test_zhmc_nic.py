# Copyright 2025 IBM Corp. All Rights Reserved.
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
End2end tests for zhmc_nic module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from unittest import mock
import random
import pytest
import urllib3
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
from zhmcclient.testutils import dpm_mode_cpcs  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_nic
from .utils import mock_ansible_module, get_failure_msg, setup_logging

urllib3.disable_warnings()

DEBUG = False  # Print debug messages

# Logging for zhmcclient HMC interactions and test functions
LOGGING = True
LOG_FILE = 'test_zhmc_nic.log' if LOGGING else None

# NIC properties that are not always present, but only under certain
# conditions. Properties are specified with hyphens.
NIC_CONDITIONAL_PROPS = (
    'network-adapter-port-uri',  # only present for port-based NICs
    'virtual-switch-uri',  # only present for vswitch-based NICs
    'ssc-ip-address-type',  # only present if SSC mgmt NIC
    'ssc-ip-address',  # only present if SSC mgmt NIC
    'ssc-mask-prefix',  # only present if SSC mgmt NIC
    'vlan-type',  # only present if SSC partition or NIC type roce/cna/netd
    'function-number',  # only present if NIC type cna/netd
    'promiscuous-mode',  # only present starting with z17
    'partition-link-uri',  # only present starting with z17
)

# Artificial partition properties (added by the module).
# Properties are specified with hyphens.
NIC_ARTIFICIAL_PROPS = (
    'partition-name',
    'cpc-name',
    'adapter-id',
    'adapter-name',
    'adapter-port',
)


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, nic_properties) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, nic):
        return changed, nic

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


def assert_nic_props(act_props, exp_props, where):
    """
    Assert the actual properties of a partition.

    Parameters:
      act_props(dict): Actual partition props to verify (with hyphens).
      exp_props(dict): Expected partition properties (with hyphens).
      where(string): Indicator about the testcase for assertion messages.
    """

    assert isinstance(act_props, dict), where
    assert isinstance(exp_props, dict), where

    # Assert presence of unconditional properties in the output
    for prop_name in zhmc_nic.ZHMC_NIC_PROPERTIES:
        prop_name_hmc = prop_name.replace('_', '-')
        if prop_name_hmc in NIC_CONDITIONAL_PROPS:
            continue
        where_prop = where + (f", property {prop_name_hmc!r} missing in "
                              f"NIC properties {act_props!r}")
        assert prop_name_hmc in act_props, where_prop

    # Assert the expected property values
    for prop_name in exp_props:
        exp_value = exp_props[prop_name]
        where_prop = where + (f", property {prop_name!r} missing in "
                              f"NIC properties {act_props!r}")
        assert prop_name in act_props, where_prop
        act_value = act_props[prop_name]
        where_prop = where + (", Unexpected value of NIC property "
                              f"{prop_name!r}: Expected: {exp_value!r}, "
                              f"Actual: {act_value!r}")
        assert act_value == exp_value, where_prop


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_nic.AnsibleModule", autospec=True)
def test_zhmc_nic_facts(
        ansible_mod_cls, check_mode, dpm_mode_cpcs):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name,unused-argument
    """
    Test the zhmc_nic module with state=facts on DPM mode CPCs.
    """
    if not dpm_mode_cpcs:
        pytest.skip("HMC definition does not include any CPCs in DPM mode")

    logger = setup_logging(LOGGING, 'test_zhmc_nic_facts', LOG_FILE)
    logger.debug("Entered test function with: check_mode=%r",
                 check_mode)

    for cpc in dpm_mode_cpcs:
        assert cpc.dpm_enabled

        session = cpc.manager.session
        hd = session.hmc_definition
        hmc_host = hd.host
        hmc_auth = dict(userid=hd.userid, password=hd.password,
                        ca_certs=hd.ca_certs, verify=hd.verify)

        faked_session = session if hd.mock_file else None

        # Determine a random existing partition
        partitions = cpc.partitions.list()
        partition = random.choice(partitions)

        # Determine a random NIC in the partition
        nics = partition.nics.list()
        nic = random.choice(nics)

        logger.debug("Testing with CPC %s, partition %s, NIC %s",
                     cpc.name, partition.name, nic.name)

        # Determine expected NIC properties
        exp_properties = dict(nic.properties)
        port = nic.backing_port()
        adapter = port.manager.parent
        exp_properties['adapter-id'] = \
            adapter.get_property('adapter-id')
        exp_properties['adapter-name'] = adapter.name
        exp_properties['adapter-port'] = port.get_property('index')
        logger.debug("Expected properties of NIC %r are: %r",
                     nic.name, exp_properties)

        where = f"NIC '{nic.name}'"

        # Prepare module input parameters (must be all required + optional)
        params = {
            'hmc_host': hmc_host,
            'hmc_auth': hmc_auth,
            'cpc_name': cpc.name,
            'partition_name': partition.name,
            'name': nic.name,
            'state': 'facts',
            'properties': {},
            'log_file': LOG_FILE,
            '_faked_session': faked_session,
        }

        # Prepare mocks for AnsibleModule object
        mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

        # Exercise the code to be tested
        with pytest.raises(SystemExit) as exc_info:
            zhmc_nic.main()
        exit_code = exc_info.value.args[0]

        # Assert module exit code
        assert exit_code == 0, \
            f"{where}: Module failed with exit code {exit_code} and " \
            f"message:\n{get_failure_msg(mod_obj)}"

        # Assert module output
        changed, nic_properties = get_module_output(mod_obj)
        assert changed is False, \
            f"{where}: Module returned changed={changed}"

        # Check the presence and absence of properties in the result
        assert_nic_props(nic_properties, exp_properties, where)

    logger.debug("Leaving test function")


# TODO: Add tests for state=present

# TODO: Add tests for state=absent
