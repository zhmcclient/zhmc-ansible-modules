#!/usr/bin/python
# Copyright 2017,2020 IBM Corp. All Rights Reserved.
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
module: zhmc_nic
version_added: "2.9.0"
short_description: Manage a NIC of a partition (DPM mode)
description:
  - Gather facts about a NIC (virtual Network Interface Card) in a partition of
    a CPC (Z system).
  - Create, update, or delete a NIC in a partition.
  - Note that the Ansible module zhmc_partition can be used to gather facts
    about existing NICs of a partition.
author:
  - Andreas Maier (@andy-maier)
  - Andreas Scheuring (@scheuran)
  - Juergen Leopold (@leopoldjuergen)
requirements:
  - The targeted Z system must be in the Dynamic Partition Manager (DPM)
    operational mode.
  - "The HMC userid must have these task permissions:
    'Partition Details'."
  - "The HMC userid must have object-access permissions to these objects:
    Partitions of the target NICs, CPCs of these partitions, network adapters
    backing the target NICs."
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
  cpc_name:
    description:
      - The name of the CPC with the partition containing the NIC.
    type: str
    required: true
  partition_name:
    description:
      - The name of the partition containing the NIC.
    type: str
    required: true
  name:
    description:
      - The name of the target NIC that is managed. If the NIC needs to be
        created, this value becomes its name.
    type: str
    required: true
  state:
    description:
      - "The desired state for the NIC. All states are fully idempotent
         within the limits of the properties that can be changed:"
      - "* V(absent): Ensures that the NIC does not exist in the specified
         partition."
      - "* V(present): Ensures that the NIC exists in the specified partition
         and has the specified properties."
      - "* V(facts): Returns the NIC properties."
    type: str
    required: true
    choices: ["absent", "present", "facts"]
  properties:
    description:
      - "Dictionary with input properties for the NIC, for O(state=present).
         Key is the property name with underscores instead of hyphens, and
         value is the property value in YAML syntax. Integer properties may
         also be provided as decimal strings. Will be ignored for
         O(state=absent)."
      - "The possible input properties in this dictionary are the properties
         defined as writeable in the data model for NIC resources (where the
         property names contain underscores instead of hyphens), with the
         following exceptions:"
      - "* C(name): Cannot be specified because the name has already been
         specified in the O(name) module parameter."
      - "* C(network_adapter_port_uri) and C(virtual_switch_uri): Cannot be
         specified because this information is specified using the artificial
         properties C(adapter_name) and C(adapter_port)."
      - "* C(adapter_name): The name of the adapter that has the port backing
         the target NIC. Used for all adapter families (ROCE, OSA,
         Hipersockets)."
      - "* C(adapter_port): The port index of the adapter port backing the
         target NIC. Used for all adapter families (ROCE, OSA, Hipersockets)."
      - "Properties omitted in this dictionary will remain unchanged when the
         NIC already exists, and will get the default value defined in the
         data model for NICs when the NIC is being created."
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

- name: Ensure NIC exists in the partition
  zhmc_partition:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    partition_name: "{{ my_partition_name }}"
    name: "{{ my_nic_name }}"
    state: present
    properties:
      adapter_name: "OSD 0128 A13B-13"
      adapter_port: 0
      description: "The port to our data network"
      device_number: "023F"
  register: nic1

- name: Ensure NIC does not exist in the partition
  zhmc_partition:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    partition_name: "{{ my_partition_name }}"
    name: "{{ my_nic_name }}"
    state: absent

- name: Gather facts about a NIC
  zhmc_partition:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    partition_name: "{{ my_partition_name }}"
    name: "{{ my_nic_name }}"
    state: facts
  register: nic1
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
nic:
  description:
    - "For O(state=absent), an empty dictionary."
    - "For O(state=present|facts), the resource properties of the NIC after any
       changes."
  returned: success
  type: dict
  contains:
    name:
      description: "NIC name"
      type: str
    "{property}":
      description: "Additional properties of the NIC, as described in the data
        model of the 'NIC' element object of the 'Partition' object in the
        R(HMC API,HMC API) book.
        The property names have hyphens (-) as described in that book."
      type: raw
  sample:
    {
        "adapter-id": "128",
        "adapter-name": "OSD_128_MGMT_NET2_30",
        "adapter-port": 0,
        "class": "nic",
        "description": "HAMGMT",
        "device-number": "0004",
        "element-id": "5956e97a-f433-11ea-b67c-00106f239d19",
        "element-uri": "/api/partitions/32323df4-f433-11ea-b67c-00106f239d19/nics/5956e97a-f433-11ea-b67c-00106f239d19",
        "mac-address": "02:d2:4d:80:b9:88",
        "name": "HAMGMT0",
        "parent": "/api/partitions/32323df4-f433-11ea-b67c-00106f239d19",
        "ssc-ip-address": null,
        "ssc-ip-address-type": null,
        "ssc-management-nic": false,
        "ssc-mask-prefix": null,
        "type": "osd",
        "virtual-switch-uri": "/api/virtual-switches/db2f0bec-e578-11e8-bd0a-00106f239c31",
        "vlan-id": null,
        "vlan-type": null
    }
"""

import time  # noqa: E402
import logging  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402

from ..module_utils.common import log_init, open_session, close_session, \
    hmc_auth_parameter, Error, ParameterError, wait_for_transition_completion, \
    eq_hex, eq_mac, to_unicode, process_normal_property, missing_required_lib, \
    common_fail_on_import_errors, parse_hmc_host, blanked_params  # noqa: E402

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
LOGGER_NAME = 'zhmc_nic'

LOGGER = logging.getLogger(LOGGER_NAME)

# Dictionary of properties of NIC resources, in this format:
#   name: (allowed, create, update, update_while_active, eq_func, type_cast)
# where:
#   name: Name of the property according to the data model, with hyphens
#     replaced by underscores (this is how it is or would be specified in
#     the 'properties' module parameter).
#   allowed: Indicates whether it is allowed in the 'properties' module
#     parameter.
#   create: Indicates whether it can be specified for the "Create NIC"
#     operation.
#   update: Indicates whether it can be specified for the "Update NIC
#     Properties" operation (at all).
#   update_while_active: Indicates whether it can be specified for the "Update
#     NIC Properties" operation while the partition of the NIC is active. None
#     means "not applicable" (i.e. update=False).
#   eq_func: Equality test function for two values of the property; None means
#     to use Python equality.
#   type_cast: Type cast function for an input value of the property; None
#     means to use it directly. This can be used for example to convert
#     integers provided as strings by Ansible back into integers (that is a
#     current deficiency of Ansible).
# Note: This should always represent the latest version of the HMC/SE.
# Attempts to set a property that does not exist or that is not writeable in
# the target HMC will be handled by the HMC rejecting the operation.
ZHMC_NIC_PROPERTIES = {

    # create+update properties:
    'name': (
        False, True, True, True, None, None),  # provided in 'name' module parm
    'description': (True, True, True, True, None, to_unicode),
    'device_number': (True, True, True, True, eq_hex, None),
    'network_adapter_port_uri': (
        False, True, True, True, None, None),  # via adapter_name/_port
    'virtual_switch_uri': (
        False, True, True, True, None, None),  # via adapter_name/_port
    'adapter_name': (
        True, True, True, True, None,
        None),  # artificial property, type_cast ignored
    'adapter_port': (
        True, True, True, True, None,
        None),  # artificial property, type_cast ignored
    # The ssc-*, vlan-id and mac-address properties were introduced in
    # API version 2.2 (an update of SE 2.13.1).
    # The mac-address property was changed to be writeable in API version 2.20
    # (SE 2.14.0).
    'ssc_management_nic': (True, True, True, True, None, None),
    'ssc_ip_address_type': (True, True, True, True, None, None),
    'ssc_ip_address': (True, True, True, True, None, None),
    'ssc_mask_prefix': (True, True, True, True, None, None),
    'vlan_id': (True, True, True, True, None, int),
    'mac_address': (True, True, True, None, eq_mac, None),
    # The vlan-type property was introduced in API version 2.20 (SE 2.14.0).
    'vlan_type': (True, True, True, True, None, None),
    # The function-* properties were introduced in API version 3.4
    # (SE 2.15 GA2).
    'function_number': (True, True, True, True, None, int),
    'function_range': (True, True, True, True, None, int),

    # read-only properties:
    'element-uri': (False, False, False, None, None, None),
    'element-id': (False, False, False, None, None, None),
    'parent': (False, False, False, None, None, None),
    'class': (False, False, False, None, None, None),
    'type': (False, False, False, None, None, None),
}


def process_properties(partition, nic, params):
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

      partition (zhmcclient.Partition): Partition containing the NIC. Must
        exist.

      nic (zhmcclient.Nic): NIC to be updated with the full set of current
        properties, or `None` if it did not previously exist.

      params (dict): Module input parameters.

    Returns:
      tuple of (create_props, update_props, stop), where:
        * create_props: dict of properties for
          zhmcclient.NicManager.create()
        * update_props: dict of properties for
          zhmcclient.Nic.update_properties()
        * stop (bool): Indicates whether some update properties require the
          partition containg the NIC to be stopped when doing the update.

    Raises:
      ParameterError: An issue with the module parameters.
    """
    create_props = {}
    update_props = {}
    stop = False

    # handle 'name' property
    nic_name = to_unicode(params['name'])
    create_props['name'] = nic_name
    # We looked up the NIC by name, so we will never have to update its name

    # Names of the artificial properties
    adapter_name_art_name = 'adapter_name'
    adapter_port_art_name = 'adapter_port'

    # handle the other properties
    input_props = params['properties']
    if input_props is None:
        input_props = {}
    for prop_name in input_props:

        if prop_name not in ZHMC_NIC_PROPERTIES:
            raise ParameterError(
                f"Property {prop_name!r} is not defined in the data model for "
                "NICs.")

        # pylint: disable=unused-variable
        allowed, create, update, update_while_active, eq_func, type_cast = \
            ZHMC_NIC_PROPERTIES[prop_name]

        if not allowed:
            raise ParameterError(
                f"Property {prop_name!r} is not allowed in the 'properties' "
                "module parameter.")

        if prop_name in (adapter_name_art_name, adapter_port_art_name):
            # Artificial properties will be processed together after this loop
            continue

        # Process a normal (= non-artificial) property
        _create_props, _update_props, _stop = process_normal_property(
            prop_name, ZHMC_NIC_PROPERTIES, input_props, nic)
        create_props.update(_create_props)
        update_props.update(_update_props)
        if _stop:
            stop = True

    # Process artificial properties
    if (adapter_name_art_name in input_props) != \
            (adapter_port_art_name in input_props):
        raise ParameterError(
            f"Artificial properties {adapter_name_art_name!r} and "
            f"{adapter_port_art_name!r} must either both be specified or both "
            "be omitted.")
    if adapter_name_art_name in input_props and \
            adapter_port_art_name in input_props:
        adapter_name = to_unicode(input_props[adapter_name_art_name])
        adapter_port_index = int(input_props[adapter_port_art_name])
        try:
            adapter = partition.manager.cpc.adapters.find(
                name=adapter_name)
        except zhmcclient.NotFound:
            raise ParameterError(
                f"Artificial property {adapter_name_art_name!r} does not "
                f"specify the name of an existing adapter: {adapter_name!r}")
        try:
            port = adapter.ports.find(index=adapter_port_index)
        except zhmcclient.NotFound:
            raise ParameterError(
                f"Artificial property {adapter_port_art_name!r} does not "
                "specify the index of an existing port on adapter "
                f"{adapter_name!r}: {adapter_port_index!r}")

        # The rest of it depends on the network adapter family:
        adapter_family = adapter.get_property('adapter-family')
        if adapter_family in ('roce', 'cna'):
            # Here we perform the same logic as in the property loop, just now
            # simplified by the knowledge about the property flags (create,
            # update, etc.).
            hmc_prop_name = 'network-adapter-port-uri'
            input_prop_value = port.uri
            if nic:
                if nic.properties.get(hmc_prop_name) != input_prop_value:
                    update_props[hmc_prop_name] = input_prop_value
            else:
                update_props[hmc_prop_name] = input_prop_value
            create_props[hmc_prop_name] = input_prop_value
        elif adapter_family in ('osa', 'hipersockets'):
            vswitches = partition.manager.cpc.virtual_switches.findall(
                **{'backing-adapter-uri': adapter.uri})
            # Adapters of this family always have a vswitch (one for each
            # port), so we assert that we can find one or more:
            if not vswitches:
                raise AssertionError()
            found_vswitch = None
            for vswitch in vswitches:
                if vswitch.get_property('port') == adapter_port_index:
                    found_vswitch = vswitch
                    break
            # Because we already checked for the existence of the specified
            # port index, we can now assert that we found the vswitch for that
            # port:
            if not found_vswitch:
                raise AssertionError()
            # Here we perform the same logic as in the property loop, just now
            # simplified by the knowledge about the property flags (create,
            # update, etc.).
            hmc_prop_name = 'virtual-switch-uri'
            input_prop_value = found_vswitch.uri
            if nic:
                if nic.properties.get(hmc_prop_name) != input_prop_value:
                    update_props[hmc_prop_name] = input_prop_value
            else:
                update_props[hmc_prop_name] = input_prop_value
            create_props[hmc_prop_name] = input_prop_value
        else:
            raise ParameterError(
                f"Artificial property {adapter_name_art_name!r} specifies the "
                f"name of a non-network adapter of family {adapter_family!r}: "
                f"{adapter_name!r}")

    return create_props, update_props, stop


class Error_500_12(Error):
    # pylint: disable=invalid-name
    """
    Error while circumventing HTTP 500.12 in find_nic_for_500_12().
    """
    pass


def find_nic_for_500_12(params, partition):
    """
    Circumvention for a defect where "Create NIC" on a Hipersocket adapter
    fails with HTTP 500.12 when the Partition Link feature on z16 is enabled.

    The NIC has been created in this case, but it still has the name that was
    created automatically by the Partition Link support.

    We identify the NIC based on its underlying Hipersockets adapter and the
    device number, and return that NIC.
    """
    # Pull nic-uris property in partition to get the new NIC. If this is done
    # immediately, the number if NICs will not have changed, so we try a few
    # times, with a wait time in between.
    initial_nic_uris = partition.get_property('nic-uris')
    nic_uris = initial_nic_uris
    attempts = 0
    max_attempts = 10
    nic_uri = None
    while True:
        time.sleep(1)
        partition.pull_properties(['nic-uris'])
        nic_uris = partition.get_property('nic-uris')
        if len(nic_uris) == len(initial_nic_uris) + 1:
            nic_uri = next(iter(set(nic_uris) - set(initial_nic_uris)))
            LOGGER.debug(
                "Found NIC URI after %d attempts: %r", attempts, nic_uri)
            break
        attempts += 1
        if attempts >= max_attempts:
            LOGGER.warning(
                "Could not get partition property 'nic-uris' updated with "
                "new NIC after %d attempts, trying filtering", attempts)
            break
    if nic_uri:
        LOGGER.debug(
            "Finding NIC by URI %r", nic_uri)
        filter_args = {
            'element-uri': nic_uri,
        }
        try:
            nic = partition.nics.find(**filter_args)
        except zhmcclient.NotFound:
            raise Error_500_12(
                f"Cannot find NIC with URI {nic_uri!r}"
            )
    else:
        try:
            props = params['properties']
            adapter_name = props['adapter_name']
            adapter_port_index = int(props['adapter_port'])
            device_number = props['device_number']
        except KeyError:
            raise Error_500_12(
                "Not all input parameters provided that are required for the "
                "circumvention: adapter_name, adapter_port, device_number"
            )
        try:
            adapter = partition.manager.cpc.adapters.find(name=adapter_name)
            adapter.ports.find(index=adapter_port_index)
        except zhmcclient.HTTPError as exc:
            raise Error_500_12(
                f"Cannot find adapter {adapter_name!r} or port "
                f"{adapter_port_index!r}: {exc}"
            )
        adapter_family = adapter.get_property('adapter-family')
        if adapter_family != 'hipersockets':
            raise Error_500_12(
                "HTTP error 500.12 happened for a non-Hipersockets adapter "
                f"{adapter_name!r}"
            )
        try:
            vswitches = partition.manager.cpc.virtual_switches.findall(
                **{'backing-adapter-uri': adapter.uri})
        except zhmcclient.HTTPError as exc:
            raise Error_500_12(
                "Cannot find virtual switch for backing adapter "
                f"{adapter_name!r}: {exc}"
            )
        found_vswitch = None
        for vswitch in vswitches:
            if vswitch.get_property('port') == adapter_port_index:
                found_vswitch = vswitch
                break
        if not found_vswitch:
            raise Error_500_12(
                f"Cannot find virtual switch for port {adapter_port_index!r} "
                f"on backing adapter {adapter_name!r}"
            )
        filter_args = {
            'type': 'iqd',
            'device-number': device_number,
            'virtual-switch-uri': found_vswitch.uri,
        }
        LOGGER.debug(
            "Finding NIC by filter arguments: %r", filter_args)
        try:
            nic = partition.nics.find(**filter_args)
        except zhmcclient.NotFound:
            raise Error_500_12(
                f"Cannot find NIC with filter arguments {filter_args!r}"
            )
    return nic


def ensure_present(params, check_mode):
    """
    Ensure that the NIC exists and has the specified properties.

    Raises:
      ParameterError: An issue with the module parameters.
      StatusError: An issue with the partition status.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    cpc_name = params['cpc_name']
    partition_name = params['partition_name']
    nic_name = params['name']

    changed = False
    result = {}

    session, logoff = open_session(params)
    try:
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        try:
            partition = cpc.partitions.find(name=partition_name)
        except zhmcclient.NotFound:
            if check_mode:
                # Once the partition is created, the NIC will also need to be
                # created. Therefore, we set changed.
                changed = True
                return changed, result
            raise

        try:
            nic = partition.nics.find(name=nic_name)
            nic.pull_full_properties()
        except zhmcclient.NotFound:
            nic = None

        if not nic:
            # It does not exist. Create it and update it if there are
            # update-only properties.
            if not check_mode:
                create_props, update_props, stop = process_properties(
                    partition, nic, params)
                try:
                    nic = partition.nics.create(create_props)
                except zhmcclient.HTTPError as exc:
                    if exc.http_status == 500 and exc.reason == 12:
                        # Circumvention for a defect that happens with
                        # Hipersocket NICs when the Partition Link feature on
                        # z16 is enabled.
                        LOGGER.warning(
                            "Circumventing HTTP 500.12 when creating NIC %r "
                            "on partition %r", nic_name, partition.name)
                        nic = find_nic_for_500_12(params, partition)
                        create_props, update_props, stop = process_properties(
                            partition, nic, params)
                        update_props['name'] = create_props.pop('name')
                        if 'virtual-switch-uri' in update_props:
                            del update_props['virtual-switch-uri']
                        if 'virtual-switch-uri' in create_props:
                            del create_props['virtual-switch-uri']
                        LOGGER.debug(
                            "Updating NIC properties for HTTP 500.12 "
                            "circumvention: %r", update_props)
                    else:
                        raise
                update2_props = {}
                for name, value in update_props.items():
                    if name not in create_props:
                        update2_props[name] = value
                if update2_props:
                    nic.update_properties(update2_props)
                # We refresh the properties after the update, in case an
                # input property value gets changed (for example, the
                # partition does that with memory properties).
                nic.pull_full_properties()
            else:
                # TODO: Show props in module result also in check mode.
                pass
            changed = True
        else:
            # It exists. Stop the partition if needed due to the NIC property
            # update requirements, or wait for an updateable partition status,
            # and update the NIC properties.
            create_props, update_props, stop = process_properties(
                partition, nic, params)
            if update_props:
                if not check_mode:
                    # NIC properties can all be updated while the partition is
                    # active, therefore:
                    if stop:
                        raise AssertionError()
                    wait_for_transition_completion(LOGGER, partition)
                    nic.update_properties(update_props)
                    # We refresh the properties after the update, in case an
                    # input property value gets changed (for example, the
                    # partition does that with memory properties).
                    nic.pull_full_properties()
                else:
                    # TODO: Show updated props in mod.result also in chk.mode
                    pass
                changed = True

        if nic:
            result = dict(nic.properties)

        return changed, result

    finally:
        close_session(session, logoff)


def ensure_absent(params, check_mode):
    """
    Ensure that the NIC does not exist.

    Raises:
      ParameterError: An issue with the module parameters.
      StatusError: An issue with the partition status.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    cpc_name = params['cpc_name']
    partition_name = params['partition_name']
    nic_name = params['name']

    changed = False
    result = {}

    session, logoff = open_session(params)
    try:
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        partition = cpc.partitions.find(name=partition_name)
        # The default exception handling is sufficient for the above.

        try:
            nic = partition.nics.find(name=nic_name)
        except zhmcclient.NotFound:
            return changed, result

        if not check_mode:
            nic.delete()
        changed = True

        return changed, result

    finally:
        close_session(session, logoff)


def facts(params, check_mode):
    # pylint: disable=unused-argument
    """
    Return NIC facts.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    cpc_name = params['cpc_name']
    partition_name = params['partition_name']
    name = params['name']

    changed = False
    result = {}

    session, logoff = open_session(params)
    try:
        # The default exception handling is sufficient for this code
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)

        partition = cpc.partitions.find(name=partition_name)

        nic = partition.nics.find(name=name)
        nic.pull_full_properties()

        result = dict(nic.properties)
        return changed, result

    finally:
        close_session(session, logoff)


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
        "facts": facts,
    }
    return actions[params['state']](params, check_mode)


def main():
    """Main function"""

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='raw'),
        hmc_auth=hmc_auth_parameter(),
        cpc_name=dict(required=True, type='str'),
        partition_name=dict(required=True, type='str'),
        name=dict(required=True, type='str'),
        state=dict(required=True, type='str',
                   choices=['absent', 'present', 'facts']),
        properties=dict(required=False, type='dict', default=None),
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

        changed, result = perform_task(module.params, module.check_mode)

    except (Error, zhmcclient.Error) as exc:
        # These exceptions are considered errors in the environment or in user
        # input. They have a proper message that stands on its own, so we
        # simply pass that message on and will not need a traceback.
        msg = f"{exc.__class__.__name__}: {exc}"
        LOGGER.debug(
            "Module exit (failure): msg: %s", msg)
        module.fail_json(msg=msg)
    # Other exceptions are considered module errors and are handled by Ansible
    # by showing the traceback.

    LOGGER.debug(
        "Module exit (success): changed: %r, nic: %r", changed, result)
    module.exit_json(changed=changed, nic=result)


if __name__ == '__main__':
    main()
