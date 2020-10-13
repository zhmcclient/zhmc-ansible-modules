#!/usr/bin/env python
# Copyright 2018 IBM Corp. All Rights Reserved.
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
    get_hmc_auth, get_session, to_unicode, process_normal_property

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
module: zhmc_storage_group
version_added: "0.5"
short_description: Manages DPM storage groups (with "dpm-storage-management"
    feature)
description:
  - Gathers facts about a storage group associated with a CPC, including its
    storage volumes and virtual storage resources.
  - Creates, deletes and updates a storage group associated with a CPC.
notes:
  - The CPC that is associated with the target storage group must be in the
    Dynamic Partition Manager (DPM) operational mode and must have the
    "dpm-storage-management" firmware feature enabled.
    That feature has been introduced with the z14-ZR1 / Rockhopper II machine
    generation.
  - This module performs actions only against the Z HMC regarding the
    definition of storage group objects and their attachment to partitions.
    This module does not perform any actions against storage subsystems or
    SAN switches.
  - Attachment of a storage group to and from partitions is managed by the
    Ansible module zhmc_storage_group_attachment.
  - The Ansible module zhmc_hba is no longer used on CPCs that have the
    "dpm-storage-management" feature enabled.
author:
  - Andreas Maier (@andy-maier, maiera@de.ibm.com)
  - Andreas Scheuring (@scheuran, scheuran@de.ibm.com)
  - Juergen Leopold (@leopoldjuergen, leopoldj@de.ibm.com)
requirements:
  - Network access to HMC
  - zhmcclient >=0.20.0
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
      - The name of the CPC associated with the target storage group.
    required: true
  name:
    description:
      - The name of the target storage group.
    required: true
  state:
    description:
      - "The desired state for the target storage group:"
      - "* C(absent): Ensures that the storage group does not exist. If the
         storage group is currently attached to any partitions, the module will
         fail."
      - "* C(present): Ensures that the storage group exists and is associated
         with the specified CPC, and has the specified properties. The
         attachment state of the storage group to a partition is not changed."
      - "* C(facts): Does not change anything on the storage group and returns
         the storage group properties."
    required: true
    choices: ['absent', 'present', 'facts']
  properties:
    description:
      - "Dictionary with desired properties for the storage group.
         Used for C(state=present); ignored for C(state=absent|facts).
         Dictionary key is the property name with underscores instead
         of hyphens, and dictionary value is the property value in YAML syntax.
         Integer properties may also be provided as decimal strings."
      - "The possible input properties in this dictionary are the properties
         defined as writeable in the data model for Storage Group resources
         (where the property names contain underscores instead of hyphens),
         with the following exceptions:"
      - "* C(name): Cannot be specified because the name has already been
         specified in the C(name) module parameter."
      - "* C(type): Cannot be changed once the storage group exists."
      - "Properties omitted in this dictionary will remain unchanged when the
         storage group already exists, and will get the default value defined
         in the data model for storage groups in the HMC API book when the
         storage group is being created."
    required: false
    default: No properties.
  expand:
    description:
      - "Boolean that controls whether the returned storage group contains
         additional artificial properties that expand certain URI or name
         properties to the full set of resource properties (see description of
         return values of this module)."
    required: false
    type: bool
    default: false
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

- name: Gather facts about a storage group
  zhmc_storage_group:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    name: "{{ my_storage_group_name }}"
    state: facts
    expand: true
  register: sg1

- name: Ensure the storage group does not exist
  zhmc_storage_group:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    name: "{{ my_storage_group_name }}"
    state: absent

- name: Ensure the storage group exists
  zhmc_storage_group:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    name: "{{ my_storage_group_name }}"
    state: present
    expand: true
    properties:
      description: "Example storage group 1"
      type: fcp
      shared: false
      connectivity: 4
      max-partitions: 1
  register: sg1

"""

RETURN = """
storage_group:
  description:
    - "For C(state=absent), an empty dictionary."
    - "For C(state=present|facts), a
       dictionary with the resource properties of the target storage group,
       plus additional artificial properties as described in the following
       list items.
       The dictionary keys are the exact property names as described in the
       data model for the resource, i.e. they contain hyphens (-), not
       underscores (_). The dictionary values are the property values using the
       Python representations described in the documentation of the zhmcclient
       Python package.
       The additional artificial properties are:"
    - "* C(attached-partition-names): List of partition names to which the
       storage group is attached."
    - "* C(cpc-name): Name of the CPC that is associated to this storage
       group."
    - "* C(candidate-adapter-ports) (only if expand was requested):
       List of candidate adapter ports of the storage group. Each port is
       represented as a dictionary of its properties; in addition each port has
       an artificial property C(parent-adapter) which represents the adapter of
       the port. Each adapter is represented as a dictionary of its
       properties."
    - "* C(storage-volumes) (only if expand was requested):
       List of storage volumes of the storage group. Each storage volume is
       represented as a dictionary of its properties."
    - "* C(virtual-storage-resources) (only if expand was requested):
       List of virtual storage resources of the storage group. Each virtual
       storage resource is represented as a dictionary of its properties."
    - "* C(attached-partitions) (only if expand was requested):
       List of partitions to which the storage group is attached. Each
       partition is represented as a dictionary of its properties."
    - "* C(cpc) (only if expand was requested): The CPC that is associated to
       this storage group. The CPC is represented as a dictionary of its
       properties."
  returned: success
  type: dict
  sample: |
    C({
      "name": "sg-1",
      "description": "storage group #1",
      ...
    })
"""

# Python logger name for this module
LOGGER_NAME = 'zhmc_storage_group'

LOGGER = logging.getLogger(LOGGER_NAME)

# Dictionary of properties of storage group resources, in this format:
#   name: (allowed, create, update, eq_func, type_cast)
# where:
#   name: Name of the property according to the data model, with hyphens
#     replaced by underscores (this is how it is or would be specified in
#     the 'properties' module parameter).
#   allowed: Indicates whether it is allowed in the 'properties' module
#     parameter.
#   create: Indicates whether it can be specified for the "Create Storage
#     Group" operation.
#   update: Indicates whether it can be specified for the "Modify Storage
#     Group Properties" operation (at all).
#   update_while_active: Indicates whether it can be specified for the "Modify
#     Storage Group Properties" operation while the storage group is attached
#     to any partition. None means "not applicable" (used for update=False).
#   eq_func: Equality test function for two values of the property; None means
#     to use Python equality.
#   type_cast: Type cast function for an input value of the property; None
#     means to use it directly. This can be used for example to convert
#     integers provided as strings by Ansible back into integers (that is a
#     current deficiency of Ansible).
ZHMC_STORAGE_GROUP_PROPERTIES = {

    # create-only properties:
    'cpc-uri': (False, True, False, None, None, None),  # auto-generated here
    'type': (True, True, False, None, None, None),

    # update-only properties: None

    # non-data model properties:
    'storage-volumes': (False, True, True, None, None, None),
    # storage-volumes is a request-info object and is not part of the data
    # model. Changes to storage volumes are performed via the
    # zhmc_storage_volume.py module.

    # create+update properties:
    'name': (False, True, True, True, None, None),
    # name: provided in 'name' module parm
    'description': (True, True, True, True, None, to_unicode),
    'shared': (True, True, True, True, None, None),
    'connectivity': (True, True, True, True, None, int),
    'max-partitions': (True, True, True, True, None, int),
    'virtual-machine-count': (True, True, True, True, None, int),
    'email-to-addresses': (True, True, True, True, None, None),
    'email-cc-addresses': (True, True, True, True, None, None),
    'email-insert': (True, True, True, True, None, None),

    # read-only properties:
    'object_uri': (False, False, False, None, None, None),
    'object_id': (False, False, False, None, None, None),
    'parent': (False, False, False, None, None, None),
    'class': (False, False, False, None, None, None),
    'fulfillment-state': (False, False, False, None, None, None),
    'storage-volume-uris': (False, False, False, None, None, None),
    # storage-volume-uris: updated via method
    'virtual-storageresource-uris': (False, False, False, None, None, None),
    'active-connectivity': (False, False, False, None, None, None),
    'active-max-partitions': (False, False, False, None, None, None),
    'candidate-adapter-port-uris': (False, False, False, None, None, None),
    # candidate-adapter-port-uris: updated via method
    'unassigned-worldwide-port-names': (False, False, False, None, None, None),
}


def process_properties(cpc, storage_group, params):
    """
    Process the properties specified in the 'properties' module parameter,
    and return two dictionaries (create_props, update_props) that contain
    the properties that can be created, and the properties that can be updated,
    respectively. If the resource exists, the input property values are
    compared with the existing resource property values and the returned set
    of properties is the minimal set of properties that need to be changed.

    - Underscores in the property names are translated into hyphens.
    - The presence of read-only properties, invalid properties (i.e. not
      defined in the data model for storage groups), and properties that are
      not allowed because of restrictions or because they are auto-created from
      an artificial property is surfaced by raising ParameterError.
    - The properties resulting from handling artificial properties are
      added to the returned dictionaries.

    Parameters:

      cpc (zhmcclient.Cpc): CPC with the partition to be updated, and
        with the adapters to be used for the partition.

      storage_group (zhmcclient.StorageGroup): Storage group object to be
        updated with the full set of current properties, or `None` if it did
        not previously exist.

      params (dict): Module input parameters.

    Returns:
      tuple of (create_props, update_props), where:
        * create_props: dict of properties for
          zhmcclient.StorageGroupManager.create()
        * update_props: dict of properties for
          zhmcclient.StorageGroup.update_properties()

    Raises:
      ParameterError: An issue with the module parameters.
    """
    create_props = {}
    update_props = {}

    # handle 'name' and 'cpc-uri' properties.
    sg_name = to_unicode(params['name'])
    if storage_group is None:
        # SG does not exist yet.
        create_props['name'] = sg_name
        create_props['cpc-uri'] = cpc.uri
    else:
        # SG does already exist.
        # We looked up the storage group by name, so we will never have to
        # update the storage group name.
        # Updates to the associated CPC are not possible.
        sg_cpc = storage_group.cpc
        if sg_cpc.uri != cpc.uri:
            raise ParameterError(
                "Storage group {!r} is not associated with the specified "
                "CPC {!r}, but with CPC {!r}.".
                format(sg_name, cpc.name, sg_cpc.name))

    # handle the other properties
    input_props = params.get('properties', None)
    if input_props is None:
        input_props = {}
    for prop_name in input_props:

        if prop_name not in ZHMC_STORAGE_GROUP_PROPERTIES:
            raise ParameterError(
                "Property {!r} is not defined in the data model for "
                "storage groups.".format(prop_name))

        allowed, create, update, update_while_active, eq_func, type_cast = \
            ZHMC_STORAGE_GROUP_PROPERTIES[prop_name]

        if not allowed:
            raise ParameterError(
                "Property {!r} is not allowed in the 'properties' module "
                "parameter.".format(prop_name))

        # Process a normal (= non-artificial) property
        _create_props, _update_props, _stop = process_normal_property(
            prop_name, ZHMC_STORAGE_GROUP_PROPERTIES, input_props,
            storage_group)
        create_props.update(_create_props)
        update_props.update(_update_props)
        assert _stop is False

    return create_props, update_props


def add_artificial_properties(storage_group, expand):
    """
    Add artificial properties to the storage_group object.

    Upon return, the properties of the storage_group object have been
    extended by these properties:

    Regardless of expand:

    * 'attached-partition-names': List of Partition names to which the storage
      group is attached.

    If expand is True:

    * 'candidate-adapter-ports': List of Port objects, each of which is
      represented as its dictionary of properties.

      The Port properties are extended by these properties:

      - 'parent-adapter': Adapter object of the port, represented as its
        dictionary of properties.

    * 'storage-volumes': List of StorageVolume objects, each of which is
      represented as its dictionary of properties.

    * 'virtual-storage-resources': List of VirtualStorageResource objects,
      each of which is represented as its dictionary of properties.

    * 'attached-partitions': List of Partition objects to which the storage
      group is attached. Each Partition object is represented as a dictionary
      of its properties.
    """

    parts = storage_group.list_attached_partitions()

    # List of attached partitions (just the names)
    part_names_prop = list()
    for part in parts:
        part_names_prop.append(part.get_property('name'))
    storage_group.properties['attached-partition-names'] = part_names_prop

    if expand:

        # Candidate adapter ports and their parent adapters (full set of props)
        caps_prop = list()
        for cap in storage_group.list_candidate_adapter_ports(
                full_properties=True):
            adapter = cap.manager.adapter
            adapter.pull_full_properties()
            cap.properties['parent-adapter'] = adapter.properties
            caps_prop.append(cap.properties)
        storage_group.properties['candidate-adapter-ports'] = caps_prop

        # Storage volumes (full set of properties).
        # Note: We create the storage volumes from the 'storage-volume-uris'
        # property, because the 'List Storage Volumes of a Storage Group'
        # operation returns an empty list for auto-discovered volumes.
        svs_prop = list()
        sv_uris = storage_group.get_property('storage-volume-uris')
        for sv_uri in sv_uris:
            sv = storage_group.storage_volumes.resource_object(sv_uri)
            sv.pull_full_properties()
            svs_prop.append(sv.properties)
        storage_group.properties['storage-volumes'] = svs_prop

        # Virtual storage resources (full set of properties).
        vsrs_prop = list()
        vsr_uris = storage_group.get_property('virtual-storage-resource-uris')
        for vsr_uri in vsr_uris:
            vsr = storage_group.virtual_storage_resources.resource_object(
                vsr_uri)
            vsr.pull_full_properties()
            vsrs_prop.append(vsr.properties)
        storage_group.properties['virtual-storage-resources'] = vsrs_prop

        # List of attached partitions (full set of properties).
        parts = storage_group.list_attached_partitions()
        parts_prop = list()
        for part in parts:
            part.pull_full_properties()
            parts_prop.append(part.properties)
        storage_group.properties['attached-partitions'] = parts_prop


def ensure_present(params, check_mode):
    """
    Ensure that the storage group exists and has the specified properties.

    Storage volumes are not subject of this function, they are handled by the
    zhmc_storage_volume.py module.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['cpc_name']
    storage_group_name = params['name']
    expand = params['expand']
    faked_session = params.get('faked_session', None)

    changed = False
    result = {}

    try:
        session = get_session(faked_session, host, userid, password)
        client = zhmcclient.Client(session)
        console = client.consoles.console
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        try:
            storage_group = console.storage_groups.find(
                name=storage_group_name)
        except zhmcclient.NotFound:
            storage_group = None

        if storage_group is None:
            # It does not exist. Create it and update it if there are
            # update-only properties.
            if not check_mode:
                create_props, update_props = \
                    process_properties(cpc, storage_group, params)
                storage_group = console.storage_groups.create(
                    create_props)
                update2_props = {}
                for name in update_props:
                    if name not in create_props:
                        update2_props[name] = update_props[name]
                if update2_props:
                    storage_group.update_properties(update2_props)
                # We refresh the properties after the update, in case an
                # input property value gets changed.
                storage_group.pull_full_properties()
            else:
                # TODO: Show props in module result also in check mode.
                pass
            changed = True
        else:
            # It exists. Update its properties.
            storage_group.pull_full_properties()
            create_props, update_props = \
                process_properties(cpc, storage_group, params)
            assert not create_props, \
                "Unexpected create_props: {!r}".format(create_props)
            if update_props:
                if not check_mode:
                    storage_group.update_properties(update_props)
                    # We refresh the properties after the update, in case an
                    # input property value gets changed.
                    storage_group.pull_full_properties()
                else:
                    # TODO: Show updated props in mod.result also in chk.mode
                    pass
                changed = True

        if not check_mode:
            assert storage_group
            add_artificial_properties(storage_group, expand)
            result = storage_group.properties

        return changed, result

    finally:
        session.logoff()


def ensure_absent(params, check_mode):
    """
    Ensure that the storage group does not exist.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['cpc_name']
    storage_group_name = params['name']
    faked_session = params.get('faked_session', None)

    changed = False
    result = {}

    try:
        session = get_session(faked_session, host, userid, password)
        client = zhmcclient.Client(session)
        console = client.consoles.console
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        try:
            storage_group = console.storage_groups.find(
                name=storage_group_name)
        except zhmcclient.NotFound:
            return changed, result

        sg_cpc = storage_group.cpc
        if sg_cpc.uri != cpc.uri:
            raise ParameterError(
                "Storage group {!r} is not associated with the specified "
                "CPC {!r}, but with CPC {!r}.".
                format(storage_group_name, cpc.name, sg_cpc.name))

        if not check_mode:
            partitions = storage_group.list_attached_partitions()
            for part in partitions:
                # This will raise HTTPError(409) if the partition is in one of
                # the transitional states ('starting', 'stopping').
                part.detach_storage_group(storage_group)
            storage_group.delete()
        changed = True

        return changed, result

    finally:
        session.logoff()


def facts(params, check_mode):
    """
    Return facts about a storage group and its storage volumes and virtual
    storage resources.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['cpc_name']
    storage_group_name = params['name']
    expand = params['expand']
    faked_session = params.get('faked_session', None)

    changed = False
    result = {}

    try:
        # The default exception handling is sufficient for this code

        session = get_session(faked_session, host, userid, password)
        client = zhmcclient.Client(session)
        console = client.consoles.console
        cpc = client.cpcs.find(name=cpc_name)

        storage_group = console.storage_groups.find(name=storage_group_name)
        storage_group.pull_full_properties()

        sg_cpc = storage_group.cpc
        if sg_cpc.uri != cpc.uri:
            raise ParameterError(
                "Storage group {!r} is not associated with the specified "
                "CPC {!r}, but with CPC {!r}.".
                format(storage_group_name, cpc.name, sg_cpc.name))

        add_artificial_properties(storage_group, expand)
        result = storage_group.properties

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
      zhmcclient.Error: Any zhmcclient exception can happen.
    """
    actions = {
        "absent": ensure_absent,
        "present": ensure_present,
        "facts": facts,
    }
    return actions[params['state']](params, check_mode)


def main():

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='str'),
        hmc_auth=dict(required=True, type='dict', no_log=True),
        cpc_name=dict(required=True, type='str'),
        name=dict(required=True, type='str'),
        state=dict(required=True, type='str',
                   choices=['absent', 'present', 'facts']),
        properties=dict(required=False, type='dict', default={}),
        expand=dict(required=False, type='bool', default=False),
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
    module.exit_json(changed=changed, storage_group=result)


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings()
    main()
