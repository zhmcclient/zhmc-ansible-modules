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
    get_hmc_auth, get_session, to_unicode, process_normal_property, eq_hex

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
module: zhmc_adapter
version_added: "0.6"
short_description: Manages an adapter in a CPC.
description:
  - Gathers facts about the adapter including its ports.
  - Updates the properties of an adapter.
notes:
author:
  - Andreas Maier (@andy-maier, maiera@de.ibm.com)
  - Andreas Scheuring (@scheuran, scheuran@de.ibm.com)
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
  name:
    description:
      - The name of the target adapter. In case of renaming an adapter, this is
        the new name of the adapter.
    required: true
  match:
    description:
      - "Only for C(state=set): Match properties for identifying the
         target adapter in the set of adapters in the CPC, if an adapter with
         the name specified in the C(name) module parameter does not exist in
         that set. This parameter will be ignored otherwise."
      - "Use of this parameter allows renaming an adapter:
         The C(name) module parameter specifies the new name of the target
         adapter, and the C(match) module parameter identifies the adapter to
         be renamed.
         This can be combined with other property updates by using the
         C(properties) module parameter."
      - "The parameter is a dictionary. The key of each dictionary item is the
         property name as specified in the data model for adapter resources,
         with underscores instead of hyphens. The value of each dictionary item
         is the match value for the property (in YAML syntax). Integer
         properties may also be provided as decimal strings."
      - "The specified match properties follow the rules of filtering for the
         zhmcclient library as described in
         https://python-zhmcclient.readthedocs.io/en/stable/concepts.html#filtering"
      - "The possible match properties are all properties in the data model for
         adapter resources, including C(name)."
    required: false
    default: No match properties
  state:
    description:
      - "The desired state for the attachment:"
      - "* C(set): Ensures that an existing adapter has the specified
         properties."
      - "* C(present): Ensures that a Hipersockets adapter exists and has the
         specified properties."
      - "* C(absent): Ensures that a Hipersockets adapter does not exist."
      - "* C(facts): Does not change anything on the adapter and returns
         the adapter properties including its ports."
    required: true
    choices: ['set', 'present', 'absent', 'facts']
  properties:
    description:
      - "Only for C(state=set|present): New values for the properties of the
         adapter.
         Properties omitted in this dictionary will remain unchanged.
         This parameter will be ignored for other states."
      - "The parameter is a dictionary. The key of each dictionary item is the
         property name as specified in the data model for adapter resources,
         with underscores instead of hyphens. The value of each dictionary item
         is the property value (in YAML syntax). Integer properties may also be
         provided as decimal strings."
      - "The possible properties in this dictionary are the properties
         defined as writeable in the data model for adapter resources, with the
         following exceptions:"
      - "* C(name): Cannot be specified as a property because the name has
         already been specified in the C(name) module parameter."
      - "* C(type): The desired adapter type can be specified in order to
         support adapters that can change their type (e.g. the FICON Express
         adapter can change its type between 'not-configured', 'fcp' and
         'fc')."
      - "* C(crypto_type): The crypto type can be specified in order to support
         the ability of the Crypto Express adapters to change their crypto
         type. Valid values are 'ep11', 'cca' and 'acc'. Changing to 'acc'
         will zeroize the crypto adapter."
    required: false
    default: No property changes (other than possibly C(name)).
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

- name: Gather facts about an existing adapter
  zhmc_adapter:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    name: "{{ my_adapter_name }}"
    state: facts
  register: adapter1

- name: Ensure an existing adapter has the desired property values
  zhmc_adapter:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    name: "{{ my_adapter_name }}"
    state: set
    properties:
      description: "This is adapter {{ my_adapter_name }}"
  register: adapter1

- name: "Ensure the existing adapter identified by its name or adapter ID has
         the desired name and property values"
  zhmc_adapter:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    name: "{{ my_adapter_name }}"
    match:
      adapter_id: "12C"
    state: set
    properties:
      description: "This is adapter {{ my_adapter_name }}"
  register: adapter1

- name: "Ensure a Hipersockets adapter exists and has the desired property
         values"
  zhmc_adapter:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    name: "{{ my_adapter_name }}"
    state: present
    properties:
      type: hipersockets
      description: "This is Hipersockets adapter {{ my_adapter_name }}"
  register: adapter1

- name: "Ensure a Hipersockets adapter does not exist"
  zhmc_adapter:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    name: "{{ my_adapter_name }}"
    state: absent

"""

RETURN = """
cpc:
  description:
    - "For C(state=absent), an empty dictionary."
    - "For C(state=set|present|facts), a dictionary with the properties of the
       adapter. The properties contain these additional artificial properties
       for listing its child resources:
       - 'ports': The ports of the adapter, as a dict of key:
         port name, value: dict of a subset of the port properties
         (name, status, element_uri)."
  returned: success
  type: dict
  sample: |
    C({
      "name": "adapter-1",
      "description": "Adapter 1",
      "status": "active",
      "acceptable_status": [ "active" ],
      ...
      "ports": [
        {
          "name": "Port 0",
          ...
        },
        ...
      ]
    })
"""

# Python logger name for this module
LOGGER_NAME = 'zhmc_adapter'

LOGGER = logging.getLogger(LOGGER_NAME)

# Dictionary of properties of adapter resources, in this format:
#   name: (allowed, create, update, eq_func, type_cast)
# where:
#   name: Name of the property according to the data model, with hyphens
#     replaced by underscores (this is how it is or would be specified in
#     the 'properties' module parameter).
#   allowed: Indicates whether it is allowed in the 'properties' module
#     parameter.
#   create: Indicates whether it can be specified for the "Create Hipersockets
#     Adapter" operation (that is the only type of creatable adapter).
#   update: Indicates whether it can be specified for the "Modify Adapter
#     Properties" operation (at all).
#   update_while_active: Indicates whether it can be specified for the "Modify
#     Adapter Properties" operation while the adapter is active. None means
#     "not applicable" (used for update=False).
#   eq_func: Equality test function for two values of the property; None means
#     to use Python equality.
#   type_cast: Type cast function for an input value of the property; None
#     means to use it directly. This can be used for example to convert
#     integers provided as strings by Ansible back into integers (that is a
#     current deficiency of Ansible).
ZHMC_ADAPTER_PROPERTIES = {

    # create-only properties: None

    # update-only properties:
    'crypto_type': (True, False, True, True, None, None),
    # crypto_type: used for Change Crypto Type
    'allowed_capacity': (True, False, True, True, None, int),
    'channel_path_id': (True, False, True, True, eq_hex, None),
    'crypto_number': (True, False, True, True, None, int),
    'tke_commands_enabled': (True, False, True, True, None, None),

    # create+update properties: (create is for hipersockets)
    'name': (False, True, True, True, None, None),  # in 'name' parm
    'description': (True, True, True, True, None, to_unicode),
    'maximum_transmission_unit_size': (True, True, True, True, None, int),
    'type': (True, True, True, True, None, None),
    # type used for Create Hipersockets and for Change Adapter Type

    # read-only properties:
    'object_uri': (False, None, False, None, None, None),
    'object_id': (False, None, False, None, None, None),
    'parent': (False, None, False, None, None, None),
    'class': (False, None, False, None, None, None),
    'status': (False, None, False, None, None, None),
    'adapter_id': (False, None, False, None, None, None),
    'adapter_family': (False, None, False, None, None, None),
    'detected_card_type': (False, None, False, None, None, None),
    'card_location': (False, None, False, None, None, None),
    'port_count': (False, None, False, None, None, None),
    'network_port_uris': (False, None, False, None, None, None),
    'storage_port_uris': (False, None, False, None, None, None),
    'state': (False, None, False, None, None, None),
    'configured_capacity': (False, None, False, None, None, None),
    'used_capacity': (False, None, False, None, None, None),
    'maximum_total_capacity': (False, None, False, None, None, None),
    'physical_channel_status': (False, None, False, None, None, None),
    'udx_loaded': (False, None, False, None, None, None),
}


# Conversion of crypto types between module parameter values and HMC values
CRYPTO_TYPES_MOD2HMC = {
    'acc': 'accelerator',
    'cca': 'cca-coprocessor',
    'ep11': 'ep11-coprocessor',
}


def process_properties(adapter, params):
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

      adapter (zhmcclient.Adapter): Existing adapter to be updated, or `None`
        if the adapter does not exist.

      params (dict): Module input parameters.

    Returns:
      tuple of (create_props, update_props), where:
        * create_props: dict of properties from params that may be specified
          in zhmcclient.AdapterManager.create_hipersocket() (may overlap with
          update_props).
        * update_props: dict of properties from params that may be specified
          in zhmcclient.Adapter.update_properties() (may overlap with
          create_props).
        * change_adapter_type: String with new adapter type (i.e. input for
          Change Adapter Type operation), or None if no change needed.
        * change_crypto_type: String with new crypto type (i.e. input for
          Change Crypto Type operation), or None if no change needed.

    Raises:
      ParameterError: An issue with the module parameters.
    """

    # Prepare return values
    create_props = {}
    update_props = {}
    change_adapter_type = None  # New adapter type, if needed
    change_crypto_type = None  # New crypto type, if needed

    # handle the 'name' module parameter
    adapter_name = to_unicode(params['name'])
    if adapter and adapter.properties.get('name', None) == adapter_name:
        pass  # adapter exists and has the desired name
    else:
        create_props['name'] = adapter_name
        update_props['name'] = adapter_name

    # handle the other input properties
    input_props = params.get('properties', None)
    if input_props is None:
        input_props = {}
    for prop_name in input_props:

        try:
            allowed, create, update, update_active, eq_func, type_cast = \
                ZHMC_ADAPTER_PROPERTIES[prop_name]
        except KeyError:
            allowed = False

        if not allowed:
            raise ParameterError(
                "Invalid adapter property {!r} specified in the 'properties' "
                "module parameter.".format(prop_name))

        if adapter and prop_name == 'type':
            # Determine need to change the adapter type
            _current_adapter_type = adapter.properties.get('type', None)
            _input_adapter_type = input_props[prop_name]
            if _input_adapter_type != _current_adapter_type:
                change_adapter_type = _input_adapter_type
        elif adapter and prop_name == 'crypto_type':
            # Determine need to change the crypto type
            _current_crypto_type = adapter.properties.get('crypto-type', None)
            _input_crypto_type = CRYPTO_TYPES_MOD2HMC[input_props[prop_name]]
            if _input_crypto_type != _current_crypto_type:
                change_crypto_type = _input_crypto_type
        else:
            # Process a normal (= non-artificial) property
            _create_props, _update_props, _stop = process_normal_property(
                prop_name, ZHMC_ADAPTER_PROPERTIES, input_props, adapter)
            create_props.update(_create_props)
            update_props.update(_update_props)
            assert _stop is False

    return create_props, update_props, change_adapter_type, change_crypto_type


def identify_adapter(cpc, name, match_props):
    """
    Identify the target adapter based on its name, or if an adapter with that
    name does not exist in the CPC, based on its match properties.
    """
    try:
        adapter = cpc.adapters.find(name=name)
    except zhmcclient.NotFound:
        if not match_props:
            raise
        match_props_hmc = dict()
        for prop_name in match_props:
            prop_name_hmc = prop_name.replace('_', '-')
            match_value = match_props[prop_name]

            # Apply type cast from property definition also to match values:
            if prop_name in ZHMC_ADAPTER_PROPERTIES:
                type_cast = ZHMC_ADAPTER_PROPERTIES[prop_name][5]
                if type_cast:
                    match_value = type_cast(match_value)

            match_props_hmc[prop_name_hmc] = match_value
        adapter = cpc.adapters.find(**match_props_hmc)
    return adapter


def ensure_set(params, check_mode):
    """
    Identify the target adapter (that must exist) and ensure that the specified
    properties are set on the adapter.

    Raises:
      ParameterError: An issue with the module parameters.
      Error: Other errors during processing.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    # Note: Defaults specified in argument_spec will be set in params dict
    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['cpc_name']
    adapter_name = params['name']
    adapter_match = params['match']
    faked_session = params.get('faked_session', None)  # No default specified

    changed = False

    try:
        session = get_session(faked_session, host, userid, password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        adapter = identify_adapter(cpc, adapter_name, adapter_match)
        # The default exception handling is sufficient for the above.

        adapter.pull_full_properties()
        result = adapter.properties

        # It was identified by name or match properties, so it does exist.
        # Update its properties and change adapter and crypto type, if
        # needed.
        create_props, update_props, chg_adapter_type, chg_crypto_type = \
            process_properties(adapter, params)

        if update_props:
            if not check_mode:
                adapter.update_properties(update_props)
            else:
                result.update(update_props)  # from input values
            changed = True

        if chg_adapter_type:
            if not check_mode:
                adapter.change_adapter_type(chg_adapter_type)
            else:
                result['type'] = chg_adapter_type
            changed = True

        if chg_crypto_type:
            if not check_mode:
                adapter.change_crypto_type(chg_crypto_type)
            else:
                result['crypto-type'] = chg_crypto_type
            changed = True

        if changed and not check_mode:
            adapter.pull_full_properties()
            result = adapter.properties  # from actual values

        ports = adapter.ports.list()
        result_ports = list()
        for port in ports:
            # TODO: Disabling the following line mitigates the recent issue
            #       with HTTP error 404,4 when retrieving port properties.
            # port.pull_full_properties()
            result_ports.append(port.properties)
        result['ports'] = result_ports

        return changed, result

    finally:
        session.logoff()


def ensure_present(params, check_mode):
    """
    Ensure that the specified Hipersockets adapter exists and has the
    specified properties set.

    Raises:
      ParameterError: An issue with the module parameters.
      Error: Other errors during processing.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    # Note: Defaults specified in argument_spec will be set in params dict
    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['cpc_name']
    adapter_name = params['name']
    faked_session = params.get('faked_session', None)  # No default specified

    changed = False

    try:
        session = get_session(faked_session, host, userid, password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        try:
            adapter = cpc.adapters.find(name=adapter_name)
        except zhmcclient.NotFound:
            adapter = None

        if not adapter:
            # It does not exist. The only possible adapter type
            # that can be created is a Hipersockets adapter, but before
            # creating one we check the 'type' input property to verify that
            # the intention is really Hipersockets creation, and not just a
            # mispelled name.
            input_props = params.get('properties', None)
            if input_props is None:
                adapter_type = None
            else:
                adapter_type = input_props.get('type', None)
            if adapter_type is None:
                raise ParameterError(
                    "Input property 'type' missing when creating "
                    "Hipersockets adapter {!r} (must specify 'hipersockets')".
                    format(adapter_name))
            if adapter_type != 'hipersockets':
                raise ParameterError(
                    "Input property 'type' specifies {!r} when creating "
                    "Hipersockets adapter {!r} (must specify 'hipersockets').".
                    format(adapter_type, adapter_name))

            create_props, update_props, _, _ = \
                process_properties(adapter, params)

            # This is specific to Hipersockets: There are no update-only
            # properties, so any remaining such property is an input error
            invalid_update_props = {}
            for name in update_props:
                if name not in create_props:
                    invalid_update_props[name] = update_props[name]
            if invalid_update_props:
                raise ParameterError(
                    "Invalid input properties specified when creating "
                    "Hipersockets adapter {!r}: {!r}".
                    format(adapter_name, invalid_update_props))

            # While the 'type' input property is required for verifying
            # the intention, it is not allowed as input for the
            # Create Hipersocket HMC operation.
            del create_props['type']

            if not check_mode:
                adapter = cpc.adapters.create_hipersocket(create_props)
                adapter.pull_full_properties()
                result = adapter.properties  # from actual values
            else:
                adapter = None
                result = dict()
                result.update(create_props)  # from input values
            changed = True
        else:
            # It does exist.
            # Update its properties and change adapter and crypto type, if
            # needed.

            adapter.pull_full_properties()
            result = adapter.properties

            create_props, update_props, chg_adapter_type, chg_crypto_type = \
                process_properties(adapter, params)

            if update_props:
                if not check_mode:
                    adapter.update_properties(update_props)
                else:
                    result.update(update_props)  # from input values
                changed = True

            if chg_adapter_type:
                if not check_mode:
                    adapter.change_adapter_type(chg_adapter_type)
                else:
                    result['type'] = chg_adapter_type
                changed = True

            if chg_crypto_type:
                if not check_mode:
                    adapter.change_crypto_type(chg_crypto_type)
                else:
                    result['crypto-type'] = chg_crypto_type
                changed = True

            if changed and not check_mode:
                adapter.pull_full_properties()
                result = adapter.properties  # from actual values

        if adapter:
            ports = adapter.ports.list()
            result_ports = list()
            for port in ports:
                port.pull_full_properties()
                result_ports.append(port.properties)
            result['ports'] = result_ports
        else:
            # For now, we return no ports when creating in check mode
            result['ports'] = dict()

        return changed, result

    finally:
        session.logoff()


def ensure_absent(params, check_mode):
    """
    Ensure that the specified Hipersockets adapter does not exist.

    Raises:
      ParameterError: An issue with the module parameters.
      Error: Other errors during processing.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    # Note: Defaults specified in argument_spec will be set in params dict
    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['cpc_name']
    adapter_name = params['name']
    faked_session = params.get('faked_session', None)  # No default specified

    changed = False
    result = {}

    try:
        session = get_session(faked_session, host, userid, password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        try:
            adapter = cpc.adapters.find(name=adapter_name)
        except zhmcclient.NotFound:
            return changed, result

        if not check_mode:
            adapter.delete()
        changed = True

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
    cpc_name = params['cpc_name']
    adapter_name = params['name']
    faked_session = params.get('faked_session', None)  # No default specified

    try:
        session = get_session(faked_session, host, userid, password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        adapter = cpc.adapters.find(name=adapter_name)
        # The default exception handling is sufficient for the above.

        adapter.pull_full_properties()
        result = adapter.properties

        ports = adapter.ports.list()
        result_ports = list()
        for port in ports:
            port.pull_full_properties()
            result_ports.append(port.properties)
        result['ports'] = result_ports

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
        "present": ensure_present,
        "absent": ensure_absent,
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
        match=dict(required=False, type='dict', default={}),
        state=dict(required=True, type='str',
                   choices=['set', 'present', 'absent', 'facts']),
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
        "Module exit (success): changed: {!r}, adapter: {!r}".
        format(changed, result))
    module.exit_json(
        changed=changed, adapter=result)


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings()
    main()
