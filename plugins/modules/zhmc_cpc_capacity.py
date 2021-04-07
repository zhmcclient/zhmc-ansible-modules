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
version_added: "2.9.0"
short_description: Manage processor capacity on demand
description:
  - Gather facts about the processor capacity of a CPC (Z system).
  - Update the processor capacity of a CPC (Z system) via adding or removing
    temporary capacity (On/Off CoD).
  - For details on processor capacity on demand, see the
    :term:`Capacity on Demand User's Guide`.
author:
  - Andreas Maier (@andy-maier)
requirements:
  - Access to the WS API of the HMC of the targeted Z system
    (see :term:`HMC API`). The targeted Z system can be in any operational
    mode (classic, DPM).
options:
  hmc_host:
    description:
      - The hostname or IP address of the HMC.
    type: str
    required: true
  hmc_auth:
    description:
      - The authentication credentials for the HMC, as a dictionary of
        C(userid), C(password).
    type: dict
    required: true
    suboptions:
      userid:
        description:
          - The userid (username) for authenticating with the HMC.
        type: str
        required: true
      password:
        description:
          - The password for authenticating with the HMC.
        type: str
        required: true
  name:
    description:
      - The name of the target CPC.
    type: str
    required: true
  state:
    description:
      - "The desired state for the operation:"
      - "* C(set): Ensures that the CPC has the specified processor capacity
         and returns capacity related properties of the CPC.."
      - "* C(facts): Does not change anything on the CPC and returns
         capacity related properties of the CPC."
    type: str
    required: true
    choices: ['set', 'facts']
  test:
    description:
      - "Indicates whether real or test resources should be activated. Test
         resources are automatically deactivated after 24h."
    type: bool
    required: false
    default: false
  record_id:
    description:
      - "The ID of the capacity record to be used for any updates of the
         processor capacity."
    type: str
    required: true
  software_model:
    description:
      - "The target software model to be active. This value must be one of
         the software models defined within the specified capacity record.
         The software model implies the number of general purpose processors
         that will be active. Target numbers of specialty processors can be
         specified with the C(specialty_processors) parameter."
    type: str
    required: false
    default: null
  specialty_processors:
    description:
      - "The target number of specialty processors to be active. Processor
         types not specified will not be changed. Target numbers of general
         purpose processors can be set via the C(software_model) parameter."
      - "Each item in the dictionary identifies the target number of processors
         of one type of specialty processor. The key identifies the type
         of specialty processor ('aap', 'cbp', 'icf', 'ifl', 'iip', 'sap'),
         and the value is the target number of processors of that type. Note
         that the target number is the number of permanently activated
         processors plus the number of temporarily activated processors."
      - "If the target number of processors is not installed in the system,
         or if the specified software model or number of a specialty processors
         exceeds the limits of the capacity record, the task will fail."
    type: dict
    required: false
    default: {}
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
    required: false
    type: raw
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
    record_id: 1234
    software_model: "710"
  register: cap1

- name: Ensure the CPC has a certain IFL processor capacity active
  zhmc_cpc_capacity:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_cpc_name }}"
    state: set
    record_id: 1234
    specialty_processors:
      ifl: 20
  register: cap1
"""

RETURN = """
changed:
  description: Indicates if any change has been made by the module.
    For C(state=facts), always will be false.
  returned: always
  type: bool
msg:
  description: An error message that describes the failure.
  returned: failure
  type: str
cpc:
  description: "A dictionary with capacity related properties of the CPC that
                indicate the currently active processor capacity."
  returned: success
  type: dict
  contains:
    name:
      description: "CPC name"
      type: str
    software_model:
      description:
        - "The current software model that is active.
           The software model implies the number of general purpose processors
           that are active."
      type: str
    general_processors:
      description:
        - "The current number of general purpose processors that are active."
      type: int
    specialty_processors:
      description:
        - "The current number of specialty processors that are active."
        - "Each item in the dictionary identifies the number of processors
           of one type of specialty processor. The key identifies the type
           of specialty processor ('aap', 'cbp', 'icf', 'ifl', 'iip', 'sap'),
           and the value is the current number of processors of that type that
           are active. Note that this number is the number of permanently
           activated processors plus the number of temporarily activated
           processors."
      type: dict
"""

import logging  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402

from ..module_utils.common import log_init, Error, ParameterError, \
    get_hmc_auth, get_session, to_unicode, process_normal_property, \
    missing_required_lib, ensure_hyphens  # noqa: E402

try:
    import requests.packages.urllib3
    IMP_URLLIB3 = True
except ImportError:
    IMP_URLLIB3 = False
    IMP_URLLIB3_ERR = traceback.format_exc()

try:
    import zhmcclient
    IMP_ZHMCCLIENT = True
except ImportError:
    IMP_ZHMCCLIENT = False
    IMP_ZHMCCLIENT_ERR = traceback.format_exc()

# Python logger name for this module
LOGGER_NAME = 'zhmc_cpc_capacity'

LOGGER = logging.getLogger(LOGGER_NAME)

# Dictionary of properties of CPC resources, in this format:
#   name: (allowed, create, update, eq_func, type_cast)
# where:
#   name: Name of the property according to the data model, with hyphens
#     replaced by underscores (this is how it is or would be specified in
#     the 'properties' module parameter).
#   allowed: Indicates whether it is allowed in the 'properties' module
#     parameter.
#   create: Not applicable for CPCs.
#   update: Indicates whether it can be specified for the "Modify CPC
#     Properties" operation (at all).
#   update_while_active: Indicates whether it can be specified for the "Modify
#     CPC Properties" operation while the CPC is active. None means
#     "not applicable" (used for update=False).
#   eq_func: Equality test function for two values of the property; None means
#     to use Python equality.
#   type_cast: Type cast function for an input value of the property; None
#     means to use it directly. This can be used for example to convert
#     integers provided as strings by Ansible back into integers (that is a
#     current deficiency of Ansible).
ZHMC_CPC_CAPACITY_PROPERTIES = {

    # update properties for any mode:
    'description': (True, None, True, True, None, to_unicode),
    'acceptable_status': (True, None, True, True, None, None),

    # update properties for classic mode:
    'next_activation_profile_name': (True, None, True, True, None, to_unicode),
    'processor_running_time_type': (True, None, True, True, None, to_unicode),
    'processor_running_time': (True, None, True, True, None, int),
    # Following property is read-only on z14 and higher:
    'does_wait_state_end_time_slice': (True, None, True, True, None, None),
    'add_temporary_capacity': (
        True, None, True, True, None, None),  # artificial property
    'remove_temporary_capacity': (
        True, None, True, True, None, None),  # artificial property

    # read-only properties (subset):
    'name': (False, None, False, None, None, None),  # provided in 'name' parm
    'object_uri': (False, None, False, None, None, None),
    'object_id': (False, None, False, None, None, None),
    'parent': (False, None, False, None, None, None),
    'class': (False, None, False, None, None, None),

    # The properties not specified here default to allow=False.
}


def process_properties(cpc, params):
    """
    Process the properties specified in the 'properties' module parameter,
    and return a dictionary (update_props) that contains the properties that
    can be updated. The input property values are compared with the existing
    resource property values and the returned set of properties is the minimal
    set of properties that need to be changed.

    - Underscores in the property names are translated into hyphens.
    - The presence of properties that cannot be updated is surfaced by raising
      ParameterError.

    Parameters:

      cpc (zhmcclient.Cpc): CPC to be updated.

      params (dict): Module input parameters.

    Returns:
      tuple with these items:
        * update_props: dict of properties for Cpc.update_properties().
        * atc_props: dict with input for Cpc.add_temporary_capacity(),
          or None if not specified.
        * rtc_props: dict with input for Cpc.remove_temporary_capacity(),
          or None if not specified.

    Raises:
      ParameterError: An issue with the module parameters.
    """

    input_props = params.get('properties', None)
    if input_props is None:
        input_props = {}

    atc_props = None
    rtc_props = None
    update_props = {}
    for prop_name in input_props:

        try:
            allowed, create, update, update_active, eq_func, type_cast = \
                ZHMC_CPC_CAPACITY_PROPERTIES[prop_name]
        except KeyError:
            allowed = False

        if not allowed:
            raise ParameterError(
                "CPC property {0!r} specified in the 'properties' module "
                "parameter cannot be updated.".format(prop_name))

        if prop_name == 'add_temporary_capacity':
            # Process this artificial property
            atc_props = ensure_hyphens(input_props[prop_name])

        elif prop_name == 'remove_temporary_capacity':
            # Process this artificial property
            rtc_props = ensure_hyphens(input_props[prop_name])

        else:
            # Process a normal (= non-artificial) property
            _create_props, _update_props, _stop = process_normal_property(
                prop_name, ZHMC_CPC_CAPACITY_PROPERTIES, input_props, cpc)
            update_props.update(_update_props)
            if _create_props:
                raise AssertionError()
            if _stop:
                raise AssertionError()

    return update_props, atc_props, rtc_props


def add_artificial_properties(cpc):
    """
    Add artificial properties to the CPC object.

    Upon return, the properties of the cpc object have been
    extended by these artificial properties:

    * 'partitions': List of partitions of the CPC, with the list subset of
      their properties.

    * 'adapters': List of adapters of the CPC, with the list subset of their
      properties.

    * 'storage-groups': List of storage groups attached to the partition, with
      the list subset of their properties.
    """
    partitions = cpc.partitions.list()
    cpc.properties['partitions'] = [p.properties for p in partitions]

    adapters = cpc.adapters.list()
    cpc.properties['adapters'] = [a.properties for a in adapters]

    storage_groups = cpc.manager.console.storage_groups.list(
        filter_args={'cpc-uri': cpc.uri})
    cpc.properties['storage-groups'] = [sg.properties
                                        for sg in storage_groups]


def ensure_set(params, check_mode):
    """
    Identify the target CPC and ensure that the specified properties are set on
    the target CPC.

    Raises:
      ParameterError: An issue with the module parameters.
      Error: Other errors during processing.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    # Note: Defaults specified in argument_spec will be set in params dict
    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['name']
    _faked_session = params.get('_faked_session', None)  # No default specified

    changed = False
    need_pull = False

    try:
        session = get_session(_faked_session, host, userid, password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        cpc.pull_full_properties()
        update_props, atc_props, rtc_props = process_properties(cpc, params)
        if update_props:
            if not check_mode:
                cpc.update_properties(update_props)
            # Some updates of CPC properties are not reflected in a new
            # retrieval of properties until after a few seconds (usually the
            # second retrieval).
            # Therefore, we construct the modified result based upon the input
            # changes, and not based upon newly retrieved properties.
            cpc.properties.update(update_props)
            changed = True

        if atc_props:
            if not check_mode:
                cpc.add_temporary_capacity(atc_props)
            need_pull = True
            changed = True

        if rtc_props:
            if not check_mode:
                cpc.remove_temporary_capacity(rtc_props)
            need_pull = True
            changed = True

        if need_pull:
            cpc.pull_full_properties()

        add_artificial_properties(cpc)

        result = cpc.properties
        return changed, result

    finally:
        session.logoff()


def facts(params, check_mode):
    """
    Identify the target CPC and return facts about the target CPC and its
    child resources.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['name']
    _faked_session = params.get('_faked_session', None)  # No default specified

    try:
        session = get_session(_faked_session, host, userid, password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        cpc.pull_full_properties()

        add_artificial_properties(cpc)

        result = cpc.properties
        return False, result

    finally:
        session.logoff()


def perform_task(params, check_mode):
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
    return actions[params['state']](params, check_mode)


def main():

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='str'),
        hmc_auth=dict(required=True, type='dict', no_log=True),
        name=dict(required=True, type='str'),
        state=dict(required=True, type='str', choices=['set', 'facts']),
        test=dict(required=False, type='bool', default=False),
        record_id=dict(required=True, type='str'),
        software_model=dict(required=False, type='str', default=None),
        specialty_processors=dict(required=False, type='dict', default={}),
        log_file=dict(required=False, type='str', default=None),
        _faked_session=dict(required=False, type='raw'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True)

    if not IMP_URLLIB3:
        module.fail_json(msg=missing_required_lib("requests"),
                         exception=IMP_URLLIB3_ERR)

    requests.packages.urllib3.disable_warnings()

    if not IMP_ZHMCCLIENT:
        module.fail_json(msg=missing_required_lib("zhmcclient"),
                         exception=IMP_ZHMCCLIENT_ERR)

    log_file = module.params['log_file']
    log_init(LOGGER_NAME, log_file)

    _params = dict(module.params)
    del _params['hmc_auth']
    LOGGER.debug("Module entry: params: %r", _params)

    try:

        changed, result = perform_task(module.params, module.check_mode)

    except (Error, zhmcclient.Error) as exc:
        # These exceptions are considered errors in the environment or in user
        # input. They have a proper message that stands on its own, so we
        # simply pass that message on and will not need a traceback.
        msg = "{0}: {1}".format(exc.__class__.__name__, exc)
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
