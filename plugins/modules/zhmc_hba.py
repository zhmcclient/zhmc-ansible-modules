#!/usr/bin/python
# Copyright 2017-2020 IBM Corp. All Rights Reserved.
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
module: zhmc_hba
version_added: "2.9.0"
short_description: Create HBAs in partitions
description:
  - Create, update, or delete an HBA (virtual Host Bus Adapter) in a partition
    of a CPC (Z system).
  - Note that the Ansible module zhmc_partition can be used to gather facts
    about existing HBAs of a partition.
author:
  - Andreas Maier (@andy-maier)
  - Andreas Scheuring (@scheuran)
  - Juergen Leopold (@leopoldjuergen)
requirements:
  - The targeted Z system must be a z13 generation and must be in the Dynamic
    Partition Manager (DPM) operational mode. The z14 and later generations
    in DPM mode manage HBAs automatically via the "dpm-storage-management"
    firmware feature.
  - "The HMC userid must have these task permissions:
    'Partition Details'."
  - "The HMC userid must have object-access permissions to these objects:
    Partitions of the target HBAs, CPCs of these partitions, storage adapters
    backing the target HBAs."
options:
  hmc_host:
    description:
      - The hostname or IP address of the HMC.
    type: str
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
            This is mutually exclusive with providing C(session_id).
        type: str
        required: false
        default: null
      password:
        description:
          - The password for authenticating with the HMC.
            This is mutually exclusive with providing C(session_id).
        type: str
        required: false
        default: null
      session_id:
        description:
          - HMC session ID to be used.
            This is mutually exclusive with providing C(userid) and C(password)
            and can be created as described in :ref:`zhmc_session_module`.
        type: str
        required: false
        default: null
      ca_certs:
        description:
          - Path name of certificate file or certificate directory to be used
            for verifying the HMC certificate. If null (default), the path name
            in the 'REQUESTS_CA_BUNDLE' environment variable or the path name
            in the 'CURL_CA_BUNDLE' environment variable is used, or if neither
            of these variables is set, the certificates in the Mozilla CA
            Certificate List provided by the 'certifi' Python package are used
            for verifying the HMC certificate.
        type: str
        required: false
        default: null
      verify:
        description:
          - If True (default), verify the HMC certificate as specified in the
            C(ca_certs) parameter. If False, ignore what is specified in the
            C(ca_certs) parameter and do not verify the HMC certificate.
        type: bool
        required: false
        default: true
  cpc_name:
    description:
      - The name of the CPC with the partition containing the HBA.
    type: str
    required: true
  partition_name:
    description:
      - The name of the partition containing the HBA.
    type: str
    required: true
  name:
    description:
      - The name of the target HBA that is managed. If the HBA needs to be
        created, this value becomes its name.
    type: str
    required: true
  state:
    description:
      - "The desired state for the HBA. All states are fully idempotent
         within the limits of the properties that can be changed:"
      - "* C(absent): Ensures that the HBA does not exist in the specified
         partition."
      - "* C(present): Ensures that the HBA exists in the specified partition
         and has the specified properties."
    type: str
    required: true
    choices: ["absent", "present"]
  properties:
    description:
      - "Dictionary with input properties for the HBA, for C(state=present).
         Key is the property name with underscores instead of hyphens, and
         value is the property value in YAML syntax. Integer properties may
         also be provided as decimal strings. Will be ignored for
         C(state=absent)."
      - "The possible input properties in this dictionary are the properties
         defined as writeable in the data model for HBA resources (where the
         property names contain underscores instead of hyphens), with the
         following exceptions:"
      - "* C(name): Cannot be specified because the name has already been
         specified in the C(name) module parameter."
      - "* C(adapter_port_uri): Cannot be specified because this information is
         specified using the artificial properties C(adapter_name) and
         C(adapter_port)."
      - "* C(adapter_name): The name of the adapter that has the port backing
         the target HBA. Cannot be changed after the HBA exists."
      - "* C(adapter_port): The port index of the adapter port backing the
         target HBA. Cannot be changed after the HBA exists."
      - "Properties omitted in this dictionary will remain unchanged when the
         HBA already exists, and will get the default value defined in the
         data model for HBAs when the HBA is being created."
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
    required: false
    type: raw
    default: null
"""

EXAMPLES = """
---
# Note: The following examples assume that some variables named 'my_*' are set.

- name: Ensure HBA exists in the partition
  zhmc_partition:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    partition_name: "{{ my_partition_name }}"
    name: "{{ my_hba_name }}"
    state: present
    properties:
      adapter_name: FCP-1
      adapter_port: 0
      description: "The port to our V7K #1"
      device_number: "123F"
  register: hba1

- name: Ensure HBA does not exist in the partition
  zhmc_partition:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    partition_name: "{{ my_partition_name }}"
    name: "{{ my_hba_name }}"
    state: absent
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
hba:
  description:
    - "For C(state=absent), an empty dictionary."
    - "For C(state=present), the resource properties of the HBA after any
       changes."
  returned: success
  type: dict
  contains:
    name:
      description: "HBA name"
      type: str
    "{property}":
      description: "Additional properties of the HBA, as described in the data
        model of the 'HBA' element object of the 'Partition' object in the
        :term:`HMC API` book.
        The property names have hyphens (-) as described in that book."
"""

import logging  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402

from ..module_utils.common import log_init, open_session, close_session, \
    Error, ParameterError, wait_for_transition_completion, eq_hex, \
    to_unicode, process_normal_property, missing_required_lib, \
    common_fail_on_import_errors  # noqa: E402

try:
    import requests.packages.urllib3
    IMP_URLLIB3_ERR = None
except ImportError:
    IMP_URLLIB3_ERR = traceback.format_exc()

try:
    import zhmcclient
    IMP_ZHMCCLIENT_ERR = None
except ImportError:
    IMP_ZHMCCLIENT_ERR = traceback.format_exc()


# Python logger name for this module
LOGGER_NAME = 'zhmc_hba'

LOGGER = logging.getLogger(LOGGER_NAME)

# Dictionary of properties of HBA resources, in this format:
#   name: (allowed, create, update, update_while_active, eq_func, type_cast)
# where:
#   name: Name of the property according to the data model, with hyphens
#     replaced by underscores (this is how it is or would be specified in
#     the 'properties' module parameter).
#   allowed: Indicates whether it is allowed in the 'properties' module
#     parameter.
#   create: Indicates whether it can be specified for the "Create HBA"
#     operation.
#   update: Indicates whether it can be specified for the "Update HBA
#     Properties" operation (at all).
#   update_while_active: Indicates whether it can be specified for the "Update
#     HBA Properties" operation while the partition of the HBA is active. None
#     means "not applicable" (i.e. update=False).
#   eq_func: Equality test function for two values of the property; None means
#     to use Python equality.
#   type_cast: Type cast function for an input value of the property; None
#     means to use it directly. This can be used for example to convert
#     integers provided as strings by Ansible back into integers (that is a
#     current deficiency of Ansible).
ZHMC_HBA_PROPERTIES = {

    # create-only properties:
    'adapter_port_uri': (
        False, True, False, None, None, None),  # via adapter_name/_port
    'adapter_name': (
        True, True, False, None, None,
        None),  # artificial property, type_cast ignored
    'adapter_port': (
        True, True, False, None, None,
        None),  # artificial property, type_cast ignored

    # create+update properties:
    'name': (
        False, True, True, True, None, None),  # provided in 'name' module parm
    'description': (True, True, True, True, None, to_unicode),
    'device_number': (True, True, True, True, eq_hex, None),

    # read-only properties:
    'element-uri': (False, False, False, None, None, None),
    'element-id': (False, False, False, None, None, None),
    'parent': (False, False, False, None, None, None),
    'class': (False, False, False, None, None, None),
    'wwpn': (False, False, False, None, None, None),
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
    hba_name = to_unicode(params['name'])
    create_props['name'] = hba_name
    # We looked up the HBA by name, so we will never have to update its name

    # Names of the artificial properties
    adapter_name_art_name = 'adapter_name'
    adapter_port_art_name = 'adapter_port'

    # handle the other properties
    input_props = params.get('properties', {})
    if input_props is None:
        input_props = {}
    for prop_name in input_props:

        if prop_name not in ZHMC_HBA_PROPERTIES:
            raise ParameterError(
                "Property {0!r} is not defined in the data model for "
                "HBAs.".format(prop_name))

        allowed, create, update, update_while_active, eq_func, type_cast = \
            ZHMC_HBA_PROPERTIES[prop_name]

        if not allowed:
            raise ParameterError(
                "Property {0!r} is not allowed in the 'properties' module "
                "parameter.".format(prop_name))

        if prop_name in (adapter_name_art_name, adapter_port_art_name):
            # Artificial properties will be processed together after this loop
            continue

        # Process a normal (= non-artificial) property
        _create_props, _update_props, _stop = process_normal_property(
            prop_name, ZHMC_HBA_PROPERTIES, input_props, hba)
        create_props.update(_create_props)
        update_props.update(_update_props)
        if _stop:
            stop = True

    # Process artificial properties
    if (adapter_name_art_name in input_props) != \
            (adapter_port_art_name in input_props):
        raise ParameterError(
            "Artificial properties {0!r} and {1!r} must either both be "
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
                "Artificial property {0!r} does not specify the name of an "
                "existing adapter: {1!r}".
                format(adapter_name_art_name, adapter_name))
        try:
            port = adapter.ports.find(index=adapter_port_index)
        except zhmcclient.NotFound:
            raise ParameterError(
                "Artificial property {0!r} does not specify the index of an "
                "existing port on adapter {1!r}: {2!r}".
                format(adapter_port_art_name, adapter_name,
                       adapter_port_index))
        hmc_prop_name = 'adapter-port-uri'
        if hba:
            existing_port_uri = hba.get_property(hmc_prop_name)
            if port.uri != existing_port_uri:
                raise ParameterError(
                    "Artificial properties {0!r} and {1!r} cannot be used to "
                    "change the adapter port of an existing HBA".
                    format(adapter_name_art_name, adapter_port_art_name))
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

    cpc_name = params['cpc_name']
    partition_name = params['partition_name']
    hba_name = params['name']

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
                # Once the partition is created, the HBA will also need to be
                # created. Therefore, we set changed.
                changed = True
                return changed, result
            raise

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
                for name, value in update_props.items():
                    if name not in create_props:
                        update2_props[name] = value
                if update2_props:
                    hba.update_properties(update2_props)
                # We refresh the properties after the update, in case an
                # input property value gets changed (for example, the
                # partition does that with memory properties).
                hba.pull_full_properties()
            else:
                # TODO: Show props in module result also in check mode.
                pass
            changed = True
        else:
            # It exists. Stop the partition if needed due to the HBA property
            # update requirements, or wait for an updateable partition status,
            # and update the HBA properties.
            create_props, update_props, stop = process_properties(
                partition, hba, params)
            if update_props:
                if not check_mode:
                    # HBA properties can all be updated while the partition is
                    # active, therefore:
                    if stop:
                        raise AssertionError()

                    wait_for_transition_completion(partition)
                    hba.update_properties(update_props)
                    # We refresh the properties after the update, in case an
                    # input property value gets changed (for example, the
                    # partition does that with memory properties).
                    hba.pull_full_properties()
                else:
                    # TODO: Show updated props in mod.result also in chk.mode
                    pass
                changed = True

        if hba:
            result = dict(hba.properties)

        return changed, result

    finally:
        close_session(session, logoff)


def ensure_absent(params, check_mode):
    """
    Ensure that the HBA does not exist.

    Raises:
      ParameterError: An issue with the module parameters.
      StatusError: An issue with the partition status.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    cpc_name = params['cpc_name']
    partition_name = params['partition_name']
    hba_name = params['name']

    changed = False
    result = {}

    session, logoff = open_session(params)
    try:
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
    }
    return actions[params['state']](params, check_mode)


def main():

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='str'),
        hmc_auth=dict(
            required=True,
            type='dict',
            options=dict(
                userid=dict(required=False, type='str', default=None),
                password=dict(required=False, type='str', default=None,
                              no_log=True),
                session_id=dict(required=False, type='str', default=None,
                                no_log=True),
                ca_certs=dict(required=False, type='str', default=None),
                verify=dict(required=False, type='bool', default=True),
            ),
        ),
        cpc_name=dict(required=True, type='str'),
        partition_name=dict(required=True, type='str'),
        name=dict(required=True, type='str'),
        state=dict(required=True, type='str',
                   choices=['absent', 'present']),
        properties=dict(required=False, type='dict', default={}),
        log_file=dict(required=False, type='str', default=None),
        _faked_session=dict(required=False, type='raw'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True)

    if IMP_URLLIB3_ERR is not None:
        module.fail_json(msg=missing_required_lib("requests"),
                         exception=IMP_URLLIB3_ERR)

    requests.packages.urllib3.disable_warnings()

    if IMP_ZHMCCLIENT_ERR is not None:
        module.fail_json(msg=missing_required_lib("zhmcclient"),
                         exception=IMP_ZHMCCLIENT_ERR)

    common_fail_on_import_errors(module)

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
        LOGGER.debug(
            "Module exit (failure): msg: %r", msg)
        module.fail_json(msg=msg)
    # Other exceptions are considered module errors and are handled by Ansible
    # by showing the traceback.

    LOGGER.debug(
        "Module exit (success): changed: %r, cpc: %r", changed, result)
    module.exit_json(changed=changed, hba=result)


if __name__ == '__main__':
    main()
