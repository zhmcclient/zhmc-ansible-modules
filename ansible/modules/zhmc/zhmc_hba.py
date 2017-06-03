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

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.zhmc.utils import ParameterError, StatusError
import requests.packages.urllib3
import zhmcclient

# For information on the format of the ANSIBLE_METADATA, DOCUMENTATION,
# EXAMPLES, and RETURN strings, see
# http://docs.ansible.com/ansible/dev_guide/developing_modules_documenting.html

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = """
---
module: zhmc_hba
version_added:
short_description: Manages HBAs in an existing partition
description:
  - Creates, updates, and deletes HBAs in existing partitions.
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
  - zhmcclient >=0.13.0
options:
  hmc_host:
    description:
      - The hostname or IP address of the HMC managing the CPC with the
        partition containing the target HBA.
    required: true
    type: string
  hmc_userid:
    description:
      - The userid for authenticating with the HMC.
    required: true
    type: string
  hmc_password:
    description:
      - The password of the userid for authenticating with the HMC.
    required: true
    type: string
  cpc_name:
    description:
      - The name of the CPC with the partition containing the HBA.
    required: true
    type: string
  partition_name:
    description:
      - The name of the partition containing the HBA.
    required: true
    type: string
  name:
    description:
      - The name of the target HBA that is managed. If the HBA needs to be
        created, this value becomes its name.
    required: true
    type: string
  state:
    description:
      - "The desired state for the target HBA:"
      - "C(absent): Ensures that the HBA does not exist in the specified
         partition."
      - "C(present): Ensures that the HBA exists in the specified partition
         and has the specified properties."
    required: true
    type: string
    choices: ["absent", "present"]
  properties:
    description:
      - "Input properties for the HBA, for C(state=present).
         Will be ignored for C(state=absent)."
      - "The possible input properties in this dictionary are:"
      - "The properties defined as writeable in the data model for HBA
         resources, where the property names contain underscores instead of
         hyphens."
      - "C(name): Cannot be specified because the name has already been
         specified in the C(name) module parameter."
      - "C(adapter_port_uri): Cannot be specified because it is derived from
         the artificial properties C(adapter_name) and C(adapter_port_index)."
      - "C(adapter_name): The name of the adapter that has the port backing the
         target HBA. Cannot be changed after the HBA exists."
      - "C(adapter_port_index): The index of the adapter port backing the
         target HBA. Cannot be changed after the HBA exists."
      - "Properties omitted in this dictionary will remain unchanged when the
         HBA already exists, and will get the default value defined in the
         data model for HBAs when the HBA is being created."
    required: false
    type: dict
    default: No input properties
"""

EXAMPLES = """
---

- name: Ensure HBA 1 exists in the partition
  zhmc_partition:
    hmc_host: "{{ hmc_host }}"
    hmc_userid: "{{ hmc_userid }}"
    hmc_password: "{{ hmc_password }}"
    cpc_name: "{{ cpc_name }}"
    partition_name: zhmc-part-1
    name: hba-1
    state: present
    properties:
      adapter_name: FCP-1
      adapter_port_index: 0
      description: "The port to our V7K #1"
      device_number: "123F"
  register: hba1

- name: Ensure HBA 2 does not exist in the partition
  zhmc_partition:
    hmc_host: "{{ hmc_host }}"
    hmc_userid: "{{ hmc_userid }}"
    hmc_password: "{{ hmc_password }}"
    cpc_name: "{{ cpc_name }}"
    partition_name: zhmc-part-1
    name: hba-2
    state: absent
"""

RETURN = """
hba:
  description:
    - "For C(state=absent), empty."
    - "For C(state=present), the resource properties of the HBA (after changes,
       if any)."
    - "The dictionary keys are the exact property names as described in the
       data model for the resource, i.e. they contain hyphens (-), not
       underscores (_). The dictionary values are the property values using the
       Python representations described in the documentation of the zhmcclient
       Python package."
  returned: success
  type: dict
  sample: |
    C({
      "name": "part-1",
      "description": "partition #1",
      "status": "active",
      "boot-device": "storage-adapter",
      # . . .
    })
"""

# Dictionary of properties of partition resources, in this format:
#   name: (allowed?, create?, update?, update-while-active?)
# where:
#   name: Name of the property according to the data model, with hyphens
#     replaced by underscores (this is how it is or would be specified in
#     the 'properties' module parameter).
#   allowed?: Is it allowed in the 'properties' module parameter?
#   create?: Can it be specified for the "Create Partition" operation?
#   update?: Can it be specified for the "Update Partition Properties"
#     operation (at all)?
#   update-while-active?: Can it be be specified for the "Update Partition
#     Properties" operation while the partition is active?
ZHMC_HBA_PROPERTIES = {

    # create-only properties:
    'adapter_port_uri': (False, True, False, None),  # via artificial props
    'adapter_name': (True, True, False, None),  # artificial prop
    'adapter_port_index': (True, True, False, None),  # artificial prop

    # create+update properties:
    'name': (False, True, True, True),  # provided in 'name' module parameter
    'description': (True, True, True, True),
    'device_number': (True, True, True, True),

    # read-only properties:
    'element-uri': (False, False, False, None),
    'element-id': (False, False, False, None),
    'parent': (False, False, False, None),
    'class': (False, False, False, None),
    'wwpn': (False, False, False, None),
}


def process_properties(partition, hba, params):
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

      partition (zhmcclient.Partition): Partition containing the HBA. Must
        exist.

      hba (zhmcclient.Hba): HBA to be updated with the full set of current
        properties, or `None` if it did not previously exist.

      params (dict): Module input parameters.

    Returns:
      tuple of (create_props, update_props, stop), where:
        * create_props: dict of properties for
          zhmcclient.HbaManager.create()
        * update_props: dict of properties for
          zhmcclient.Hba.update_properties()
        * stop (bool): Indicates whether some update properties require the
          partition containg the HBA to be stopped when doing the update.

    Raises:
      ParameterError: An issue with the module parameters.
    """
    create_props = {}
    update_props = {}
    stop = False

    # handle 'name' property
    hba_name = params['name']
    create_props['name'] = hba_name
    # We looked up the HBA by name, so we will never have to update its name

    # Names of the artificial properties
    adapter_name_art_name = 'adapter_name'
    port_index_art_name = 'adapter_port_index'

    # handle the other properties
    input_props = params['properties']
    for prop_name in input_props:

        if prop_name not in ZHMC_HBA_PROPERTIES:
            raise ParameterError(
                "Property {!r} is not defined in the data model for "
                "HBAs.".format(prop_name))

        allowed, create, update, update_while_active = \
            ZHMC_HBA_PROPERTIES[prop_name]

        if not allowed:
            raise ParameterError(
                "Property {!r} is not allowed in the 'properties' module "
                "parameter.".format(prop_name))

        # Double check that read-only properties are all marked as not allowed:
        assert (create or update) is True

        if prop_name in (adapter_name_art_name, port_index_art_name):
            # Artificial properties will be processed together after this loop
            continue

        # Process a normal (= non-artificial) property
        hmc_prop_name = prop_name.replace('_', '-')
        input_prop_value = input_props[prop_name]
        if not hba or hba.properties[hmc_prop_name] != input_prop_value:
            if create:
                create_props[hmc_prop_name] = input_prop_value
            if update:
                update_props[hmc_prop_name] = input_prop_value
            if not update_while_active:
                stop = True

    # Process artificial properties
    if (adapter_name_art_name in input_props) != \
            (port_index_art_name in input_props):
        raise ParameterError(
            "Artificial properties {!r} and {!r} must either both be "
            "specified or both be omitted.".
            format(adapter_name_art_name, port_index_art_name))
    if adapter_name_art_name in input_props and \
            port_index_art_name in input_props:
        adapter_name = input_props[adapter_name_art_name]
        port_index = input_props[port_index_art_name]
        try:
            adapter = partition.manager.cpc.adapters.find(
                name=adapter_name)
        except zhmcclient.NotFound:
            raise ParameterError(
                "Artificial property {!r} does not name an existing "
                "adapter: {!r}".format(adapter_name_art_name, adapter_name))
        try:
            port = adapter.ports.find(index=port_index)
        except zhmcclient.NotFound:
            raise ParameterError(
                "Artificial property {!r} does not name an existing port on "
                "adapter {!r}: {!r}".
                format(port_index_art_name, adapter_name, port_index))
        hmc_prop_name = 'adapter-port-uri'
        if hba:
            existing_port_uri = hba.get_property(hmc_prop_name)
            if port.uri != existing_port_uri:
                raise ParameterError(
                    "Artificial properties {!r} and {!r} cannot be used to "
                    "change the adapter port {!r} in an existing HBA to: {!r}".
                    format(adapter_name_art_name, port_index_art_name,
                           existing_port_uri, port.uri))
        create_props[hmc_prop_name] = port.uri

    return create_props, update_props, stop


def ensure_present(params, check_mode):
    """
    Ensure that the HBA exists and has the specified properties.

    Raises:
      ParameterError: An issue with the module parameters.
      StatusError: An issue with the partition status.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    hmc = params['hmc_host']
    userid = params['hmc_userid']
    password = params['hmc_password']
    cpc_name = params['cpc_name']
    partition_name = params['partition_name']
    hba_name = params['name']

    changed = False
    result = {}

    try:
        session = zhmcclient.Session(hmc, userid, password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        partition = cpc.partitions.find(name=partition_name)
        # The default exception handling is sufficient for the above.

        try:
            hba = partition.hbas.find(name=hba_name)
            hba.pull_full_properties()
        except zhmcclient.NotFound:
            hba = None

        if not hba:
            # It does not exist. Create it and update it if there are
            # update-only properties.

            if not check_mode:
                create_props, update_props, stop = process_properties(
                    partition, hba, params)
                hba = partition.hbas.create(create_props)
                update2_props = {}
                for name in update_props:
                    if name not in create_props:
                        update2_props[name] = update_props[name]
                if update2_props:
                    hba.update_properties(update2_props)
            changed = True
        else:
            # It exists, update its properties.

            create_props, update_props, stop = process_properties(
                partition, hba, params)
            # A need for partition stop is not yet supported. It is not needed
            # according to the current property definitions, though.
            if update_props:
                if not check_mode:
                    hba.update_properties(update_props)
                changed = True

        if hba:
            result = hba.properties

        return changed, result

    finally:
        session.logoff()


def ensure_absent(params, check_mode):
    """
    Ensure that the HBA does not exist.

    Raises:
      ParameterError: An issue with the module parameters.
      StatusError: An issue with the partition status.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    hmc = params['hmc_host']
    userid = params['hmc_userid']
    password = params['hmc_password']
    cpc_name = params['cpc_name']
    partition_name = params['partition_name']
    hba_name = params['name']

    changed = False
    result = {}

    try:
        session = zhmcclient.Session(hmc, userid, password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        partition = cpc.partitions.find(name=partition_name)
        # The default exception handling is sufficient for the above.

        try:
            hba = partition.hbas.find(name=hba_name)
        except zhmcclient.NotFound:
            return changed, result

        if not check_mode:
            hba.delete()
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

    # The following definition of module parameters must match the description
    # of the options in the DOCUMENTATION string.
    module_param_spec = {
        'hmc_host': {
            'required': True,
            'type': 'str',
        },
        'hmc_userid': {
            'required': True,
            'type': 'str',
        },
        'hmc_password': {
            'required': True,
            'type': 'str',
            'no_log': True,
        },
        'cpc_name': {
            'required': True,
            'type': 'str',
        },
        'partition_name': {
            'required': True,
            'type': 'str',
        },
        'name': {
            'required': True,
            'type': 'str',
        },
        'state': {
            'required': True,
            'type': 'str',
            'choices': ['absent', 'present'],
        },
        'properties': {
            'required': False,
            'type': 'dict',
            'default': {},
        },
    }

    module = AnsibleModule(
        argument_spec=module_param_spec,
        supports_check_mode=True)

    try:

        changed, result = perform_task(module.params, module.check_mode)

    except (ParameterError, StatusError, zhmcclient.Error) as exc:
        # These exceptions are considered errors in the environment or in user
        # input. They have a proper message that stands on its own, so we
        # simply pass that message on and will not need a traceback.
        msg = "{}: {}".format(exc.__class__.__name__, exc)
        module.fail_json(msg=msg)
    # Other exceptions are considered module errors and are handled by Ansible
    # by showing the traceback.

    module.exit_json(changed=changed, partition=result)


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings()
    main()
