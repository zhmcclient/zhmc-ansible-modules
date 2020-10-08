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
    wait_for_transition_completion, eq_hex, eq_mac, get_hmc_auth, \
    get_session, to_unicode, process_normal_property

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
module: zhmc_nic
version_added: "0.0"
short_description: Manages NICs in existing partitions
description:
  - Creates, updates, and deletes NICs in existing partitions of a CPC.
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
      - The name of the CPC with the partition containing the NIC.
    required: true
  partition_name:
    description:
      - The name of the partition containing the NIC.
    required: true
  name:
    description:
      - The name of the target NIC that is managed. If the NIC needs to be
        created, this value becomes its name.
    required: true
  state:
    description:
      - "The desired state for the target NIC:"
      - "C(absent): Ensures that the NIC does not exist in the specified
         partition."
      - "C(present): Ensures that the NIC exists in the specified partition
         and has the specified properties."
    required: true
    choices: ["absent", "present"]
  properties:
    description:
      - "Dictionary with input properties for the NIC, for C(state=present).
         Key is the property name with underscores instead of hyphens, and
         value is the property value in YAML syntax. Integer properties may
         also be provided as decimal strings. Will be ignored for
         C(state=absent)."
      - "The possible input properties in this dictionary are the properties
         defined as writeable in the data model for NIC resources (where the
         property names contain underscores instead of hyphens), with the
         following exceptions:"
      - "* C(name): Cannot be specified because the name has already been
         specified in the C(name) module parameter."
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
"""

RETURN = """
nic:
  description:
    - "For C(state=absent), an empty dictionary."
    - "For C(state=present), a dictionary with the resource properties of the
       NIC (after changes, if any). The dictionary keys are the exact property
       names as described in the data model for the resource, i.e. they contain
       hyphens (-), not underscores (_). The dictionary values are the property
       values using the Python representations described in the documentation
       of the zhmcclient Python package."
  returned: success
  type: dict
  sample: |
    C({
      "name": "nic-1",
      "description": "NIC #1",
      "virtual-switch-uri': "/api/vswitches/...",
      ...
    })
"""

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
    input_props = params.get('properties', {})
    if input_props is None:
        input_props = {}
    for prop_name in input_props:

        if prop_name not in ZHMC_NIC_PROPERTIES:
            raise ParameterError(
                "Property {!r} is not defined in the data model for "
                "NICs.".format(prop_name))

        allowed, create, update, update_while_active, eq_func, type_cast = \
            ZHMC_NIC_PROPERTIES[prop_name]

        if not allowed:
            raise ParameterError(
                "Property {!r} is not allowed in the 'properties' module "
                "parameter.".format(prop_name))

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
            "Artificial properties {!r} and {!r} must either both be "
            "specified or both be omitted.".
            format(adapter_name_art_name, adapter_port_art_name))
    if adapter_name_art_name in input_props and \
            adapter_port_art_name in input_props:
        adapter_name = to_unicode(input_props[adapter_name_art_name])
        adapter_port_index = int(input_props[adapter_port_art_name])
        try:
            adapter = partition.manager.cpc.adapters.find(
                name=adapter_name)
        except zhmcclient.NotFound:
            raise ParameterError(
                "Artificial property {!r} does not specify the name of an "
                "existing adapter: {!r}".
                format(adapter_name_art_name, adapter_name))
        try:
            port = adapter.ports.find(index=adapter_port_index)
        except zhmcclient.NotFound:
            raise ParameterError(
                "Artificial property {!r} does not specify the index of an "
                "existing port on adapter {!r}: {!r}".
                format(adapter_port_art_name, adapter_name,
                       adapter_port_index))

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
            assert vswitches
            found_vswitch = None
            for vswitch in vswitches:
                if vswitch.get_property('port') == adapter_port_index:
                    found_vswitch = vswitch
                    break
            # Because we already checked for the existence of the specified
            # port index, we can now assert that we found the vswitch for that
            # port:
            assert found_vswitch
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
                "Artificial property {!r} specifies the name of a non-network "
                "adapter of family {!r}: {!r}".
                format(adapter_name_art_name, adapter_family, adapter_name))

    return create_props, update_props, stop


def ensure_present(params, check_mode):
    """
    Ensure that the NIC exists and has the specified properties.

    Raises:
      ParameterError: An issue with the module parameters.
      StatusError: An issue with the partition status.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['cpc_name']
    partition_name = params['partition_name']
    nic_name = params['name']
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
                nic = partition.nics.create(create_props)
                update2_props = {}
                for name in update_props:
                    if name not in create_props:
                        update2_props[name] = update_props[name]
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
                    assert not stop
                    wait_for_transition_completion(partition)
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
            result = nic.properties

        return changed, result

    finally:
        session.logoff()


def ensure_absent(params, check_mode):
    """
    Ensure that the NIC does not exist.

    Raises:
      ParameterError: An issue with the module parameters.
      StatusError: An issue with the partition status.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['cpc_name']
    partition_name = params['partition_name']
    nic_name = params['name']
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
            nic = partition.nics.find(name=nic_name)
        except zhmcclient.NotFound:
            return changed, result

        if not check_mode:
            nic.delete()
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
    module.exit_json(changed=changed, nic=result)


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings()
    main()
