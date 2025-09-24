#!/usr/bin/python
# Copyright 2020 IBM Corp. All Rights Reserved.
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

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

# For information on the format of the ANSIBLE_METADATA, DOCUMENTATION,
# EXAMPLES, and RETURN strings, see
# http://docs.ansible.com/ansible/dev_guide/developing_modules_documenting.html

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['stableinterface'],
    'supported_by': 'community',
    'shipped_by': 'other',
    'other_repo_url': 'https://github.com/zhmcclient/zhmc-ansible-modules'
}

DOCUMENTATION = """
---
module: zhmc_cpc_capacity
version_added: "2.15.0"
short_description: Manage temporary processor capacity
description:
  - Gather facts about the processor capacity of a CPC (Z system).
  - Update the processor capacity of a CPC (Z system) via adding or removing
    temporary capacity (On/Off CoD).
  - For details on processor capacity on demand, see the
    R(Capacity on Demand User's Guide,CoD Users Guide).
author:
  - Andreas Maier (@andy-maier)
requirements:
  - "The HMC userid must have these task permissions:
    'Perform Model Conversion'."
  - "The HMC userid must have object-access permissions to these objects:
    Target CPCs."
  - "The CPC must be enabled for On-Off Capacity-On-Demand."
options:
  hmc_host:
    description:
      - The hostnames or IP addresses of a single HMC or of a list of redundant
        HMCs. A single HMC can be specified as a string type or as an HMC list
        with one item. An HMC list can be specified as a list type or as a
        string type containing a Python list representation.
      - The first available HMC of a list of redundant HMCs is used for the
        entire execution of the module.
    type: raw
    required: true
  hmc_auth:
    description:
      - The authentication credentials for the HMC.
    type: dict
    required: true
    suboptions:
      userid:
        description:
          - The userid (username) for authenticating with the HMC.
            This is mutually exclusive with providing O(hmc_auth.session_id).
        type: str
        required: false
        default: null
      password:
        description:
          - The password for authenticating with the HMC.
            This is mutually exclusive with providing O(hmc_auth.session_id).
        type: str
        required: false
        default: null
      session_id:
        description:
          - HMC session ID to be used.
            This is mutually exclusive with providing O(hmc_auth.userid) and
            O(hmc_auth.password) and can be created as described in the
            R(zhmc_session module,zhmc_session_module).
        type: str
        required: false
        default: null
      ca_certs:
        description:
          - Path name of certificate file or certificate directory to be used
            for verifying the HMC certificate. If null (default), the path name
            in the E(REQUESTS_CA_BUNDLE) environment variable or the path name
            in the E(CURL_CA_BUNDLE) environment variable is used, or if neither
            of these variables is set, the certificates in the Mozilla CA
            Certificate List provided by the 'certifi' Python package are used
            for verifying the HMC certificate.
        type: str
        required: false
        default: null
      verify:
        description:
          - If True (default), verify the HMC certificate as specified in the
            O(hmc_auth.ca_certs) parameter. If False, ignore what is specified in the
            O(hmc_auth.ca_certs) parameter and do not verify the HMC certificate.
        type: bool
        required: false
        default: true
  name:
    description:
      - The name of the target CPC.
    type: str
    required: true
  state:
    description:
      - "The desired state for the operation:"
      - "* V(set): Ensures that the CPC has the specified specialty processor
           capacity and the specified software model, and returns the resulting
           processor capacity of the CPC."
      - "* V(facts): Does not change anything on the CPC and returns the
           current processor capacity of the CPC."
    type: str
    required: true
    choices: ['set', 'facts']
  record_id:
    description:
      - "The ID of the capacity record to be used for any updates of the
         processor capacity."
      - "Required for O(state=set)."
    type: str
    required: false
    default: null
  software_model:
    description:
      - "The target software model to be active. This value must be one of
         the software models defined within the specified capacity record.
         The software model implies the number of general purpose processors
         that will be active."
      - "If null or not provided, the software model and the number of
         general purpose processors of the CPC will remain unchanged."
    type: str
    required: false
    default: null
  software_model_direction:
    description:
      - "Indicates the direction of the capacity change for general purpose
         processors in O(software_model), relative to the current software
         model:"
      - "* V(increase): The specified software model defines more general
           purpose processors than the current software model."
      - "* V(decrease): The specified software model defines less general
           purpose processors than the current software model."
      - "Ignored when O(software_model) is null, not provided, or specifies
         the current software model. Otherwise required."
    type: str
    choices: ['increase', 'decrease']
    required: false
    default: null
  specialty_processors:
    description:
      - "The target number of specialty processors to be active. Processor
         types not provided will not be changed. Target numbers of general
         purpose processors can be set via the O(software_model) parameter."
      - "Each item in the dictionary identifies the target number of processors
         of one type of specialty processor. The key identifies the type
         of specialty processor (V(icf), V(ifl), V(iip), V(sap)),
         and the value is the target number of processors of that type. Note
         that the target number is the number of permanently activated
         processors plus the number of temporarily activated processors."
      - "The target number for each processor type may be larger, equal or
         lower than the current number, but it must not be lower than the
         number of permanent processors of that type."
      - "If the target number of processors is not installed in the CPC,
         the O(force) parameter controls what happens."
      - "If null, empty or not provided, the specialty processor capacity will
         remain unchanged."
    type: dict
    required: false
    default: null
  test_activation:
    description:
      - "Indicates that for an increase of capacity, test resources instead of
         real resources from the capacity record should be activated.
         This parameter has no meaning if the capacity is decreased.
         Test resources are automatically deactivated after 24h. This is mainly
         used for Capacity Backup Upgrade (CBU) test activations. For details,
         see the R(Capacity on Demand User's Guide,CoD Users Guide)."
    type: bool
    required: false
    default: false
  force:
    description:
      - "Indicates that an increase of capacity should be performed even if the
         necessary processors are not currently installed in the CPC.
         This parameter has no meaning if the capacity is decreased."
    type: bool
    required: false
    default: false
  log_file:
    description:
      - "File path of a log file to which the logic flow of this module as well
         as interactions with the HMC are logged. If null, logging will be
         propagated to the Python root logger."
    type: str
    required: false
    default: null
  _faked_session:
    description:
      - "An internal parameter used for testing the module."
    type: raw
    required: false
    default: null
"""

EXAMPLES = """
---
# Note: The following examples assume that some variables named 'my_*' are set.

- name: Gather facts about the CPC processor capacity
  zhmc_cpc_capacity:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_cpc_name }}"
    state: facts
  register: cap1

- name: Ensure the CPC has a certain general purpose processor capacity active
  zhmc_cpc_capacity:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_cpc_name }}"
    state: set
    record_id: R1234
    software_model: "710"
  register: cap1

- name: Ensure the CPC has a certain IFL processor capacity active
  zhmc_cpc_capacity:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_cpc_name }}"
    state: set
    record_id: R1234
    specialty_processors:
      ifl: 20
  register: cap1
"""

RETURN = """
changed:
  description: Indicates if any change has been made by the module.
    For O(state=facts), always will be false.
  returned: always
  type: bool
msg:
  description: An error message that describes the failure.
  returned: failure
  type: str
cpc:
  description: "A dictionary with capacity related properties of the CPC."
  returned: success
  type: dict
  contains:
    name:
      description: "CPC name"
      type: str
    has_temporary_capacity_change_allowed:
      description:
        - "Boolean indicating whether API applications are allowed to make
           changes to temporary capacity."
      type: bool
    is_on_off_cod_enabled:
      description:
        - "Boolean indicating whether the On/Off Capacity on Demand feature
           is enabled for the CPC."
      type: bool
    is_on_off_cod_installed:
      description:
        - "Boolean indicating whether an On/Off Capacity on Demand record is
           installed on the CPC."
      type: bool
    is_on_off_cod_activated:
      description:
        - "Boolean indicating whether an On/Off Capacity on Demand record is
           installed and active on the CPC."
      type: bool
    on_off_cod_activation_date:
      description:
        - "Timestamp when the On/Off Capacity on Demand record was activated
           on the CPC."
      type: int

    software_model_purchased:
      description:
        - "The software model based on the originally purchased processors.
          Omitted for SE version below 2.16.0."
      type: str
    software_model_permanent:
      description:
        - "The software model based on the permanently present processors
          (including any permanent capacity changes since the original
          purchase)."
      type: str
    software_model_permanent_plus_billable:
      description:
        - "The software model based on the permanently present processors
          plus billable temporary processors."
      type: str
    software_model_permanent_plus_temporary:
      description:
        - "The software model based on the permanently present processors
          plus all temporary processors."
      type: str

    msu_purchased:
      description:
        - "The MSU value associated with the software model based on the
           originally purchased processors.
           Omitted for SE version below 2.16.0."
      type: int
    msu_permanent:
      description:
        - "The MSU value associated with the software model based on the
          permanently present processors (including any permanent capacity
          changes since the original purchase)."
      type: int
    msu_permanent_plus_billable:
      description:
        - "The MSU value associated with the software model based on the
           permanently present processors plus billable temporary processors."
      type: int
    msu_permanent_plus_temporary:
      description:
        - "The MSU value associated with the software model based on the
           permanently present processors plus all temporary processors."
      type: int

    processor_count_general_purpose:
      description:
        - "The count of active general purpose processors."
      type: int
    processor_count_ifl:
      description:
        - "The count of active Integrated Facility for Linux (IFL) processors."
      type: int
    processor_count_icf:
      description:
        - "The count of active Internal Coupling Facility (ICF) processors."
      type: int
    processor_count_iip:
      description:
        - "The count of active IBM z Integrated Information Processor (zIIP)
           processors."
      type: int
    processor_count_service_assist:
      description:
        - "The count of active service assist processors."
      type: int
    processor_count_spare:
      description:
        - "The count of spare processors, across all processor types."
      type: int
    processor_count_defective:
      description:
        - "The count of defective processors, across all processor types."
      type: int

    processor_count_pending_general_purpose:
      description:
        - "The number of general purpose processors that will become active,
           when more processors are made available by adding new hardware or by
           deactivating capacity records."
      type: int
    processor_count_pending_ifl:
      description:
        - "The number of Integrated Facility for Linux processors that will
           become active, when more processors are made available by adding new
           hardware or by deactivating capacity records."
      type: int
    processor_count_pending_icf:
      description:
        - "The number of Integrated Coupling Facility processors that will
           become active, when more processors are made available by adding new
           hardware or by deactivating capacity records."
      type: int
    processor_count_pending_iip:
      description:
        - "The number of z Integrated Information Processors that will become
           active, when more processors are made available by adding new
           hardware or by deactivating capacity records."
      type: int
    processor_count_pending_service_assist:
      description:
        - "The number of service assist processors that will become active,
           when more processors are made available by adding new hardware or by
           deactivating capacity records."
      type: int

    processor_count_permanent_ifl:
      description:
        - "The number of Integrated Facility for Linux processors that are
           permanent.
           Omitted for SE version below 2.16.0."
      type: int
    processor_count_permanent_icf:
      description:
        - "The number of Integrated Coupling Facility processors that are
           permanent.
           Omitted for SE version below 2.16.0."
      type: int
    processor_count_permanent_iip:
      description:
        - "The number of z Integrated Information Processors that are
           permanent.
           Omitted for SE version below 2.16.0."
      type: int
    processor_count_permanent_service_assist:
      description:
        - "The number of service assist processors that are permanent.
          Omitted for SE version below 2.16.0."
      type: int

    processor_count_unassigned_ifl:
      description:
        - "The number of Integrated Facility for Linux processors that are
           unassigned.
           Omitted for SE version below 2.16.0."
      type: int
    processor_count_unassigned_icf:
      description:
        - "The number of Integrated Coupling Facility processors that are
           unassigned.
           Omitted for SE version below 2.16.0."
      type: int
    processor_count_unassigned_iip:
      description:
        - "The number of z Integrated Information Processors that are
           unassigned.
           Omitted for SE version below 2.16.0."
      type: int
    processor_count_unassigned_service_assist:
      description:
        - "The number of service assist processors that are unassigned.
          Omitted for SE version below 2.16.0."
      type: int
"""

import logging  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402

from ..module_utils.common import log_init, open_session, close_session, \
    hmc_auth_parameter, Error, missing_required_lib, \
    common_fail_on_import_errors, parse_hmc_host, \
    underscore_properties, blanked_params  # noqa: E402

try:
    import urllib3
    IMP_URLLIB3_ERR = None
except ImportError:
    IMP_URLLIB3_ERR = traceback.format_exc()

try:
    import zhmcclient
    IMP_ZHMCCLIENT_ERR = None
except ImportError:
    IMP_ZHMCCLIENT_ERR = traceback.format_exc()

# Python logger name for this module
LOGGER_NAME = 'zhmc_cpc_capacity'

LOGGER = logging.getLogger(LOGGER_NAME)


# Capacity-related CPC properties for result, in HMC notation (hyphens)
# The display order is automatically sorted by Ansible.
CPC_CAPACITY_PROPERTIES = [
    'name',
    'has-temporary-capacity-change-allowed',
    'is-on-off-cod-enabled',
    'is-on-off-cod-installed',
    'is-on-off-cod-activated',
    'on-off-cod-activation-date',
    'software-model-purchased',  # added in SE 2.16.0
    'software-model-permanent',
    'software-model-permanent-plus-billable',
    'software-model-permanent-plus-temporary',
    'msu-purchased',  # added in SE 2.16.0
    'msu-permanent',
    'msu-permanent-plus-billable',
    'msu-permanent-plus-temporary',
    'processor-count-general-purpose',
    'processor-count-ifl',
    'processor-count-icf',
    'processor-count-iip',
    'processor-count-service-assist',
    'processor-count-spare',
    'processor-count-defective',
    'processor-count-pending-general-purpose',
    'processor-count-pending-ifl',
    'processor-count-pending-icf',
    'processor-count-pending-iip',
    'processor-count-pending-service-assist',
    'processor-count-permanent-ifl',  # added in SE 2.16.0
    'processor-count-permanent-icf',  # added in SE 2.16.0
    'processor-count-permanent-iip',  # added in SE 2.16.0
    'processor-count-permanent-service-assist',  # added in SE 2.16.0
    'processor-count-unassigned-ifl',  # added in SE 2.16.0
    'processor-count-unassigned-icf',  # added in SE 2.16.0
    'processor-count-unassigned-iip',  # added in SE 2.16.0
    'processor-count-unassigned-service-assist',  # added in SE 2.16.0
]


def split_target_processors(target_processors, current_processors):
    """
    Split the target processor dict into processors to add and processors to
    remove, relative to the current processors.

    In all parameters and return values, dict key is the processor type and dict
    value is the number of processors.

    Parameters:
        target_processors(dict): Dict with target numbers of the specialty
          processors.
        current_processors(dict): Dict with current numbers of the specialty
          processors.

    Returns:
      tuple(add_info, remove_info): Tuple of dict with processor numbers to
        add and dict with processor numbers to remove.
    """
    add_processors = {}
    remove_processors = {}
    for proc_key, target_number in target_processors.items():
        current_number = current_processors[proc_key]
        if target_number > current_number:
            add_processors[proc_key] = target_number - current_number
        elif target_number < current_number:
            remove_processors[proc_key] = current_number - target_number
    return add_processors, remove_processors


def get_current_processor_dict(cpc):
    """
    Get the current speciality processors of the CPC as a processor dict.
    """
    processor_dict = {
        'ifl': cpc.get_property('processor-count-ifl'),
        'icf': cpc.get_property('processor-count-icf'),
        'iip': cpc.get_property('processor-count-iip'),
        'sap': cpc.get_property('processor-count-service-assist'),
    }
    return processor_dict


def cpc_result_properties(cpc):
    """
    Convert CPC properties (with hyphens) into result properties
    (with underscores) and reduce to exact set defined.
    """
    result_props = {}
    for prop_name in CPC_CAPACITY_PROPERTIES:
        # Some properties have been added in SSE 2.16.0. If the property is
        # not known by the CPC, we just ignore it.
        try:
            value = cpc.get_property(prop_name)
            result_props[prop_name] = value
        except KeyError:
            pass
    return underscore_properties(result_props)


def add_temporary_capacity_check_mode(
        cpc, record_id, software_model, processor_info):
    # pylint: disable=unused-argument
    """
    Simulate the addition of capacity in check mode, by updating the CPC
    properties locally.
    """
    update_properties = {}

    if software_model:
        current_model = cpc.get_property(
            'software-model-permanent-plus-temporary')
        if software_model != current_model:
            update_properties['software-model-permanent-plus-temporary'] = \
                software_model
            update_properties['software-model-permanent-plus-billable'] = \
                software_model
            cp_delta = 1  # TODO: Can we find out from the software model?
            update_properties['processor-count-general-purpose'] = \
                cpc.get_property('processor-count-general-purpose') + cp_delta

    if processor_info:
        for proc_key, delta in processor_info.items():
            if proc_key == 'ifl':
                update_properties['processor-count-ifl'] = \
                    cpc.get_property('processor-count-ifl') + delta
            elif proc_key == 'icf':
                update_properties['processor-count-icf'] = \
                    cpc.get_property('processor-count-icf') + delta
            elif proc_key == 'iip':
                update_properties['processor-count-iip'] = \
                    cpc.get_property('processor-count-iip') + delta
            elif proc_key == 'sap':
                update_properties['processor-count-service-assist'] = \
                    cpc.get_property('processor-count-service-assist') + delta

    if update_properties:
        cpc.update_properties_local(update_properties)


def remove_temporary_capacity_check_mode(
        cpc, record_id, software_model, processor_info):
    # pylint: disable=unused-argument
    """
    Simulate the removal of capacity in check mode, by updating the CPC
    properties locally.
    """
    update_properties = {}

    if software_model:
        current_model = cpc.get_property(
            'software-model-permanent-plus-temporary')
        if software_model != current_model:
            update_properties['software-model-permanent-plus-temporary'] = \
                software_model
            cp_delta = 1  # TODO: Can we find out from the software model?
            update_properties['processor-count-general-purpose'] = \
                cpc.get_property('processor-count-general-purpose') - cp_delta

    if processor_info:
        for proc_key, delta in processor_info.items():
            if proc_key == 'ifl':
                update_properties['processor-count-ifl'] = \
                    cpc.get_property('processor-count-ifl') - delta
            elif proc_key == 'icf':
                update_properties['processor-count-icf'] = \
                    cpc.get_property('processor-count-icf') - delta
            elif proc_key == 'iip':
                update_properties['processor-count-iip'] = \
                    cpc.get_property('processor-count-iip') - delta
            elif proc_key == 'sap':
                update_properties['processor-count-service-assist'] = \
                    cpc.get_property('processor-count-service-assist') - delta

    if update_properties:
        cpc.update_properties_local(update_properties)


def ensure_set(module):
    """
    Identify the target CPC and ensure that the specified capacity is set on
    the target CPC.

    Raises:
      ParameterError: An issue with the module parameters.
      Error: Other errors during processing.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    module.fail_on_missing_params(['record_id'])
    cpc_name = module.params['name']
    record_id = module.params['record_id']
    software_model = module.params['software_model']
    software_model_direction = module.params['software_model_direction']
    specialty_processors = module.params['specialty_processors']
    if specialty_processors is None:
        specialty_processors = {}
    test_activation = module.params['test_activation']
    force = module.params['force']

    changed = False
    need_pull = False

    session, logoff = open_session(module.params)
    try:
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        cpc.pull_properties(CPC_CAPACITY_PROPERTIES)

        add_software_model = None
        remove_software_model = None
        if software_model:
            current_model = cpc.get_property(
                'software-model-permanent-plus-temporary')
            if software_model != current_model:
                module.fail_on_missing_params(['software_model_direction'])
                if software_model_direction == 'increase':
                    add_software_model = software_model
                elif software_model_direction == 'decrease':
                    remove_software_model = software_model

        add_processors = None
        remove_processors = None
        if specialty_processors:
            current_processors = get_current_processor_dict(cpc)
            add_processors, remove_processors = split_target_processors(
                specialty_processors, current_processors)

        if add_processors or add_software_model:
            LOGGER.debug(
                "Adding temporary capacity to CPC %r: software_model=%r, "
                "processors=%r",
                cpc_name, add_software_model, add_processors)
            if not module.check_mode:
                cpc.add_temporary_capacity(
                    record_id, software_model=add_software_model,
                    processor_info=add_processors,
                    test=test_activation,
                    force=force)
                need_pull = True
            else:
                add_temporary_capacity_check_mode(
                    cpc, record_id, software_model=add_software_model,
                    processor_info=add_processors)
            changed = True

        if remove_processors or remove_software_model:
            LOGGER.debug(
                "Removing temporary capacity from CPC %r: software_model=%r, "
                "processor_info=%r",
                cpc_name, remove_software_model, remove_processors)
            if not module.check_mode:
                cpc.remove_temporary_capacity(
                    record_id, software_model=remove_software_model,
                    processor_info=remove_processors)
                need_pull = True
            else:
                remove_temporary_capacity_check_mode(
                    cpc, record_id, software_model=remove_software_model,
                    processor_info=remove_processors)
            changed = True

        if need_pull:
            cpc.pull_properties(CPC_CAPACITY_PROPERTIES)

        result = cpc_result_properties(cpc)
        return changed, result

    finally:
        close_session(session, logoff)


def facts(module):
    """
    Identify the target CPC and return facts about the target CPC and its
    child resources.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    cpc_name = module.params['name']

    session, logoff = open_session(module.params)
    try:
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        cpc.pull_properties(CPC_CAPACITY_PROPERTIES)

        result = cpc_result_properties(cpc)
        return False, result

    finally:
        close_session(session, logoff)


def perform_task(module):
    """
    Perform the task for this module, dependent on the 'state' module
    parameter.

    If check_mode is True, check whether changes would occur, but don't
    actually perform any changes.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """
    actions = {
        "set": ensure_set,
        "facts": facts,
    }
    return actions[module.params['state']](module)


def main():
    """Main function"""

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='raw'),
        hmc_auth=hmc_auth_parameter(),
        name=dict(required=True, type='str'),
        state=dict(required=True, type='str', choices=['set', 'facts']),
        record_id=dict(required=False, type='str', default=None),
        software_model=dict(required=False, type='str', default=None),
        software_model_direction=dict(
            required=False, type='str', choices=['increase', 'decrease'],
            default=None),
        specialty_processors=dict(required=False, type='dict', default=None),
        test_activation=dict(required=False, type='bool', default=False),
        force=dict(required=False, type='bool', default=False),
        log_file=dict(required=False, type='str', default=None),
        _faked_session=dict(required=False, type='raw'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True)

    if IMP_URLLIB3_ERR is not None:
        module.fail_json(msg=missing_required_lib("requests"),
                         exception=IMP_URLLIB3_ERR)

    urllib3.disable_warnings()

    if IMP_ZHMCCLIENT_ERR is not None:
        module.fail_json(msg=missing_required_lib("zhmcclient"),
                         exception=IMP_ZHMCCLIENT_ERR)

    common_fail_on_import_errors(module)

    log_file = module.params['log_file']
    log_init(LOGGER_NAME, log_file)

    module.params['hmc_host'] = parse_hmc_host(module.params['hmc_host'])

    if LOGGER.isEnabledFor(logging.DEBUG):
        LOGGER.debug("Module entry: params: %r",
                     blanked_params(module.params))

    try:

        changed, result = perform_task(module)

    except (Error, zhmcclient.Error) as exc:
        # These exceptions are considered errors in the environment or in user
        # input. They have a proper message that stands on its own, so we
        # simply pass that message on and will not need a traceback.
        msg = f"{exc.__class__.__name__}: {exc}"
        LOGGER.debug("Module exit (failure): msg: %r", msg)
        module.fail_json(msg=msg)
    # Other exceptions are considered module errors and are handled by Ansible
    # by showing the traceback.

    LOGGER.debug("Module exit (success): changed: %s, cpc: %r",
                 changed, result)
    module.exit_json(
        changed=changed, cpc=result)


if __name__ == '__main__':
    main()
