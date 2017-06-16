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
from ansible.module_utils.zhmc.utils import Error, ParameterError, \
    StatusError, stop_partition, start_partition, eq_hex
import requests.packages.urllib3
import zhmcclient

# For information on the format of the ANSIBLE_METADATA, DOCUMENTATION,
# EXAMPLES, and RETURN strings, see
# http://docs.ansible.com/ansible/dev_guide/developing_modules_documenting.html

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'core'
}

DOCUMENTATION = """
---
module: zhmc_partition
version_added: "0.0"
short_description: Manages partitions
description:
  - Creates, updates, deletes, starts, and stops partitions on z Systems and
    LinuxONE machines that are in the Dynamic Partition Manager (DPM)
    operational mode.
  - Child resources on partitions such as HBAs, NICs or virtual functions are
    managed by separate Ansible modules.
notes:
  - See also Ansible modules zhmc_hba, zhmc_nic, zhmc_virtualfunction.
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
        target partition.
    required: true
  hmc_userid:
    description:
      - The userid for authenticating with the HMC.
    required: true
  hmc_password:
    description:
      - The password of the userid for authenticating with the HMC.
    required: true
  cpc_name:
    description:
      - The name of the CPC with the target partition.
    required: true
  name:
    description:
      - The name of the target partition.
    required: true
  state:
    description:
      - "The desired state for the target partition:"
      - "C(absent): Ensures that the partition does not exist in the specified
         CPC."
      - "C(stopped): Ensures that the partition exists in the specified CPC,
         has the specified properties, and is in the 'stopped' status."
      - "C(active): Ensures that the partition exists in the specified CPC,
         has the specified properties, and is in the 'active' or 'degraded'
         status."
    required: true
    choices: ['absent', 'stopped', 'active']
  properties:
    description:
      - "Dictionary with input properties for the partition, for
         C(state=stopped) and C(state=active). Key is the property name with
         underscores instead of hyphens, and value is the property value in
         YAML syntax. Will be ignored for C(state=absent)."
      - "The possible input properties in this dictionary are:"
      - "The properties defined as writeable in the data model for partition
         resources, where the property names contain underscores instead of
         hyphens."
      - "C(name): Cannot be specified because the name has already been
         specified in the C(name) module parameter."
      - "C(type): Cannot be changed once the partition exists, because updating
         it is not supported."
      - "C(boot_storage_device): Cannot be specified because it is derived from
         the artificial property C(boot_storage_hba_name)."
      - "C(boot_network_device): Cannot be specified because it is derived from
         the artificial property C(boot_network_nic_name)."
      - "C(boot_storage_hba_name): The name of the HBA whose URI is used to
         construct C(boot_storage_device). Specifying it requires that the
         partition exists."
      - "C(boot_network_nic_name): The name of the NIC whose URI is used to
         construct C(boot_network_device). Specifying it requires that the
         partition exists."
      - "Properties omitted in this dictionary will remain unchanged when the
         partition already exists, and will get the default value defined in
         the data model for partitions in the HMC API book when the partition
         is being created."
    required: false
    default: No input properties
"""

EXAMPLES = """
---
# Note: The following examples assume that some variables named 'my_*' are set.

# Because configuring LUN masking in the SAN requires the host WWPN, and the
# host WWPN is automatically assigned and will be known only after an HBA has
# been added to the partition, the partition needs to be created in stopped
# state. Also, because the HBA has not yet been created, the boot
# configuration cannot be done yet:
- name: Ensure the partition exists and is stopped
  zhmc_partition:
    hmc_host: "{{ my_hmc_host }}"
    hmc_userid: "{{ my_hmc_userid }}"
    hmc_password: "{{ my_hmc_password }}"
    cpc_name: "{{ my_cpc_name }}"
    name: "{{ my_partition_name }}"
    state: stopped
    properties:
      description: "zhmc Ansible modules: Example partition 1"
      ifl_processors: 2
      initial_memory: 1024
      maximum_memory: 1024
  register: part1

# After an HBA has been added (see Ansible module zhmc_hba), and LUN masking
# has been configured in the SAN, and a bootable image is available at the
# configured LUN and target WWPN, the partition can be configured for boot
# from the FCP LUN and can be started:
- name: Configure boot device and start the partition
  zhmc_partition:
    hmc_host: "{{ my_hmc_host }}"
    hmc_userid: "{{ my_hmc_userid }}"
    hmc_password: "{{ my_hmc_password }}"
    cpc_name: "{{ my_cpc_name }}"
    name: "{{ my_partition_name }}"
    state: active
    properties:
      boot_device: storage-adapter
      boot_storage_device_hba_name: hba1
      boot_logical_unit_number: 00000000001
      boot_world_wide_port_name: abcdefabcdef
  register: part1

- name: Ensure the partition does not exist
  zhmc_partition:
    hmc_host: "{{ my_hmc_host }}"
    hmc_userid: "{{ my_hmc_userid }}"
    hmc_password: "{{ my_hmc_password }}"
    cpc_name: "{{ my_cpc_name }}"
    name: "{{ my_partition_name }}"
    state: absent
"""

RETURN = """
partition:
  description:
    - "For C(state=absent), empty."
    - "For C(state=stopped) and C(state=active), the resource properties of the
       partition (after changes, if any)."
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
#   name: (allowed, create, update, update_while_active, eq_func)
# where:
#   name: Name of the property according to the data model, with hyphens
#     replaced by underscores (this is how it is or would be specified in
#     the 'properties' module parameter).
#   allowed: Indicates whether it is allowed in the 'properties' module
#     parameter.
#   create: Indicates whether it can be specified for the "Create Partition"
#     operation.
#   update: Indicates whether it can be specified for the "Update Partition
#     Properties" operation (at all).
#   update_while_active: Indicates whether it can be specified for the "Update
#     Partition Properties" operation while the partition is active. None means
#     "not applicable" (i.e. update=False).
#   eq_func: Equality test function for two values of the property; None means
#     to use Python equality.
ZHMC_PARTITION_PROPERTIES = {

    # create-only properties:
    'type': (False, True, False, None, None),  # restriction not to change type

    # update-only properties:
    'boot_network_device': (False, False, True, True, None),  # via artif. prop
    'boot_network_nic_name': (True, False, True, True, None),  # artif. prop
    'boot_storage_device': (False, False, True, True, None),  # via artif. prop
    'boot_storage_hba_name': (True, False, True, True, None),  # artif. prop
    'acceptable_status': (True, False, True, True, None),
    'processor_management_enabled': (True, False, True, True, None),
    'ifl_absolute_processor_capping': (True, False, True, True, None),
    'ifl_absolute_processor_capping_value': (True, False, True, True, None),
    'ifl_processing_weight_capped': (True, False, True, True, None),
    'minimum_ifl_processing_weight': (True, False, True, True, None),
    'maximum_ifl_processing_weight': (True, False, True, True, None),
    'initial_ifl_processing_weight': (True, False, True, True, None),
    'cp_absolute_processor_capping': (True, False, True, True, None),
    'cp_absolute_processor_capping_value': (True, False, True, True, None),
    'cp_processing_weight_capped': (True, False, True, True, None),
    'minimum_cp_processing_weight': (True, False, True, True, None),
    'maximum_cp_processing_weight': (True, False, True, True, None),
    'initial_cp_processing_weight': (True, False, True, True, None),
    'boot_logical_unit_number': (True, False, True, True, eq_hex),
    'boot_world_wide_port_name': (True, False, True, True, eq_hex),
    'boot_os_specific_parameters': (True, False, True, True, None),
    'boot_iso_ins_file': (True, False, True, True, None),
    'ssc_boot_selection': (True, False, True, True, None),

    # create+update properties:
    'name': (False, True, True, True, None),  # provided in 'name' module parm
    'description': (True, True, True, True, None),
    'short_name': (True, True, True, True, None),
    'partition_id': (True, True, True, True, None),
    'autogenerate_partition_id': (True, True, True, True, None),
    'ifl_processors': (True, True, True, True, None),
    'cp_processors': (True, True, True, True, None),
    'processor_mode': (True, True, True, True, None),
    'initial_memory': (True, True, True, True, None),
    'maximum_memory': (True, True, True, True, None),
    'reserve_resources': (True, True, True, True, None),
    'boot_device': (True, True, True, True, None),
    'boot_timeout': (True, True, True, True, None),
    'boot_ftp_host': (True, True, True, True, None),
    'boot_ftp_username': (True, True, True, True, None),
    'boot_ftp_password': (True, True, True, True, None),
    'boot_ftp_insfile': (True, True, True, True, None),
    'boot_removable_media': (True, True, True, True, None),
    'boot_removable_media_type': (True, True, True, True, None),
    'boot_configuration_selector': (True, True, True, True, None),
    'boot_record_lba': (True, True, True, True, None),
    'access_global_performance_data': (True, True, True, True, None),
    'permit_cross_partition_commands': (True, True, True, True, None),
    'access_basic_counter_set': (True, True, True, True, None),
    'access_problem_state_counter_set': (True, True, True, True, None),
    'access_crypto_activity_counter_set': (True, True, True, True, None),
    'access_extended_counter_set': (True, True, True, True, None),
    'access_coprocessor_group_set': (True, True, True, True, None),
    'access_basic_sampling': (True, True, True, True, None),
    'access_diagnostic_sampling': (True, True, True, True, None),
    'permit_des_key_import_functions': (True, True, True, True, None),
    'permit_aes_key_import_functions': (True, True, True, True, None),
    'ssc_host_name': (True, True, True, True, None),
    'ssc_ipv4_gateway': (True, True, True, True, None),
    'ssc_dns_servers': (True, True, True, True, None),
    'ssc_master_userid': (True, True, True, True, None),
    'ssc_master_pw': (True, True, True, True, None),

    # read-only properties:
    'object_uri': (False, False, False, None, None),
    'object_id': (False, False, False, None, None),
    'parent': (False, False, False, None, None),
    'class': (False, False, False, None, None),
    'status': (False, False, False, None, None),
    'has_unacceptable_status': (False, False, False, None, None),
    'is_locked': (False, False, False, None, None),
    'os_name': (False, False, False, None, None),
    'os_type': (False, False, False, None, None),
    'os_version': (False, False, False, None, None),
    'degraded_adapters': (False, False, False, None, None),
    'current_ifl_processing_weight': (False, False, False, None, None),
    'current_cp_processing_weight': (False, False, False, None, None),
    'reserved_memory': (False, False, False, None, None),
    'auto_start': (False, False, False, None, None),
    'boot_iso_image_name': (False, False, False, None, None),
    'threads_per_processor': (False, False, False, None, None),
    'virtual_function_uris': (False, False, False, None, None),
    'nic_uris': (False, False, False, None, None),
    'hba_uris': (False, False, False, None, None),
    'crypto_configuration': (False, False, False, None, None),
}


def process_properties(partition, params):
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

      partition (zhmcclient.Partition): Partition to be updated with the full
        set of current properties, or `None` if it did not previously exist.

      params (dict): Module input parameters.

    Returns:
      tuple of (create_props, update_props, stop), where:
        * create_props: dict of properties for
          zhmcclient.PartitionManager.create()
        * update_props: dict of properties for
          zhmcclient.Partition.update_properties()
        * stop (bool): Indicates whether some update properties require the
          partition to be stopped when doing the update.

    Raises:
      ParameterError: An issue with the module parameters.
    """
    create_props = {}
    update_props = {}
    stop = False

    # handle 'name' property
    part_name = params['name']
    create_props['name'] = part_name
    # We looked up the partition by name, so we will never have to update
    # the partition name

    # handle the other properties
    input_props = params['properties']
    for prop_name in input_props:

        if prop_name not in ZHMC_PARTITION_PROPERTIES:
            raise ParameterError(
                "Property {!r} is not defined in the data model for "
                "partitions.".format(prop_name))

        allowed, create, update, update_while_active, eq_func = \
            ZHMC_PARTITION_PROPERTIES[prop_name]

        if not allowed:
            raise ParameterError(
                "Property {!r} is not allowed in the 'properties' module "
                "parameter.".format(prop_name))

        # Double check that read-only properties are all marked as not allowed:
        assert (create or update) is True

        if prop_name == 'boot_storage_hba_name':
            # Process this artificial property
            if not partition:
                raise ParameterError(
                    "Artificial property {!r} can only be specified when the "
                    "partition previously exists.".format(prop_name))
            hba_name = input_props[prop_name]
            try:
                hba = partition.hbas.find(name=hba_name)
            except zhmcclient.NotFound:
                raise ParameterError(
                    "Artificial property {!r} does not name an existing HBA: "
                    "{!r}".format(prop_name, hba_name))
            hmc_prop_name = 'boot-storage-device'
            if partition.properties[hmc_prop_name] != hba.uri:
                update_props[hmc_prop_name] = hba.uri
                if not update_while_active:
                    stop = True
        elif prop_name == 'boot_network_nic_name':
            # Process this artificial property
            if not partition:
                raise ParameterError(
                    "Artificial property {!r} can only be specified when the "
                    "partition previously exists.".format(prop_name))
            nic_name = input_props[prop_name]
            try:
                nic = partition.nics.find(name=nic_name)
            except zhmcclient.NotFound:
                raise ParameterError(
                    "Artificial property {!r} does not name an existing NIC: "
                    "{!r}".format(prop_name, nic_name))
            hmc_prop_name = 'boot-network-device'
            if partition.properties[hmc_prop_name] != nic.uri:
                update_props[hmc_prop_name] = nic.uri
                if not update_while_active:
                    stop = True
        else:
            # Process a normal (= non-artificial) property
            hmc_prop_name = prop_name.replace('_', '-')
            input_prop_value = input_props[prop_name]
            if partition:
                if eq_func:
                    equal = eq_func(partition.properties[hmc_prop_name],
                                    input_prop_value,
                                    prop_name)
                else:
                    equal = (partition.properties[hmc_prop_name] ==
                             input_prop_value)
                if not equal and update:
                    update_props[hmc_prop_name] = input_prop_value
                    if not update_while_active:
                        stop = True
            else:
                if update:
                    update_props[hmc_prop_name] = input_prop_value
                    if not update_while_active:
                        stop = True
                if create:
                    create_props[hmc_prop_name] = input_prop_value

    return create_props, update_props, stop


def ensure_active(params, check_mode):
    """
    Ensure that the partition exists, is active or degraded, and has the
    specified properties.

    Raises:
      ParameterError: An issue with the module parameters.
      StatusError: An issue with the partition status.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    host = params['hmc_host']
    userid = params['hmc_userid']
    password = params['hmc_password']
    cpc_name = params['cpc_name']
    partition_name = params['name']

    changed = False
    result = {}

    try:
        session = zhmcclient.Session(host, userid, password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        try:
            partition = cpc.partitions.find(name=partition_name)
            partition.pull_full_properties()
        except zhmcclient.NotFound:
            partition = None

        if not partition:
            # It does not exist. Create it and update it if there are
            # update-only properties.

            if not check_mode:
                create_props, update_props, stop = process_properties(
                    partition, params)
                partition = cpc.partitions.create(create_props)
                update2_props = {}
                for name in update_props:
                    if name not in create_props:
                        update2_props[name] = update_props[name]
                if update2_props:
                    partition.update_properties(update2_props)
            changed = True
        else:
            # It exists, just update its properties. Stop only if needed.

            create_props, update_props, stop = process_properties(
                partition, params)
            if stop:
                changed |= stop_partition(partition, check_mode)
            if update_props:
                if not check_mode:
                    partition.update_properties(update_props)
                changed = True

        if partition:
            changed |= start_partition(partition, check_mode)

        if partition and not check_mode:
            partition.pull_full_properties()
            status = partition.get_property('status')
            if status not in ('active', 'degraded'):
                raise StatusError(
                    "Could not get partition {!r} into an active state, "
                    "status is: {r}".format(partition.name, status))

        if partition:
            result = partition.properties

        return changed, result

    finally:
        session.logoff()


def ensure_stopped(params, check_mode):
    """
    Ensure that the partition exists, is stopped, and has the specified
    properties.

    Raises:
      ParameterError: An issue with the module parameters.
      StatusError: An issue with the partition status.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    host = params['hmc_host']
    userid = params['hmc_userid']
    password = params['hmc_password']
    cpc_name = params['cpc_name']
    partition_name = params['name']

    changed = False
    result = {}

    try:
        session = zhmcclient.Session(host, userid, password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        try:
            partition = cpc.partitions.find(name=partition_name)
            partition.pull_full_properties()
        except zhmcclient.NotFound:
            partition = None

        if not partition:
            # It does not exist. Create it and update it if there are
            # update-only properties.

            if not check_mode:
                create_props, update_props, stop = process_properties(
                    partition, params)
                partition = cpc.partitions.create(create_props)
                update2_props = {}
                for name in update_props:
                    if name not in create_props:
                        update2_props[name] = update_props[name]
                if update2_props:
                    partition.update_properties(update2_props)
            changed = True
        else:
            # It exists, stop it and update its properties.

            changed |= stop_partition(partition, check_mode)

            create_props, update_props, stop = process_properties(
                partition, params)
            if update_props:
                if not check_mode:
                    partition.update_properties(update_props)
                changed = True

        if partition and not check_mode:
            partition.pull_full_properties()
            status = partition.get_property('status')
            if status not in ('stopped'):
                raise StatusError(
                    "Could not get partition {!r} into a stopped state, "
                    "status is: {!r}".format(partition.name, status))

        if partition:
            result = partition.properties

        return changed, result

    finally:
        session.logoff()


def ensure_absent(params, check_mode):
    """
    Ensure that the partition does not exist.

    Raises:
      ParameterError: An issue with the module parameters.
      StatusError: An issue with the partition status.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    host = params['hmc_host']
    userid = params['hmc_userid']
    password = params['hmc_password']
    cpc_name = params['cpc_name']
    partition_name = params['name']

    changed = False
    result = {}

    try:
        session = zhmcclient.Session(host, userid, password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        try:
            partition = cpc.partitions.find(name=partition_name)
        except zhmcclient.NotFound:
            return changed, result

        if not check_mode:
            stop_partition(partition, check_mode)
            partition.delete()
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
        "active": ensure_active,
        "stopped": ensure_stopped,
    }
    return actions[params['state']](params, check_mode)


def main():

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='str'),
        hmc_userid=dict(required=True, type='str'),
        hmc_password=dict(required=True, type='str', no_log=True),
        cpc_name=dict(required=True, type='str'),
        name=dict(required=True, type='str'),
        state=dict(required=True, type='str',
                   choices=['absent', 'stopped', 'active']),
        properties=dict(required=False, type='dict', default={}),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True)

    try:

        changed, result = perform_task(module.params, module.check_mode)

    except (Error, zhmcclient.Error) as exc:
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
