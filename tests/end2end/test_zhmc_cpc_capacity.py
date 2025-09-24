# Copyright 2024 IBM Corp. All Rights Reserved.
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
End2end tests for zhmc_cpc_capacity module.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
import random
import pytest
import mock
import urllib3
# pylint: disable=line-too-long,unused-import
from zhmcclient.testutils import hmc_definition, hmc_session  # noqa: F401, E501
from zhmcclient.testutils import all_cpcs  # noqa: F401, E501
# pylint: enable=line-too-long,unused-import

from plugins.modules import zhmc_cpc_capacity
from plugins.module_utils.common import underscore_properties
from .utils import mock_ansible_module, get_failure_msg, setup_logging

urllib3.disable_warnings()

# Enable logging
LOGGING = False

LOG_FILE = 'zhmc_cpc_capacity.log' if LOGGING else None


def calc_sw_model(sw_model, delta):
    """
    Calculate the string for a new software model, based on the specified
    software model and a numeric delta.

    The software model string (3 chars) is interpreted as a hex number and the
    delta is added.
    """
    sw_model_number = int(sw_model, 16)
    sw_model_number += delta
    sw_model_str = format(sw_model_number, "X")
    return sw_model_str


def get_module_output(mod_obj):
    """
    Return the module output as a tuple (changed, user_properties) (i.e.
    the arguments of the call to exit_json()).
    If the module failed, return None.
    """

    def func(changed, cpc):
        return changed, cpc

    if not mod_obj.exit_json.called:
        return None
    call_args = mod_obj.exit_json.call_args

    # The following makes sure we get the arguments regardless of whether they
    # were specified as positional or keyword arguments:
    return func(*call_args[0], **call_args[1])


# CPC properties in result of zhmc_cpc_capacity module, with underscores.
CPC_CAPACITY_PROPERTIES = [
    'name',
    'has_temporary_capacity_change_allowed',
    'is_on_off_cod_enabled',
    'is_on_off_cod_installed',
    'is_on_off_cod_activated',
    'on_off_cod_activation_date',
    'software_model_purchased',
    'software_model_permanent',
    'software_model_permanent_plus_billable',
    'software_model_permanent_plus_temporary',
    'msu_purchased',
    'msu_permanent',
    'msu_permanent_plus_billable',
    'msu_permanent_plus_temporary',
    'processor_count_general_purpose',
    'processor_count_ifl',
    'processor_count_icf',
    'processor_count_iip',
    'processor_count_service_assist',
    'processor_count_spare',
    'processor_count_defective',
    'processor_count_pending_general_purpose',
    'processor_count_pending_ifl',
    'processor_count_pending_icf',
    'processor_count_pending_iip',
    'processor_count_pending_service_assist',
    'processor_count_permanent_ifl',
    'processor_count_permanent_icf',
    'processor_count_permanent_iip',
    'processor_count_permanent_service_assist',
    'processor_count_unassigned_ifl',
    'processor_count_unassigned_icf',
    'processor_count_unassigned_iip',
    'processor_count_unassigned_service_assist',
]


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_cpc_capacity.AnsibleModule", autospec=True)
def test_zhmc_cpc_capacity_facts(
        ansible_mod_cls, check_mode, all_cpcs):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_cpc_capacity module with state=facts.
    """
    if not all_cpcs:
        pytest.skip("HMC definition does not include any CPCs")

    setup_logging(LOGGING, 'test_zhmc_cpc_capacity', LOG_FILE)

    cpc = random.choice(all_cpcs)

    session = cpc.manager.session
    hd = session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    faked_session = session if hd.mock_file else None

    # Determine the expected CPC properties
    cpc.pull_full_properties()
    exp_cpc_props = underscore_properties(cpc.properties)

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'name': cpc.name,
        'state': 'facts',
        'record_id': None,
        'software_model': None,
        'software_model_direction': None,
        'specialty_processors': None,
        'test_activation': False,
        'force': False,
        'log_file': LOG_FILE,
        '_faked_session': faked_session,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_cpc_capacity.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 0, \
        "Module failed with exit code {e} and message:\n{m}". \
        format(e=exit_code, m=get_failure_msg(mod_obj))

    # Assert module output

    changed, cpc_props = get_module_output(mod_obj)
    assert changed is False

    for name, value in cpc_props.items():
        assert name in CPC_CAPACITY_PROPERTIES

        exp_value = exp_cpc_props[name]
        assert value == exp_value, \
            "Incorrect value for property {p!r} in module result for " \
            "CPC {c!r}: Got {v!r}, expected {ev!r}". \
            format(p=name, c=cpc.name, v=value, ev=exp_value)


@pytest.mark.parametrize(
    "check_mode", [
        pytest.param(False, id="check_mode=False"),
        # pytest.param(True, id="check_mode=True"),
    ]
)
@mock.patch("plugins.modules.zhmc_cpc_capacity.AnsibleModule", autospec=True)
def test_zhmc_cpc_capacity_set(
        ansible_mod_cls, check_mode, all_cpcs):  # noqa: F811, E501
    # pylint: disable=redefined-outer-name
    """
    Test the zhmc_cpc_capacity module with state=set.
    """
    if not all_cpcs:
        pytest.skip("HMC definition does not include any CPCs")

    setup_logging(LOGGING, 'test_zhmc_cpc_capacity', LOG_FILE)

    cpc = random.choice(all_cpcs)

    session = cpc.manager.session
    hd = session.hmc_definition
    hmc_host = hd.host
    hmc_auth = dict(userid=hd.userid, password=hd.password,
                    ca_certs=hd.ca_certs, verify=hd.verify)

    faked_session = session if hd.mock_file else None

    temp_sw_model = cpc.get_property('software-model-permanent-plus-temporary')

    # Increase temporary capacity (with incorrect record ID)

    new_sw_model = calc_sw_model(temp_sw_model, 1)

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'name': cpc.name,
        'state': 'set',
        'record_id': 'foo',  # invalid
        'software_model': new_sw_model,
        'software_model_direction': 'increase',
        'specialty_processors': None,
        'test_activation': True,
        'force': False,
        'log_file': LOG_FILE,
        '_faked_session': faked_session,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_cpc_capacity.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 1
    msg = get_failure_msg(mod_obj)
    assert re.match(r"HTTPError: 400,274: record-id .* was not found", msg)

    # Decrease temporary capacity (with incorrect record ID)

    new_sw_model = calc_sw_model(temp_sw_model, -1)

    # Prepare module input parameters (must be all required + optional)
    params = {
        'hmc_host': hmc_host,
        'hmc_auth': hmc_auth,
        'name': cpc.name,
        'state': 'set',
        'record_id': 'foo',  # invalid
        'software_model': new_sw_model,
        'software_model_direction': 'decrease',
        'specialty_processors': None,
        'test_activation': None,
        'force': None,
        'log_file': LOG_FILE,
        '_faked_session': faked_session,
    }

    # Prepare mocks for AnsibleModule object
    mod_obj = mock_ansible_module(ansible_mod_cls, params, check_mode)

    # Exercise the code to be tested
    with pytest.raises(SystemExit) as exc_info:
        zhmc_cpc_capacity.main()
    exit_code = exc_info.value.args[0]

    # Assert module exit code
    assert exit_code == 1
    msg = get_failure_msg(mod_obj)
    assert re.match(r"HTTPError: 400,274: record-id .* was not found", msg)
