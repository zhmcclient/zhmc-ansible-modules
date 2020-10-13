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
from collections import OrderedDict
from ansible.module_utils.basic import AnsibleModule
from operator import itemgetter
import requests.packages.urllib3
import zhmcclient

from zhmc_ansible_modules.utils import log_init, Error, ParameterError, \
    StatusError, stop_partition, start_partition, \
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
module: zhmc_partition
version_added: "0.0"
short_description: Manages partitions
description:
  - Gathers facts about a partition, including its child resources (HBAs, NICs
    and virtual functions).
  - Creates, updates, deletes, starts, and stops partitions in a CPC. The
    child resources of the partition are are managed by separate Ansible
    modules.
  - The targeted CPC must be in the Dynamic Partition Manager (DPM) operational
    mode.
notes:
  - See also Ansible modules zhmc_hba, zhmc_nic, zhmc_virtual_function.
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
      - "C(facts): Does not change anything on the partition and returns
         the partition properties and the properties of its child resources
         (HBAs, NICs, and virtual functions)."
    required: true
    choices: ['absent', 'stopped', 'active', 'facts']
  properties:
    description:
      - "Dictionary with input properties for the partition, for
         C(state=stopped) and C(state=active). Key is the property name with
         underscores instead of hyphens, and value is the property value in
         YAML syntax. Integer properties may also be provided as decimal
         strings. Will be ignored for C(state=absent)."
      - "The possible input properties in this dictionary are the properties
         defined as writeable in the data model for Partition resources
         (where the property names contain underscores instead of hyphens),
         with the following exceptions:"
      - "* C(name): Cannot be specified because the name has already been
         specified in the C(name) module parameter."
      - "* C(type): Cannot be changed once the partition exists, because
         updating it is not supported."
      - "* C(boot_storage_device): Cannot be specified because this information
         is specified using the artificial property C(boot_storage_hba_name)."
      - "* C(boot_network_device): Cannot be specified because this information
         is specified using the artificial property C(boot_network_nic_name)."
      - "* C(boot_storage_hba_name): The name of the HBA whose URI is used to
         construct C(boot_storage_device). Specifying it requires that the
         partition exists."
      - "* C(boot_network_nic_name): The name of the NIC whose URI is used to
         construct C(boot_network_device). Specifying it requires that the
         partition exists."
      - "* C(crypto_configuration): The crypto configuration for the partition,
         in the format of the C(crypto-configuration) property of the
         partition (see HMC API book for details), with the exception that
         adapters are specified with their names in field
         C(crypto_adapter_names) instead of their URIs in field
         C(crypto_adapter_uris). If the C(crypto_adapter_names) field is null,
         all crypto adapters of the CPC will be used."
      - "Properties omitted in this dictionary will remain unchanged when the
         partition already exists, and will get the default value defined in
         the data model for partitions in the HMC API book when the partition
         is being created."
    required: false
    default: No input properties
  expand_storage_groups:
    description:
      - "Boolean that controls whether the returned partition contains
         an additional artificial property 'storage-groups' that is the list
         of storage groups attached to the partition, with properties as
         described for the zhmc_storage_group module with expand=true."
    required: false
    type: bool
    default: false
  expand_crypto_adapters:
    description:
      - "Boolean that controls whether the returned partition contains
         an additional artificial property 'crypto-adapters' in its
         'crypto-configuration' property that is the list
         of crypto adapters attached to the partition, with properties as
         described for the zhmc_adapter module."
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

# Because configuring LUN masking in the SAN requires the host WWPN, and the
# host WWPN is automatically assigned and will be known only after an HBA has
# been added to the partition, the partition needs to be created in stopped
# state. Also, because the HBA has not yet been created, the boot
# configuration cannot be done yet:
- name: Ensure the partition exists and is stopped
  zhmc_partition:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
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
    hmc_auth: "{{ my_hmc_auth }}"
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
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    name: "{{ my_partition_name }}"
    state: absent

- name: Define crypto configuration
  zhmc_partition:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    name: "{{ my_partition_name }}"
    state: active
    properties:
      crypto_configuration:
        crypto_adapter_names:
          - adapter1
          - adapter2
        crypto_domain_configurations:
          - domain_index: 0
            access_mode: control-usage
          - domain_index: 1
            access_mode: control
  register: part1

- name: Gather facts about a partition
  zhmc_partition:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    name: "{{ my_partition_name }}"
    state: facts
    expand_storage_groups: true
    expand_crypto_adapters: true
  register: part1

"""

RETURN = """
partition:
  description:
    - "For C(state=absent), an empty dictionary."
    - "For C(state=stopped) and C(state=active), a dictionary with the resource
       properties of the partition (after changes, if any). The dictionary
       keys are the exact property names as described in the data model for the
       resource, i.e. they contain hyphens (-), not underscores (_). The
       dictionary values are the property values using the Python
       representations described in the documentation of the zhmcclient Python
       package."
    - "For C(state=facts), a dictionary with the resource properties of the
       partition, including its child resources (HBAs, NICs, and virtual
       functions). The dictionary keys are the exact property names as
       described in the data model for the resource, i.e. they contain hyphens
       (-), not underscores (_). The dictionary values are the property values
       using the Python representations described in the documentation of the
       zhmcclient Python package. The properties of the child resources are
       represented in partition properties named 'hbas', 'nics', and
       'virtual-functions', respectively. The NIC properties are amended by
       artificial properties 'adapter-name', 'adapter-port', 'adapter-id'."
  returned: success
  type: dict
  sample: |
    C({
      "name": "part-1",
      "description": "partition #1",
      "status": "active",
      "boot-device": "storage-adapter",
      ...
    })
"""

# Python logger name for this module
LOGGER_NAME = 'zhmc_partition'

LOGGER = logging.getLogger(LOGGER_NAME)

# Dictionary of properties of partition resources, in this format:
#   name: (allowed, create, update, update_while_active, eq_func, type_cast)
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
#   type_cast: Type cast function for an input value of the property; None
#     means to use it directly. This can be used for example to convert
#     integers provided as strings by Ansible back into integers (that is a
#     current deficiency of Ansible).
ZHMC_PARTITION_PROPERTIES = {

    # create-only properties:
    'type': (True, True, False, None, None, None),  # cannot change type

    # update-only properties:
    'boot_network_device': (
        False, False, True, True, None, None),  # via boot_network_nic_name
    'boot_network_nic_name': (
        True, False, True, True, None, to_unicode),  # artificial property
    'boot_storage_device': (
        False, False, True, True, None, None),  # via boot_storage_hba_name
    'boot_storage_hba_name': (
        True, False, True, True, None, to_unicode),  # artificial property
    'crypto_configuration': (
        True, False, False, None, None,
        None),  # Contains artificial properties, type_cast ignored
    'acceptable_status': (True, False, True, True, None, None),
    'processor_management_enabled': (True, False, True, True, None, None),
    'ifl_absolute_processor_capping': (True, False, True, True, None, None),
    'ifl_absolute_processor_capping_value': (
        True, False, True, True, None, float),
    'ifl_processing_weight_capped': (True, False, True, True, None, None),
    'minimum_ifl_processing_weight': (True, False, True, True, None, int),
    'maximum_ifl_processing_weight': (True, False, True, True, None, int),
    'initial_ifl_processing_weight': (True, False, True, True, None, int),
    'cp_absolute_processor_capping': (True, False, True, True, None, None),
    'cp_absolute_processor_capping_value': (
        True, False, True, True, None, float),
    'cp_processing_weight_capped': (True, False, True, True, None, None),
    'minimum_cp_processing_weight': (True, False, True, True, None, int),
    'maximum_cp_processing_weight': (True, False, True, True, None, int),
    'initial_cp_processing_weight': (True, False, True, True, None, int),
    'boot_logical_unit_number': (True, False, True, True, eq_hex, None),
    'boot_world_wide_port_name': (True, False, True, True, eq_hex, None),
    'boot_os_specific_parameters': (True, False, True, True, None, to_unicode),
    'boot_iso_ins_file': (True, False, True, True, None, to_unicode),
    'ssc_boot_selection': (True, False, True, True, None, None),

    # create+update properties:
    'name': (
        False, True, True, True, None, None),  # provided in 'name' module parm
    'description': (True, True, True, True, None, to_unicode),
    'short_name': (True, True, True, False, None, None),
    'partition_id': (True, True, True, False, None, None),
    'autogenerate_partition_id': (True, True, True, False, None, None),
    'ifl_processors': (True, True, True, True, None, int),
    'cp_processors': (True, True, True, True, None, int),
    'processor_mode': (True, True, True, False, None, None),
    'initial_memory': (True, True, True, True, None, int),
    'maximum_memory': (True, True, True, False, None, int),
    'reserve_resources': (True, True, True, True, None, None),
    'boot_device': (True, True, True, True, None, None),
    'boot_timeout': (True, True, True, True, None, int),
    'boot_ftp_host': (True, True, True, True, None, to_unicode),
    'boot_ftp_username': (True, True, True, True, None, to_unicode),
    'boot_ftp_password': (True, True, True, True, None, to_unicode),
    'boot_ftp_insfile': (True, True, True, True, None, to_unicode),
    'boot_removable_media': (True, True, True, True, None, to_unicode),
    'boot_removable_media_type': (True, True, True, True, None, None),
    'boot_configuration_selector': (True, True, True, True, None, int),
    'boot_record_lba': (True, True, True, True, None, None),
    'access_global_performance_data': (True, True, True, True, None, None),
    'permit_cross_partition_commands': (True, True, True, True, None, None),
    'access_basic_counter_set': (True, True, True, True, None, None),
    'access_problem_state_counter_set': (True, True, True, True, None, None),
    'access_crypto_activity_counter_set': (True, True, True, True, None, None),
    'access_extended_counter_set': (True, True, True, True, None, None),
    'access_coprocessor_group_set': (True, True, True, True, None, None),
    'access_basic_sampling': (True, True, True, True, None, None),
    'access_diagnostic_sampling': (True, True, True, True, None, None),
    'permit_des_key_import_functions': (True, True, True, True, None, None),
    'permit_aes_key_import_functions': (True, True, True, True, None, None),
    'ssc_host_name': (True, True, True, True, None, to_unicode),
    'ssc_ipv4_gateway': (True, True, True, True, None, to_unicode),
    'ssc_dns_servers': (True, True, True, True, None, to_unicode),
    'ssc_master_userid': (True, True, True, True, None, to_unicode),
    'ssc_master_pw': (True, True, True, True, None, to_unicode),

    # read-only properties:
    'object_uri': (False, False, False, None, None, None),
    'object_id': (False, False, False, None, None, None),
    'parent': (False, False, False, None, None, None),
    'class': (False, False, False, None, None, None),
    'status': (False, False, False, None, None, None),
    'has_unacceptable_status': (False, False, False, None, None, None),
    'is_locked': (False, False, False, None, None, None),
    'os_name': (False, False, False, None, None, None),
    'os_type': (False, False, False, None, None, None),
    'os_version': (False, False, False, None, None, None),
    'degraded_adapters': (False, False, False, None, None, None),
    'current_ifl_processing_weight': (False, False, False, None, None, None),
    'current_cp_processing_weight': (False, False, False, None, None, None),
    'reserved_memory': (False, False, False, None, None, None),
    'auto_start': (False, False, False, None, None, None),
    'boot_iso_image_name': (False, False, False, None, None, None),
    'threads_per_processor': (False, False, False, None, None, None),
    'virtual_function_uris': (False, False, False, None, None, None),
    'nic_uris': (False, False, False, None, None, None),
    'hba_uris': (False, False, False, None, None, None),
}


def process_properties(cpc, partition, params):
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

      cpc (zhmcclient.Cpc): CPC with the partition to be updated, and
        with the adapters to be used for the partition.

      partition (zhmcclient.Partition): Partition to be updated with the full
        set of current properties, or `None` if it did not previously exist.

      params (dict): Module input parameters.

    Returns:
      tuple of (create_props, update_props, stop, crypto_changes), where:
        * create_props: dict of properties for
          zhmcclient.PartitionManager.create()
        * update_props: dict of properties for
          zhmcclient.Partition.update_properties()
        * stop (bool): Indicates whether some update properties require the
          partition to be stopped when doing the update.
        * crypto_changes (tuple): Changes to the crypto configuration if any
          (or `None` if no changes were specified), as a tuple of:
          * remove_adapters: List of Adapter objects to be removed
          * remove_domain_indexes: List of domain indexes to be removed
          * add_adapters: List of Adapter objects to be added
          * add_domain_configs: List of domain configs to be added (dict of
            'domain-index', 'access-mode')
          * change_domain_configs: List of domain configs for changing the
            access mode of existing domain indexes.

    Raises:
      ParameterError: An issue with the module parameters.
    """
    create_props = {}
    update_props = {}
    stop = False
    crypto_changes = None

    # handle 'name' property
    part_name = to_unicode(params['name'])
    create_props['name'] = part_name
    # We looked up the partition by name, so we will never have to update
    # the partition name

    # handle the other properties
    input_props = params.get('properties', {})
    if input_props is None:
        input_props = {}
    for prop_name in input_props:

        if prop_name not in ZHMC_PARTITION_PROPERTIES:
            raise ParameterError(
                "Property {!r} is not defined in the data model for "
                "partitions.".format(prop_name))

        allowed, create, update, update_while_active, eq_func, type_cast = \
            ZHMC_PARTITION_PROPERTIES[prop_name]

        if not allowed:
            raise ParameterError(
                "Property {!r} is not allowed in the 'properties' module "
                "parameter.".format(prop_name))

        if prop_name == 'boot_storage_hba_name':
            # Process this artificial property

            if not partition:
                raise ParameterError(
                    "Artificial property {!r} can only be specified when the "
                    "partition previously exists.".format(prop_name))

            if partition.hbas is None:
                raise ParameterError(
                    "Artificial property {!r} can only be specified when the "
                    "'dpm-storage-management' feature is disabled.".
                    format(prop_name))

            hba_name = input_props[prop_name]
            if type_cast:
                hba_name = type_cast(hba_name)

            try:
                hba = partition.hbas.find(name=hba_name)
            except zhmcclient.NotFound:
                raise ParameterError(
                    "Artificial property {!r} does not name an existing HBA: "
                    "{!r}".format(prop_name, hba_name))

            hmc_prop_name = 'boot-storage-device'
            if partition.properties.get(hmc_prop_name) != hba.uri:
                update_props[hmc_prop_name] = hba.uri
                assert update_while_active

        elif prop_name == 'boot_network_nic_name':
            # Process this artificial property

            if not partition:
                raise ParameterError(
                    "Artificial property {!r} can only be specified when the "
                    "partition previously exists.".format(prop_name))

            nic_name = input_props[prop_name]
            if type_cast:
                nic_name = type_cast(nic_name)

            try:
                nic = partition.nics.find(name=nic_name)
            except zhmcclient.NotFound:
                raise ParameterError(
                    "Artificial property {!r} does not name an existing NIC: "
                    "{!r}".format(prop_name, nic_name))

            hmc_prop_name = 'boot-network-device'
            if partition.properties.get(hmc_prop_name) != nic.uri:
                update_props[hmc_prop_name] = nic.uri
                assert update_while_active

        elif prop_name == 'crypto_configuration':
            # Process this artificial property

            crypto_config = input_props[prop_name]

            if not isinstance(crypto_config, dict):
                raise ParameterError(
                    "Artificial property {!r} is not a dictionary: {!r}.".
                    format(prop_name, crypto_config))

            if partition:
                hmc_prop_name = 'crypto-configuration'
                current_crypto_config = partition.properties.get(hmc_prop_name)
            else:
                current_crypto_config = None

            # Determine adapter changes
            try:
                adapter_field_name = 'crypto_adapter_names'
                adapter_names = crypto_config[adapter_field_name]
            except KeyError:
                raise ParameterError(
                    "Artificial property {!r} does not have required field "
                    "{!r}.".format(prop_name, adapter_field_name))
            adapter_uris = set()
            adapter_dict = {}  # adapters by uri
            if adapter_names is None:
                # Default: Use all crypto adapters of the CPC
                adapters = cpc.adapters.findall(type='crypto')
                for adapter in adapters:
                    adapter_dict[adapter.uri] = adapter
                    adapter_uris.add(adapter.uri)
            else:
                for adapter_name in adapter_names:
                    try:
                        adapter = cpc.adapters.find(name=adapter_name,
                                                    type='crypto')
                    except zhmcclient.NotFound:
                        raise ParameterError(
                            "Artificial property {!r} does not specify the "
                            "name of an existing crypto adapter in its {!r} "
                            "field: {!r}".
                            format(prop_name, adapter_field_name,
                                   adapter_name))
                    adapter_dict[adapter.uri] = adapter
                    adapter_uris.add(adapter.uri)
            if current_crypto_config:
                current_adapter_uris = set(
                    current_crypto_config['crypto-adapter-uris'])
            else:
                current_adapter_uris = set()
            if adapter_uris != current_adapter_uris:
                add_adapter_uris = adapter_uris - current_adapter_uris
                # Result: List of adapters to be added:
                add_adapters = [adapter_dict[uri] for uri in add_adapter_uris]
                remove_adapter_uris = current_adapter_uris - adapter_uris
                for uri in remove_adapter_uris:
                    adapter = cpc.adapters.find(**{'object-uri': uri})
                    # We assume the current crypto config lists only valid URIs
                    adapter_dict[adapter.uri] = adapter
                # Result: List of adapters to be removed:
                remove_adapters = \
                    [adapter_dict[uri] for uri in remove_adapter_uris]
            else:
                # Result: List of adapters to be added:
                add_adapters = []
                # Result: List of adapters to be removed:
                remove_adapters = []

            # Determine domain config changes.
            try:
                config_field_name = 'crypto_domain_configurations'
                domain_configs = crypto_config[config_field_name]
            except KeyError:
                raise ParameterError(
                    "Artificial property {!r} does not have required field "
                    "{!r}.".format(prop_name, config_field_name))
            di_field_name = 'domain_index'
            am_field_name = 'access_mode'
            domain_indexes = set()
            for dc in domain_configs:
                try:
                    # Convert to integer in case the domain index is provided
                    # as a string:
                    domain_index = int(dc[di_field_name])
                except KeyError:
                    raise ParameterError(
                        "Artificial property {!r} does not have required "
                        "sub-field {!r} in one of its {!r} fields.".
                        format(prop_name, di_field_name, config_field_name))
                domain_indexes.add(domain_index)
            current_access_mode_dict = {}  # dict: acc.mode by dom.index
            if current_crypto_config:
                current_domain_configs = \
                    current_crypto_config['crypto-domain-configurations']
                di_prop_name = 'domain-index'
                am_prop_name = 'access-mode'
                for dc in current_domain_configs:
                    # Here the domain index is always an integer because it is
                    # returned from the HMC that way, so no type cast needed.
                    current_access_mode_dict[dc[di_prop_name]] = \
                        dc[am_prop_name]
            current_domain_indexes = \
                set([di for di in current_access_mode_dict])
            # Result: List of domain indexes to be removed:
            remove_domain_indexes = \
                list(current_domain_indexes - domain_indexes)
            # Building result: List of domain configs to be added:
            add_domain_configs = []
            # Building result: List of domain configs to be changed:
            change_domain_configs = []
            for dc in domain_configs:
                # Convert to integer in case the domain index is provided
                # as a string:
                domain_index = int(dc[di_field_name])
                try:
                    access_mode = dc[am_field_name]
                except KeyError:
                    raise ParameterError(
                        "Artificial property {!r} does not have required "
                        "sub-field {!r} in one of its {!r} fields.".
                        format(prop_name, am_field_name, config_field_name))
                hmc_domain_config = {
                    'domain-index': domain_index,
                    'access-mode': access_mode,
                }
                if domain_index not in current_access_mode_dict:
                    # Domain is not included yet
                    add_domain_configs.append(hmc_domain_config)
                elif access_mode != current_access_mode_dict[domain_index]:
                    # Domain is included but access mode needs to be changed
                    change_domain_configs.append(hmc_domain_config)

            crypto_changes = (remove_adapters, remove_domain_indexes,
                              add_adapters, add_domain_configs,
                              change_domain_configs)

        else:
            # Process a normal (= non-artificial) property
            if prop_name == 'ssc_ipv4_gateway':
                # Undo conversion from None to empty string in Ansible
                if input_props[prop_name] == '':
                    input_props[prop_name] = None
            _create_props, _update_props, _stop = process_normal_property(
                prop_name, ZHMC_PARTITION_PROPERTIES, input_props, partition)
            create_props.update(_create_props)
            update_props.update(_update_props)
            if _stop:
                stop = True

    return create_props, update_props, stop, crypto_changes


def change_crypto_config(partition, crypto_changes, check_mode):
    """
    Change the crypto configuration of the partition as specified.

    Returns whether the crypto configuration has or would have changed.
    """

    remove_adapters, remove_domain_indexes, \
        add_adapters, add_domain_configs, \
        change_domain_configs = crypto_changes

    changed = False

    # We process additions first, in order to avoid
    # HTTPError 409,111 (At least one 'usage' required).
    if add_adapters or add_domain_configs:
        if not check_mode:
            partition.increase_crypto_config(add_adapters,
                                             add_domain_configs)
        changed = True

    if change_domain_configs:
        # We process changes that set access mode 'control-usage' first,
        # in order to avoid HTTPError 409,111 (At least one 'usage' required).
        for domain_config in sorted(change_domain_configs,
                                    key=itemgetter('access-mode'),
                                    reverse=True):
            domain_index = domain_config['domain-index']
            access_mode = domain_config['access-mode']
            if not check_mode:
                partition.change_crypto_domain_config(domain_index,
                                                      access_mode)
        changed = True

    if remove_adapters or remove_domain_indexes:
        if not check_mode:
            partition.decrease_crypto_config(remove_adapters,
                                             remove_domain_indexes)
        changed = True

    return changed


def add_artificial_properties(
        partition, expand_storage_groups, expand_crypto_adapters):
    """
    Add artificial properties to the partition object.

    Upon return, the properties of the partition object have been
    extended by these artificial properties:

    * 'hbas': List of Hba objects of the partition.

    * 'nics': List of Nic objects of the partition, with their properties
      and these artificial properties:

        * 'adapter-name'
        * 'adapter-port'
        * 'adapter-id'

    * 'virtual-functions': List of VirtualFunction objects of the partition.

    and if expand_storage_groups is True:

    * 'storage-groups': List of StorageGroup objects representing the
      storage groups attached to the partition, with their properties
      and these artificial properties:

        * 'candidate-adapter-ports': List of Port objects representing the
          candidate adapter ports of the storage group, with their properties
          and these artificial properties:

            - 'parent-adapter': Adapter object of the port.

        * 'storage-volumes': List of StorageVolume objects of the storage
          group.

        * 'virtual-storage-resources': List of VirtualStorageResource objects
          of the storage group.

    and if expand_crypto_adapters is True:

    * 'crypto-adapters' in 'crypto-configuration': List of Adapter objects
      representing the crypto adapters assigned to the partition.
    """
    cpc = partition.manager.cpc
    console = cpc.manager.console
    session = cpc.manager.client.session

    # Get the HBA child elements of the partition
    hbas_prop = list()
    if partition.hbas is not None:
        for hba in partition.hbas.list(full_properties=True):
            hbas_prop.append(hba.properties)
    partition.properties['hbas'] = hbas_prop

    # Get the NIC child elements of the partition
    nics_prop = list()
    for nic in partition.nics.list(full_properties=True):
        nic_props = OrderedDict()
        nic_props.update(nic.properties)
        # Add artificial properties adapter-name/-port/-id:
        vswitch_uri = nic.prop("virtual-switch-uri", None)
        if vswitch_uri:
            # OSA, Hipersockets
            vswitch = cpc.virtual_switches.find(**{'object-uri': vswitch_uri})
            adapter_uri = vswitch.get_property('backing-adapter-uri')
            adapter_port = vswitch.get_property('port')
            adapter = cpc.adapters.find(**{'object-uri': adapter_uri})
            nic_props['adapter-name'] = adapter.name
            nic_props['adapter-port'] = adapter_port
            nic_props['adapter-id'] = adapter.get_property('adapter-id')
        else:
            # RoCE, CNA
            port_uri = nic.prop("network-adapter-port-uri", None)
            assert port_uri
            port_props = session.get(port_uri)
            adapter_uri = port_props['parent']
            adapter = cpc.adapters.find(**{'object-uri': adapter_uri})
            nic_props['adapter-name'] = adapter.name
            nic_props['adapter-port'] = port_props['index']
            nic_props['adapter-id'] = adapter.get_property('adapter-id')
        nics_prop.append(nic_props)
    partition.properties['nics'] = nics_prop

    # Get the VF child elements of the partition
    vf_prop = list()
    for vf in partition.virtual_functions.list(full_properties=True):
        vf_prop.append(vf.properties)
    partition.properties['virtual-functions'] = vf_prop

    if expand_storage_groups:
        sg_prop = list()
        for sg_uri in partition.properties['storage-group-uris']:
            storage_group = console.storage_groups.resource_object(sg_uri)
            storage_group.pull_full_properties()
            sg_prop.append(storage_group.properties)

            # Candidate adapter ports and their adapters (full set of props)
            caps_prop = list()
            for cap in storage_group.list_candidate_adapter_ports(
                    full_properties=True):
                adapter = cap.manager.adapter
                adapter.pull_full_properties()
                cap.properties['parent-adapter'] = adapter.properties
                caps_prop.append(cap.properties)
            storage_group.properties['candidate-adapter-ports'] = caps_prop

            # Storage volumes (full set of properties).
            # Note: We create the storage volumes from the
            # 'storage-volume-uris' property, because the 'List Storage
            # Volumes of a Storage Group' operation returns an empty list for
            # auto-discovered volumes.
            svs_prop = list()
            sv_uris = storage_group.get_property('storage-volume-uris')
            for sv_uri in sv_uris:
                sv = storage_group.storage_volumes.resource_object(sv_uri)
                sv.pull_full_properties()
                svs_prop.append(sv.properties)
            storage_group.properties['storage-volumes'] = svs_prop

            # Virtual storage resources (full set of properties).
            vsrs_prop = list()
            vsr_uris = storage_group.get_property(
                'virtual-storage-resource-uris')
            for vsr_uri in vsr_uris:
                vsr = storage_group.virtual_storage_resources.resource_object(
                    vsr_uri)
                vsr.pull_full_properties()
                vsrs_prop.append(vsr.properties)
            storage_group.properties['virtual-storage-resources'] = vsrs_prop

        partition.properties['storage-groups'] = sg_prop

    if expand_crypto_adapters:

        cc = partition.properties['crypto-configuration']
        if cc:
            ca_prop = list()
            for ca_uri in cc['crypto-adapter-uris']:
                ca = cpc.adapters.resource_object(ca_uri)
                ca.pull_full_properties()
                ca_prop.append(ca.properties)
            cc['crypto-adapters'] = ca_prop


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
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['cpc_name']
    partition_name = params['name']
    expand_storage_groups = params['expand_storage_groups']
    expand_crypto_adapters = params['expand_crypto_adapters']
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
            partition.pull_full_properties()
        except zhmcclient.NotFound:
            partition = None

        if not partition:
            # It does not exist. Create it and update it if there are
            # update-only properties.
            if not check_mode:
                create_props, update_props, stop, crypto_changes = \
                    process_properties(cpc, partition, params)
                partition = cpc.partitions.create(create_props)
                update2_props = {}
                for name in update_props:
                    if name not in create_props:
                        update2_props[name] = update_props[name]
                if update2_props:
                    partition.update_properties(update2_props)
                # We refresh the properties after the update, in case an
                # input property value gets changed (for example, the
                # partition does that with memory properties).
                partition.pull_full_properties()
                if crypto_changes:
                    change_crypto_config(partition, crypto_changes, check_mode)
            else:
                # TODO: Show props in module result also in check mode.
                pass
            changed = True
        else:
            # It exists. Stop if needed due to property update requirements,
            # or wait for an updateable partition status, and update its
            # properties.
            create_props, update_props, stop, crypto_changes = \
                process_properties(cpc, partition, params)
            if update_props:
                if not check_mode:
                    if stop:
                        stop_partition(partition, check_mode)
                    else:
                        wait_for_transition_completion(partition)
                    partition.update_properties(update_props)
                    # We refresh the properties after the update, in case an
                    # input property value gets changed (for example, the
                    # partition does that with memory properties).
                    partition.pull_full_properties()
                else:
                    # TODO: Show updated props in mod.result also in chk.mode
                    pass
                changed = True
            if crypto_changes:
                changed |= change_crypto_config(partition, crypto_changes,
                                                check_mode)

        if partition:
            changed |= start_partition(partition, check_mode)

        if partition and not check_mode:
            partition.pull_full_properties()
            status = partition.get_property('status')
            if status not in ('active', 'degraded'):
                raise StatusError(
                    "Could not get partition {!r} into an active state, "
                    "status is: {!r}".format(partition.name, status))

        if partition:
            add_artificial_properties(
                partition, expand_storage_groups, expand_crypto_adapters)
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
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['cpc_name']
    partition_name = params['name']
    expand_storage_groups = params['expand_storage_groups']
    expand_crypto_adapters = params['expand_crypto_adapters']
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
            partition.pull_full_properties()
        except zhmcclient.NotFound:
            partition = None

        if not partition:
            # It does not exist. Create it and update it if there are
            # update-only properties.
            if not check_mode:
                create_props, update_props, stop, crypto_changes = \
                    process_properties(cpc, partition, params)
                partition = cpc.partitions.create(create_props)
                update2_props = {}
                for name in update_props:
                    if name not in create_props:
                        update2_props[name] = update_props[name]
                if update2_props:
                    partition.update_properties(update2_props)
                if crypto_changes:
                    change_crypto_config(partition, crypto_changes, check_mode)
            changed = True
        else:
            # It exists. Stop it and update its properties.
            create_props, update_props, stop, crypto_changes = \
                process_properties(cpc, partition, params)
            changed |= stop_partition(partition, check_mode)
            if update_props:
                if not check_mode:
                    partition.update_properties(update_props)
                changed = True
            if crypto_changes:
                changed |= change_crypto_config(partition, crypto_changes,
                                                check_mode)

        if partition and not check_mode:
            partition.pull_full_properties()
            status = partition.get_property('status')
            if status not in ('stopped'):
                raise StatusError(
                    "Could not get partition {!r} into a stopped state, "
                    "status is: {!r}".format(partition.name, status))

        if partition:
            add_artificial_properties(
                partition, expand_storage_groups, expand_crypto_adapters)
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
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['cpc_name']
    partition_name = params['name']
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
            return changed, result

        if not check_mode:
            stop_partition(partition, check_mode)
            partition.delete()
        changed = True

        return changed, result

    finally:
        session.logoff()


def facts(params, check_mode):
    """
    Return partition facts.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['cpc_name']
    partition_name = params['name']
    expand_storage_groups = params['expand_storage_groups']
    expand_crypto_adapters = params['expand_crypto_adapters']
    faked_session = params.get('faked_session', None)

    changed = False
    result = {}

    try:
        # The default exception handling is sufficient for this code

        session = get_session(faked_session, host, userid, password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)

        partition = cpc.partitions.find(name=partition_name)
        partition.pull_full_properties()

        add_artificial_properties(
            partition, expand_storage_groups, expand_crypto_adapters)
        result = partition.properties
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
                   choices=['absent', 'stopped', 'active', 'facts']),
        properties=dict(required=False, type='dict', default={}),
        expand_storage_groups=dict(required=False, type='bool', default=False),
        expand_crypto_adapters=dict(required=False, type='bool',
                                    default=False),
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
    module.exit_json(changed=changed, partition=result)


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings()
    main()
