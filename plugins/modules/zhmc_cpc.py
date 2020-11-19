#!/usr/bin/python
# Copyright 2018-2020 IBM Corp. All Rights Reserved.
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
module: zhmc_cpc
version_added: "0.6.0"
short_description: Update CPCs
description:
  - Gather facts about a CPC (Z system), including its adapters and partitions.
  - Update the properties of a CPC.
author:
  - Andreas Maier (@andy-maier)
  - Andreas Scheuring (@scheuran)
requirements:
  - Access to the WS API of the HMC of the targeted Z system
    (see :term:`HMC API`). The targeted Z system must be in the Dynamic
    Partition Manager (DPM) operational mode
  - Python package zhmcclient >=0.20.0
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
      - "The desired state for the attachment:"
      - "* C(set): Ensures that the CPC has the specified properties."
      - "* C(facts): Does not change anything on the CPC and returns
         the CPC properties including its child resources."
    type: str
    required: true
    choices: ['set', 'facts']
  properties:
    description:
      - "Only for C(state=set): New values for the properties of the CPC.
         Properties omitted in this dictionary will remain unchanged.
         This parameter will be ignored for C(state=facts)."
      - "The parameter is a dictionary. The key of each dictionary item is the
         property name as specified in the data model for CPC resources, with
         underscores instead of hyphens. The value of each dictionary item is
         the property value (in YAML syntax). Integer properties may also be
         provided as decimal strings."
      - "The possible properties in this dictionary are the properties
         defined as writeable in the data model for CPC resources."
    type: dict
    required: false
    default: null
  log_file:
    description:
      - "File path of a log file to which the logic flow of this module as well
         as interactions with the HMC are logged. If null, logging will be
         propagated to the Python root logger."
    type: str
    required: false
    default: null
  faked_session:
    description:
      - "A C(zhmcclient_mock.FakedSession) object that has a mocked HMC set up.
         If not null, this session will be used instead of connecting to the
         HMC specified in C(hmc_host). This is used for testing purposes only."
    required: false
    type: raw
    default: null
"""

EXAMPLES = """
---
# Note: The following examples assume that some variables named 'my_*' are set.

- name: Gather facts about the CPC
  zhmc_cpc:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_cpc_name }}"
    state: facts
  register: cpc1

- name: Ensure the CPC has the desired property values
  zhmc_cpc:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_cpc_name }}"
    state: set
    properties:
      acceptable_status:
       - active
      description: "This is CPC {{ my_cpc_name }}"

"""

RETURN = """
cpc:
  description: "A dictionary with the properties of the CPC, including
    additional artificial properties as described below."
  returned: success
  type: dict
  contains:
    name:
      description: "CPC name"
      type: str
    "{property}":
      description: "Additional properties of the CPC, as described in the
       :term:`HMC API` (using hyphens (-) in the property names)."
    partitions:
      description: "Artificial property for the defined partitions of the CPC,
        with a subset of its properties."
      type: dict
      contains:
        "{name}":
          description: "Partition name"
          type: dict
          contains:
            name:
              description: "Partition name"
              type: str
            status:
              description: "Status of the partition"
              type: str
            object_uri:
              description: "Canonical URI of the partition"
              type: str
    adapters:
      description: "Artificial property for the adapters of the CPC,
        with a subset of its properties."
      type: dict
      contains:
        "{name}":
          description: "Adapter name"
          type: dict
          contains:
            name:
              description: "Adapter name"
              type: str
            status:
              description: "Status of the adapter"
              type: str
            object_uri:
              description: "Canonical URI of the adapter"
              type: str
    storage-groups:
      description: "Artificial property for the storage groups associated with
        the CPC, with a subset of its properties."
      type: dict
      contains:
        "{name}":
          description: "Storage group name"
          type: dict
          contains:
            name:
              description: "Storage group name"
              type: str
            fulfillment-status:
              description: "Fulfillment status of the storage group"
              type: str
            object_uri:
              description: "Canonical URI of the storage group"
              type: str
"""

import logging  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402

from ..module_utils.common import log_init, Error, ParameterError, \
    get_hmc_auth, get_session, to_unicode, process_normal_property, \
    missing_required_lib  # noqa: E402

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
LOGGER_NAME = 'zhmc_cpc'

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
ZHMC_CPC_PROPERTIES = {

    # update properties:
    'description': (True, None, True, True, None, to_unicode),
    'acceptable_status': (True, None, True, True, None, None),

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
      update_props: dict of properties for zhmcclient.Cpc.update_properties()

    Raises:
      ParameterError: An issue with the module parameters.
    """

    input_props = params.get('properties', None)
    if input_props is None:
        input_props = {}

    update_props = {}
    for prop_name in input_props:

        try:
            allowed, create, update, update_active, eq_func, type_cast = \
                ZHMC_CPC_PROPERTIES[prop_name]
        except KeyError:
            allowed = False

        if not allowed:
            raise ParameterError(
                "CPC property {0!r} specified in the 'properties' module "
                "parameter cannot be updated.".format(prop_name))

        # Process a normal (= non-artificial) property
        _create_props, _update_props, _stop = process_normal_property(
            prop_name, ZHMC_CPC_PROPERTIES, input_props, cpc)
        update_props.update(_update_props)
        if _create_props:
            raise AssertionError()
        if _stop:
            raise AssertionError()

    return update_props


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
    faked_session = params.get('faked_session', None)  # No default specified

    changed = False

    try:
        session = get_session(faked_session, host, userid, password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        cpc.pull_full_properties()
        update_props = process_properties(cpc, params)
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
    faked_session = params.get('faked_session', None)  # No default specified

    try:
        session = get_session(faked_session, host, userid, password)
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
        properties=dict(required=False, type='dict', default={}),
        log_file=dict(required=False, type='str', default=None),
        faked_session=dict(required=False, type='raw'),
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
