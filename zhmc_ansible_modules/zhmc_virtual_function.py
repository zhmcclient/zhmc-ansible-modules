#!/usr/bin/env python
# Copyright 2017 IBM Corp. All Rights Reserved.
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

from __future__ import absolute_import, print_function

import logging
from ansible.module_utils.basic import AnsibleModule
import requests.packages.urllib3
import zhmcclient

from zhmc_ansible_modules.utils import log_init, Error, ParameterError, \
    wait_for_transition_completion, eq_hex, get_hmc_auth, get_session, \
    to_unicode, process_normal_property

# For information on the format of the ANSIBLE_METADATA, DOCUMENTATION,
# EXAMPLES, and RETURN strings, see
# http://docs.ansible.com/ansible/dev_guide/developing_modules_documenting.html

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community',
    'shipped_by': 'other',
    'other_repo_url': 'https://github.com/zhmcclient/zhmc-ansible-modules'
}

DOCUMENTATION = """
---
module: zhmc_virtual_function
version_added: "0.0"
short_description: Manages virtual functions in existing partitions
description:
  - Creates, updates, and deletes virtual functions in existing partitions of a
    CPC.
  - The targeted CPC must be in the Dynamic Partition Manager (DPM) operational
    mode.
notes:
  - See also Ansible module zhmc_partition.
author:
  - Andreas Maier (@andy-maier, maiera@de.ibm.com)
  - Andreas Scheuring (@scheuran, scheuran@de.ibm.com)
  - Juergen Leopold (@leopoldjuergen, leopoldj@de.ibm.com)
requirements:
  - Network access to HMC
  - zhmcclient >=0.14.0
  - ansible >=2.2.0.0
options:
  hmc_host:
    description:
      - The hostname or IP address of the HMC.
    required: true
  hmc_auth:
    description:
      - The authentication credentials for the HMC.
    required: true
    suboptions:
      userid:
        description:
          - The userid (username) for authenticating with the HMC.
        required: true
      password:
        description:
          - The password for authenticating with the HMC.
        required: true
  cpc_name:
    description:
      - The name of the CPC with the partition containing the virtual function.
    required: true
  partition_name:
    description:
      - The name of the partition containing the virtual function.
    required: true
  name:
    description:
      - The name of the target virtual function that is managed. If the virtual
        function needs to be created, this value becomes its name.
    required: true
  state:
    description:
      - "The desired state for the target virtual function:"
      - "C(absent): Ensures that the virtual function does not exist in the
         specified partition."
      - "C(present): Ensures that the virtual function exists in the specified
         partition and has the specified properties."
    required: true
    choices: ["absent", "present"]
  properties:
    description:
      - "Dictionary with input properties for the virtual function, for
         C(state=present). Key is the property name with underscores instead of
         hyphens, and value is the property value in YAML syntax. Integer
         properties may also be provided as decimal strings. Will be ignored
         for C(state=absent)."
      - "The possible input properties in this dictionary are the properties
         defined as writeable in the data model for Virtual Function resources
         (where the property names contain underscores instead of hyphens),
         with the following exceptions:"
      - "* C(name): Cannot be specified because the name has already been
         specified in the C(name) module parameter."
      - "* C(adapter_uri): Cannot be specified because this information is
         specified using the artificial property C(adapter_name)."
      - "* C(adapter_name): The name of the adapter that backs the target
         virtual function."
      - "Properties omitted in this dictionary will remain unchanged when the
         virtual function already exists, and will get the default value
         defined in the data model for virtual functions when the virtual
         function is being created."
    required: false
    default: No input properties
  log_file:
    description:
      - "File path of a log file to which the logic flow of this module as well
         as interactions with the HMC are logged. If null, logging will be
         propagated to the Python root logger."
    required: false
    default: null
  faked_session:
    description:
      - "A C(zhmcclient_mock.FakedSession) object that has a mocked HMC set up.
         If provided, it will be used instead of connecting to a real HMC. This
         is used for testing purposes only."
    required: false
    default: Real HMC will be used.
"""

EXAMPLES = """
---
# Note: The following examples assume that some variables named 'my_*' are set.

- name: Ensure virtual function exists in the partition
  zhmc_partition:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    partition_name: "{{ my_partition_name }}"
    name: "{{ my_vfunction_name }}"
    state: present
    properties:
      adapter_name: "ABC-123"
      description: "The accelerator adapter"
      device_number: "033F"
  register: vfunction1

- name: Ensure virtual function does not exist in the partition
  zhmc_partition:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    partition_name: "{{ my_partition_name }}"
    name: "{{ my_vfunction_name }}"
    state: absent
"""

RETURN = """
virtual_function:
  description:
    - "For C(state=absent), an empty dictionary."
    - "For C(state=present), a dictionary with the resource properties of the
       virtual function (after changes, if any). The dictionary keys are the
       exact property names as described in the data model for the resource,
       i.e. they contain hyphens (-), not underscores (_). The dictionary
       values are the property values using the Python representations
       described in the documentation of the zhmcclient Python package."
  returned: success
  type: dict
  sample: |
    C({
      "name": "vfunction-1",
      "description": "virtual function #1",
      "adapter-uri': "/api/adapters/...",
      ...
    })
"""

# Python logger name for this module
LOGGER_NAME = 'zhmc_virtual_function'

LOGGER = logging.getLogger(LOGGER_NAME)

# Dictionary of properties of virtual function resources, in this format:
#   name: (allowed, create, update, update_while_active, eq_func, type_cast)
# where:
#   name: Name of the property according to the data model, with hyphens
#     replaced by underscores (this is how it is or would be specified in
#     the 'properties' module parameter).
#   allowed: Indicates whether it is allowed in the 'properties' module
#     parameter.
#   create: Indicates whether it can be specified for the "Create Virtual
#     Function" operation.
#   update: Indicates whether it can be specified for the "Update Virtual
#     Function Properties" operation (at all).
#   update_while_active: Indicates whether it can be specified for the "Update
#     Virtual Function Properties" operation while the partition of the
#     virtual function is active. None means "not applicable" (i.e.
#     update=False).
#   eq_func: Equality test function for two values of the property; None means
#     to use Python equality.
#   type_cast: Type cast function for an input value of the property; None
#     means to use it directly. This can be used for example to convert
#     integers provided as strings by Ansible back into integers (that is a
#     current deficiency of Ansible).
ZHMC_VFUNCTION_PROPERTIES = {

    # create+update properties:
    'name': (
        False, True, True, True, None, None),  # provided in 'name' module parm
    'description': (True, True, True, True, None, to_unicode),
    'device_number': (True, True, True, True, eq_hex, None),
    'adapter_uri': (
        False, True, True, True, None, None),  # via adapter_name
    'adapter_name': (
        True, True, True, True, None,
        None),  # artificial property, type_cast ignored

    # read-only properties:
    'element-uri': (False, False, False, None, None, None),
    'element-id': (False, False, False, None, None, None),
    'parent': (False, False, False, None, None, None),
    'class': (False, False, False, None, None, None),
}


def process_properties(partition, vfunction, params):
    """
    Process the properties specified in the 'properties' module parameter,
    and return two dictionaries (create_props, update_props) that contain
    the properties that can be created, and the properties that can be updated,
    respectively. If the resource exists, the input property values are
    compared with the existing resource property values and the returned set
    of properties is the minimal set of properties that need to be changed.

    - Underscores in the property names are translated into hyphens.
    - The presence of read-only properties, invalid properties (i.e. not
      defined in the data model for partitions), and properties that are not
      allowed because of restrictions or because they are auto-created from
      an artificial property is surfaced by raising ParameterError.
    - The properties resulting from handling artificial properties are
      added to the returned dictionaries.

    Parameters:

      partition (zhmcclient.Partition): Partition containing the virtual
        function. Must exist.

      vfunction (zhmcclient.VirtualFunction): Virtual function to be updated
        with the full set of current properties, or `None` if it did not
        previously exist.

      params (dict): Module input parameters.

    Returns:
      tuple of (create_props, update_props, stop), where:
        * create_props: dict of properties for
          zhmcclient.VirtualFunctionManager.create()
        * update_props: dict of properties for
          zhmcclient.VirtualFunction.update_properties()
        * stop (bool): Indicates whether some update properties require the
          partition containg the virtual function to be stopped when doing the
          update.

    Raises:
      ParameterError: An issue with the module parameters.
    """
    create_props = {}
    update_props = {}
    stop = False

    # handle 'name' property
    vfunction_name = to_unicode(params['name'])
    create_props['name'] = vfunction_name
    # We looked up the virtual function by name, so we will never have to
    # update its name

    # Names of the artificial properties
    adapter_name_art_name = 'adapter_name'

    # handle the other properties
    input_props = params.get('properties', {})
    if input_props is None:
        input_props = {}
    for prop_name in input_props:

        if prop_name not in ZHMC_VFUNCTION_PROPERTIES:
            raise ParameterError(
                "Property {!r} is not defined in the data model for "
                "virtual functions.".format(prop_name))

        allowed, create, update, update_while_active, eq_func, type_cast = \
            ZHMC_VFUNCTION_PROPERTIES[prop_name]

        if not allowed:
            raise ParameterError(
                "Property {!r} is not allowed in the 'properties' module "
                "parameter.".format(prop_name))

        if prop_name == adapter_name_art_name:
            # Artificial properties will be processed together after this loop
            continue

        # Process a normal (= non-artificial) property
        _create_props, _update_props, _stop = process_normal_property(
            prop_name, ZHMC_VFUNCTION_PROPERTIES, input_props, vfunction)
        create_props.update(_create_props)
        update_props.update(_update_props)
        if _stop:
            stop = True

    # Process artificial properties
    if adapter_name_art_name in input_props:
        adapter_name = to_unicode(input_props[adapter_name_art_name])
        try:
            adapter = partition.manager.cpc.adapters.find(
                name=adapter_name)
        except zhmcclient.NotFound:
            raise ParameterError(
                "Artificial property {!r} does not specify the name of an "
                "existing adapter: {!r}".
                format(adapter_name_art_name, adapter_name))

        # Here we perform the same logic as in the property loop, just now
        # simplified by the knowledge about the property flags (create, update,
        # etc.).
        hmc_prop_name = 'adapter-uri'
        input_prop_value = adapter.uri
        if vfunction:
            if vfunction.properties.get(hmc_prop_name) != input_prop_value:
                update_props[hmc_prop_name] = input_prop_value
        else:
            update_props[hmc_prop_name] = input_prop_value
        create_props[hmc_prop_name] = input_prop_value

    return create_props, update_props, stop


def ensure_present(params, check_mode):
    """
    Ensure that the virtual function exists and has the specified properties.

    Raises:
      ParameterError: An issue with the module parameters.
      StatusError: An issue with the partition status.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['cpc_name']
    partition_name = params['partition_name']
    vfunction_name = params['name']
    faked_session = params.get('faked_session', None)

    changed = False
    result = {}

    try:
        session = get_session(faked_session, host, userid, password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        try:
            partition = cpc.partitions.find(name=partition_name)
        except zhmcclient.NotFound:
            if check_mode:
                # Once the partition is created, the virtual function  will
                # also need to be created. Therefore, we set changed.
                changed = True
                return changed, result
            raise

        try:
            vfunction = partition.virtual_functions.find(name=vfunction_name)
            vfunction.pull_full_properties()
        except zhmcclient.NotFound:
            vfunction = None

        if not vfunction:
            # It does not exist. Create it and update it if there are
            # update-only properties.
            if not check_mode:
                create_props, update_props, stop = process_properties(
                    partition, vfunction, params)
                vfunction = partition.virtual_functions.create(create_props)
                update2_props = {}
                for name in update_props:
                    if name not in create_props:
                        update2_props[name] = update_props[name]
                if update2_props:
                    vfunction.update_properties(update2_props)
                # We refresh the properties after the update, in case an
                # input property value gets changed (for example, the
                # partition does that with memory properties).
                vfunction.pull_full_properties()
            else:
                # TODO: Show props in module result also in check mode.
                pass
            changed = True
        else:
            # It exists. Stop the partition if needed due to the virtual
            # function property update requirements, or wait for an updateable
            # partition status, and update the virtual function properties.
            create_props, update_props, stop = process_properties(
                partition, vfunction, params)
            if update_props:
                if not check_mode:
                    # Virtual function properties can all be updated while the
                    # partition is active, therefore:
                    assert not stop
                    wait_for_transition_completion(partition)
                    vfunction.update_properties(update_props)
                    # We refresh the properties after the update, in case an
                    # input property value gets changed (for example, the
                    # partition does that with memory properties).
                    vfunction.pull_full_properties()
                else:
                    # TODO: Show updated props in mod.result also in chk.mode
                    pass
                changed = True

        if vfunction:
            result = vfunction.properties

        return changed, result

    finally:
        session.logoff()


def ensure_absent(params, check_mode):
    """
    Ensure that the virtual function does not exist.

    Raises:
      ParameterError: An issue with the module parameters.
      StatusError: An issue with the partition status.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['cpc_name']
    partition_name = params['partition_name']
    vfunction_name = params['name']
    faked_session = params.get('faked_session', None)

    changed = False
    result = {}

    try:
        session = get_session(faked_session, host, userid, password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        partition = cpc.partitions.find(name=partition_name)
        # The default exception handling is sufficient for the above.

        try:
            vfunction = partition.virtual_functions.find(name=vfunction_name)
        except zhmcclient.NotFound:
            return changed, result

        if not check_mode:
            vfunction.delete()
        changed = True

        return changed, result

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
      StatusError: An issue with the partition status.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """
    actions = {
        "absent": ensure_absent,
        "present": ensure_present,
    }
    return actions[params['state']](params, check_mode)


def main():

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='str'),
        hmc_auth=dict(required=True, type='dict', no_log=True),
        cpc_name=dict(required=True, type='str'),
        partition_name=dict(required=True, type='str'),
        name=dict(required=True, type='str'),
        state=dict(required=True, type='str',
                   choices=['absent', 'present']),
        properties=dict(required=False, type='dict', default={}),
        log_file=dict(required=False, type='str', default=None),
        faked_session=dict(required=False, type='object'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True)

    log_file = module.params['log_file']
    log_init(LOGGER_NAME, log_file)

    _params = dict(module.params)
    del _params['hmc_auth']
    LOGGER.debug("Module entry: params: {!r}".format(_params))

    try:

        changed, result = perform_task(module.params, module.check_mode)

    except (Error, zhmcclient.Error) as exc:
        # These exceptions are considered errors in the environment or in user
        # input. They have a proper message that stands on its own, so we
        # simply pass that message on and will not need a traceback.
        msg = "{}: {}".format(exc.__class__.__name__, exc)
        LOGGER.debug(
            "Module exit (failure): msg: {!r}".
            format(msg))
        module.fail_json(msg=msg)
    # Other exceptions are considered module errors and are handled by Ansible
    # by showing the traceback.

    LOGGER.debug(
        "Module exit (success): changed: {!r}, cpc: {!r}".
        format(changed, result))
    module.exit_json(changed=changed, virtual_function=result)


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings()
    main()
