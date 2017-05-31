#!/usr/bin/env python

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
module: zhmc_partition
short_description: Manages partitions on z Systems / LinuxONE machines
description:
  - Creates, updates, deletes, starts, and stops partitions on z Systems and
    LinuxONE machines that are in the Dynamic Partition Manager (DPM)
    operational mode.
  - Child resources on partitions such as HBAs, NICs or virtual functions are
    managed by separate Ansible modules.
  - If the targeted CPC is not in DPM mode, the module will fail.
notes:
  - See also Ansible modules zhmc_hba, zhmc_nic, zhmc_virtualfunction.
author:
  - Andreas Maier (@andy-maier)
  - Andreas Scheuring (@scheuran)
  - Juergen Leopold (@leopoldjuergen)
requirements:
  - z Systems or LinuxONE CPC in DPM mode
  - Python package zhmcclient >=0.14.0
options:
  - option-name: hmc_host
    description:
      - The hostname or IP address of the HMC managing the target z Systems or
        LinuxONE machine (CPC).
    required: true
    type: string
  - option-name: hmc_userid
    description:
      - The userid for authenticating with the HMC.
    required: true
    type: string
  - option-name: hmc_password
    description:
      - The password of the userid for authenticating with the HMC.
    required: true
    type: string
  - option-name: cpc_name
    description:
      - The name of the CPC containing the target partition (i.e. the value of
        the C(name) property of the CPC resource). This value is used to look
        up the CPC within the specified HMC.
    required: true
    type: string
  - option-name: name
    description:
      - The name of the target partition (i.e. the value of the C(name)
        property of the partition resource).  This value is used to look up the
        partition within the specified CPC. If a partition needs to be created,
        this value becomes its name.
    required: true
    type: string
  - option-name: state
    description:
      - The desired existence and operational status for the partition, using
        the following values:
        * C(absent): The partition shall not exist in the specified CPC.
          Details: If the partition exists, it will be stopped (if active or
          degraded) and deleted.
          This will also delete all child resources of the partition (HBAs,
          NICs, virtual functions).
        * C(stopped): The partition shall exist and shall be in the "stopped"
          operational status (i.e. its C(status) property has the according
          value.
          Details: If the partition does not exist in the specified CPC, it is
          created, and updated if needed (some properties can only be updated).
          If the partition exists, the input properties will be used to update
          the partition.
          If the partition is not in the stopped status, it will be stopped.
        * C(active): The partition shall exist and shall be in the "active"
          or "degraded" operational status (i.e. its C(status) property has the
          according value).
          Details: If the partition does not exist in the specified CPC, it is
          created, and updated if needed (some properties can only be updated).
          If the partition exists, the input properties will be used to update
          the partition.
          If the partition is not in the active or degraded status, it will be
          started.
    required: true
    type: string
    choices:
      - absent
      - stopped
      - active
  - option-name: properties
    description:
      - A dictionary of input properties for the partition, for C(state) values
        C(stopped) and C(active). The dictionary may be specified and will
        be ignored for C(state) value C(absent).
      - These input properties are used to ensure that the partition properties
        have the specified values. If needed, a "Create Partition" operation
        will be followed by an "Update Partition properties" operation (some
        properties cannot be set at creation time, but can be updated
        afterwards).
      - The possible input properties in this dictionary are:
        * The properties defined as writeable in the data model for partition
          resources in the HMC API book, with the following additional
          considerations:
          * Property names are specified with underscores instead of hyphens.
          * The C(name) property cannot be specified here because the name has
            already been specified in the C(name) module parameter.
          * The C(type) property cannot be changed, because updating it
            is not supported, and deleting and recreating the partition just
            for a change of the partition type seems prohibitive.
          * Some properties from the data model are replaced with more
            convenient artificial properties, see below.
        * The following artificial properties, replacing their corresponding
          data model properties:
          * C(boot_storage_hba_name): The name of the HBA whose URI will be
            used to construct the C(boot-storage-device) property. A
            C(boot_storage_device) property cannot be specified in the
            input dictionary.
          * C(boot_network_nic_name): The name of the NIC whose URI will be
            used to construct the C(boot-network-device) property. A
            C(boot_network_device) property cannot be specified in the
            input dictionary.
      - Properties omitted in this dictionary will remain unchanged when the
        partition already existed, and will get the default value defined in
        the data model for partitions in the HMC API book when the partition
        was created.
    required: false
    type: dict
    default:
      - No input properties
"""

EXAMPLES = """
---

# Because configuring LUN masking in the SAN requires the host WWPN, and the
# host WWPN is automatically assigned and will be known only after an HBA has
# been added to the partition, the partition needs to be created in stopped
# state. Also, because the HBA has not yet been created, the boot configuration
# cannot be done yet:
- name: Ensure the partition exists and is stopped
  zhmc_partition:
    hmc_host: "{{ hmc_host }}"
    hmc_userid: "{{ hmc_userid }}"
    hmc_password: "{{ hmc_password }}"
    cpc_name: "{{ cpc_name }}"
    name: zhmc-part-1
    state: stopped
    properties:
      description: "zhmc Ansible modules: Example partition 1"
      ifl_processors: 2
      initial_memory: 1024
      maximum_memory: 1024
  register: part1

# After an HBA has been added (see Ansible module zhmc_hba), and LUN masking
# has been configured in the SAN, and a bootable image is available at the
# configured LUN and target WWPN, the partition can be configured for boot from
# the FCP LUN and can be started:
- name: Configure boot device and start the partition
  zhmc_partition:
    hmc_host: "{{ hmc_host }}"
    hmc_userid: "{{ hmc_userid }}"
    hmc_password: "{{ hmc_password }}"
    cpc_name: "{{ cpc_name }}"
    name: zhmc-part-1
    state: active
      boot_device: storage-adapter
      boot_storage_device_hba_name: hba1
      boot_logical_unit_number: 00000000001
      boot_world_wide_port_name: abcdefabcdef
  register: part1
"""

RETURN = """
properties:
  description:
    - For state=stopped and state=active, a dictionary with all resource
      properties of the partition (after changes, if any), as defined in the
      data model for partition resources in the HMC API book.
    - For state=absent, an empty dictionary.
    - The dictionary keys are the exact property names as described in the
      data model for partition resources, i.e. they contain hyphens (-),
      not underscores (_).
    - The dictionary values are the property values using the Python
      representations described in the documentation of the zhmcclient Python
      package.
    - Note that the returned dictionary contains all resource properties of
      the partition, not just those that can be or have been provided when
      creating the partition.
    - Note that the names of properties in the returned dictionary are
      different from the names of properties in the 'properties' input
      parameter in two ways:
      * In the returned dictionary, the property names contain the hyphens
        exactly as defined in the data model, while in the 'properties' input
        parameter, the hyphens have been replaced with underscores.
      * The returned dictionary does not have the artificial properties
        that have been added to the properties in the 'properties' input
        parameter, but has the underlying properties from the data model
        instead.
  returned: success
  type: dict
  sample:
    - {
        'name': 'part-1',
        'description': 'partition #1',
        'status': 'active',
        'boot-device': 'storage-adapter',
        . . .
      }
"""


import traceback
from ansible.module_utils.basic import AnsibleModule
import requests.packages.urllib3
import zhmcclient

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
ZHMC_PARTITION_PROPERTIES = {

    # properties provided in specific module parameters (not in 'properties'):
    'name': (False, True, True, True),

    # HMC properties handled by artificial properties:
    'boot_network_device': (False, False, True, True),
    'boot_storage_device': (False, False, True, True),

    # the corresponding artificial properties:
    'boot_network_nic_name': (True, False, True, True),
    'boot_storage_hba_name': (True, False, True, True),

    # create-only properties:
    'type': (False, True, False, None),  # not allowed by restriction

    # update-only properties:
    'ifl_absolute_processor_capping': (True, False, True, True),
    'ifl_absolute_processor_capping_value': (True, False, True, True),
    'ifl_processing_weight_capped': (True, False, True, True),
    'minimum_ifl_processing_weight': (True, False, True, True),
    'maximum_ifl_processing_weight': (True, False, True, True),
    'initial_ifl_processing_weight': (True, False, True, True),
    'cp_absolute_processor_capping': (True, False, True, True),
    'cp_absolute_processor_capping_value': (True, False, True, True),
    'minimum_cp_processing_weight': (True, False, True, True),
    'maximum_cp_processing_weight': (True, False, True, True),
    'initial_cp_processing_weight': (True, False, True, True),
    'boot_logical_unit_number': (True, False, True, True),
    'boot_world_wide_port_name': (True, False, True, True),
    'boot_os_specific_parameters': (True, False, True, True),
    'boot_iso_ins_file': (True, False, True, True),
    'ssc_boot_selection': (True, False, True, True),

    # create+update properties:
    'description': (True, True, True, True),
    'short_name': (True, True, True, True),
    'partition_id': (True, True, True, True),
    'autogenerate_partition_id': (True, True, True, True),
    'ifl_processors': (True, True, True, True),
    'cp_processors': (True, True, True, True),
    'processor_mode': (True, True, True, True),
    'initial_memory': (True, True, True, True),
    'maximum_memory': (True, True, True, True),
    'reserve_resources': (True, True, True, True),
    'boot_device': (True, True, True, True),
    'boot_timeout': (True, True, True, True),
    'boot_ftp_host': (True, True, True, True),
    'boot_ftp_username': (True, True, True, True),
    'boot_ftp_password': (True, True, True, True),
    'boot_ftp_insfile': (True, True, True, True),
    'boot_removable_media': (True, True, True, True),
    'boot_removable_media_type': (True, True, True, True),
    'boot_configuration_selector': (True, True, True, True),
    'boot_record_lba': (True, True, True, True),
    'access_global_performance_data': (True, True, True, True),
    'permit_cross_partition_commands': (True, True, True, True),
    'access_basic_counter_set': (True, True, True, True),
    'access_problem_state_counter_set': (True, True, True, True),
    'access_crypto_activity_counter_set': (True, True, True, True),
    'access_extended_counter_set': (True, True, True, True),
    'access_coprocessor_group_set': (True, True, True, True),
    'access_basic_sampling': (True, True, True, True),
    'access_diagnostic_sampling': (True, True, True, True),
    'permit_des_key_import_functions': (True, True, True, True),
    'permit_aes_key_import_functions': (True, True, True, True),
    'ssc_host_name': (True, True, True, True),
    'ssc_ipv4_gateway': (True, True, True, True),
    'ssc_dns_servers': (True, True, True, True),
    'ssc_master_userid': (True, True, True, True),
    'ssc_master_pw': (True, True, True, True),

    # read-only properties:
    'object-uri': (False, False, False, None),
    'parent': (False, False, False, None),
    'class': (False, False, False, None),
    'status': (False, False, False, None),
    'os_name': (False, False, False, None),
    'os_type': (False, False, False, None),
    'os_version': (False, False, False, None),
    'degraded_adapters': (False, False, False, None),
    'current_ifl_processing_weight': (False, False, False, None),
    'current_cp_processing_weight': (False, False, False, None),
    'reserved_memory': (False, False, False, None),
    'auto_start': (False, False, False, None),
    'boot_iso_image_name': (False, False, False, None),
    'threads_per_processor': (False, False, False, None),
    'virtual_function_uris': (False, False, False, None),
    'nic_uris': (False, False, False, None),
    'hba_uris': (False, False, False, None),
    'crypto_configuration': (False, False, False, None),
}

# Partition status values that may happen after Partition.start()
STARTED_STATUSES = ('active', 'degraded', 'reservation-error')

# Partition status values that may happen after Partition.stop()
STOPPED_STATUSES = ('stopped', 'terminated', 'paused')

# Partition status values that indicate CPC issues
BAD_STATUSES = ('communications-not-active', 'status-check')


class ParameterError(Exception):
    """
    Indicates an error with the module input parameters.
    """
    pass


class StatusError(Exception):
    """
    Indicates an error with the status of the partition.
    """
    pass


def stop_partition(partition, check_mode):
    """
    Ensure that the partition is stopped, by influencing the operational
    status of the partition, regardless of what its current operational status
    is.

    The resulting operational status will be one of STOPPED_STATUSES.

    Parameters:
      partition (zhmcclient.Partition): The partition (must exist, and its
        status property is assumed to be current).
      check_mode (bool): Indicates whether the playbook was run in check mode,
        in which case this method does ot actually stop the partition, but
        just returns what would have been done.

    Returns:
      bool: Indicates whether the partition was changed.

    Raises:
      StatusError: Partition is in one of BAD_STATUSES.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """
    changed = False
    status = partition.get_property('status')
    if status in BAD_STATUSES:
        raise StatusError(
            "Target CPC {!r} has issues; status of partition {!r} is: {!r}".
            format(partition.manager.cpc.name, partition.name, status))
    elif status == 'starting':
        if not check_mode:
            # Let it first finish the starting
            partition.wait_for_status(STARTED_STATUSES)
            partition.stop()
        changed = True
    elif status == 'stopping':
        if not check_mode:
            partition.wait_for_status(STOPPED_STATUSES)
        changed = True
    elif status in STARTED_STATUSES:
        if not check_mode:
            partition.stop()
        changed = True
    else:
        assert status in STOPPED_STATUSES
    return changed


def start_partition(partition, check_mode):
    """
    Ensure that the partition is started, by influencing the operational
    status of the partition, regardless of what its current operational status
    is.

    The resulting operational status will be one of STARTED_STATUSES.

    Parameters:
      partition (zhmcclient.Partition): The partition (must exist, and its
        status property is assumed to be current).
      check_mode (bool): Indicates whether the playbook was run in check mode,
        in which case this method does not actually change the partition, but
        just returns what would have been done.

    Returns:
      bool: Indicates whether the partition was changed.

    Raises:
      StatusError: Partition is in one of BAD_STATUSES.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """
    changed = False
    status = partition.get_property('status')
    if status in BAD_STATUSES:
        raise StatusError(
            "Target CPC {!r} has issues; status of partition {!r} is: {!r}".
            format(partition.manager.cpc.name, partition.name, status))
    elif status == 'stopping':
        if not check_mode:
            # Let it first finish the stopping
            partition.wait_for_status(STOPPED_STATUSES)
            partition.start()
        changed = True
    elif status == 'starting':
        if not check_mode:
            partition.wait_for_status(STARTED_STATUSES)
        changed = True
    elif status in STOPPED_STATUSES:
        if not check_mode:
            partition.start()
        changed = True
    else:
        assert status in STARTED_STATUSES
    return changed


def process_properties(partition, params):
    """
    Process the properties specified in the 'partition' module parameter,
    and return a tuple of dictionaries (create, update) that contain
    the properties that can be created, and the properties that can be updated,
    respectively. If the partition exists, the input property values are
    compared with the existing partition property values and the returned set
    of properties is the minimal set of properties that need to be changed.

    - Underscores in the property names are translated into hyphens.
    - The presence of read-only properties, invalid properties (i.e. not
      defined in the data model for partitions), and properties that are not
      allowed because of restrictions or because they are auto-created from
      an artificial property is surfaced by raising ValueError.
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

        allowed, create, update, update_while_active = \
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
            if not partition or \
                    partition.properties[hmc_prop_name] != input_prop_value:
                if create:
                    create_props[hmc_prop_name] = input_prop_value
                if update:
                    update_props[hmc_prop_name] = input_prop_value
                if not update_while_active:
                    stop = True

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

    hmc = params['hmc_host']
    userid = params['hmc_userid']
    password = params['hmc_password']
    cpc_name = params['cpc_name']
    partition_name = params['name']

    changed = False
    result = {}

    try:
        session = zhmcclient.Session(hmc, userid, password)
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

    hmc = params['hmc_host']
    userid = params['hmc_userid']
    password = params['hmc_password']
    cpc_name = params['cpc_name']
    partition_name = params['name']

    changed = False
    result = {}

    try:
        session = zhmcclient.Session(hmc, userid, password)
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

    hmc = params['hmc_host']
    userid = params['hmc_userid']
    password = params['hmc_password']
    cpc_name = params['cpc_name']
    partition_name = params['name']

    changed = False
    result = {}

    try:
        session = zhmcclient.Session(hmc, userid, password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        try:
            partition = cpc.partitions.find(name=partition_name)
        except zhmcclient.NotFound:
            return changed, result

        if not check_mode:
            stop_partition(partition)
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
        'name': {
            'required': True,
            'type': 'str',
        },
        'state': {
            'required': True,
            'type': 'str',
            'choices': ['absent', 'stopped', 'active'],
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
