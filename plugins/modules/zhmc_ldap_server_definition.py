#!/usr/bin/python
# Copyright 2023 IBM Corp. All Rights Reserved.
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
module: zhmc_ldap_server_definition
version_added: "2.9.0"
short_description: Manage an LDAP Server Definition on the HMC
description:
  - Gather facts about an LDAP Server Definition on an HMC of a Z system.
  - Create, delete, or update an LDAP Server Definition on an HMC.
author:
  - Andreas Maier (@andy-maier)
requirements:
  - "The HMC userid must have these task permissions:
    'Manage LDAP Server Definitions'."
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
  name:
    description:
      - The name of the target LDAP Server Definition object.
      - The name is case-insensitive (but case-preserving).
    type: str
    required: true
  state:
    description:
      - "The desired state for the LDAP Server Definition. All states are fully
         idempotent within the limits of the properties that can be changed:"
      - "* C(absent): Ensures that the LDAP Server Definition does not exist."
      - "* C(present): Ensures that the LDAP Server Definition exists and has
         the specified properties."
      - "* C(facts): Returns the LDAP Server Definition properties."
    type: str
    required: true
    choices: ['absent', 'present', 'facts']
  properties:
    description:
      - "Dictionary with desired properties for the LDAP Server Definition.
         Used for C(state=present); ignored for C(state=absent|facts).
         Dictionary key is the property name with underscores instead
         of hyphens, and dictionary value is the property value in YAML syntax.
         Integer properties may also be provided as decimal strings."
      - "The possible input properties in this dictionary are the properties
         defined as writeable in the data model for LDAP Server Definition
         resources (where the property names contain underscores instead of
         hyphens), with the following exceptions:"
      - "* C(name): Cannot be specified because the name has already been
         specified in the C(name) module parameter."
      - "Properties omitted in this dictionary will remain unchanged when the
         LDAP Server Definition already exists, and will get the default value
         defined in the data model for LDAP Server Definitions in the
         :term:`HMC API` when the LDAP Server Definition is being created."
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

- name: Gather facts about an LDAP Server Definition
  zhmc_ldap_server_definition:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_lsd_name }}"
    state: facts
  register: lsd1

- name: Ensure the LDAP Server Definition does not exist
  zhmc_ldap_server_definition:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_lsd_name }}"
    state: absent

- name: Ensure the LDAP Server Definition exists
  zhmc_ldap_server_definition:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_lsd_name }}"
    state: present
    properties:
      description: "Example LDAP Server Definition 1"
      primary_hostname_ipaddr: "10.11.12.13"
      search_distinguished_name: "test_user{0}"
  register: lsd1
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
ldap_server_definition:
  description:
    - "For C(state=absent), an empty dictionary."
    - "For C(state=present|facts), a dictionary with the resource properties of
       the target LDAP Server Definition."
  returned: success
  type: dict
  contains:
    name:
      description: "LDAP Server Definition name"
      type: str
    "{property}":
      description: "Additional properties of the LDAP Server Definition, as
        described in the data model of the 'LDAP Server Definition' object in
        the :term:`HMC API` book.
        The property names have hyphens (-) as described in that book."
      type: raw
  sample:
    {
        "backup-hostname-ipaddr": null,
        "bind-distinguished-name": null,
        "class": "ldap-server-definition",
        "connection-port": null,
        "description": "zhmc test LSD 1",
        "element-id": "dcb6d966-465f-11ee-80ca-00106f234c71",
        "element-uri": "/api/console/ldap-server-definitions/dcb6d966-465f-11ee-80ca-00106f234c71",
        "location-method": "pattern",
        "name": "zhmc_test_lsd_1",
        "parent": "/api/console",
        "primary-hostname-ipaddr": "10.11.12.13",
        "replication-overwrite-possible": false,
        "search-distinguished-name": "test_user{0}",
        "search-filter": null,
        "search-scope": null,
        "tolerate-untrusted-certificates": null,
        "use-ssl": false
    }
"""

import uuid  # noqa: E402
import logging  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402

from ..module_utils.common import log_init, open_session, close_session, \
    hmc_auth_parameter, Error, ParameterError, to_unicode, \
    process_normal_property, missing_required_lib, \
    common_fail_on_import_errors, parse_hmc_host  # noqa: E402

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
LOGGER_NAME = 'zhmc_ldap_server_definition'

LOGGER = logging.getLogger(LOGGER_NAME)


def casefold(txt):
    """Type cast function to casefolded text"""
    try:
        return txt.casefold()
    except AttributeError:
        return txt.lower()


# Dictionary of properties of LDAP Server Definition resources, in this format:
#   name: (allowed, create, update, eq_func, type_cast)
# where:
#   name: Name of the property according to the data model, with hyphens
#     replaced by underscores (this is how it is or would be specified in
#     the 'properties' module parameter).
#   allowed: Indicates whether it is allowed in the 'properties' module
#     parameter.
#   create: Indicates whether it can be specified for the "Create LDAP Server
#     Definition" operation.
#   update: Indicates whether it can be specified for the "Modify LDAP Server
#     Definition Properties" operation (at all).
#   update_while_active: No meaning in this module, always set to True.
#   eq_func: Equality test function for two values of the property; None means
#     to use Python equality.
#   type_cast: Type cast function for an input value of the property; None
#     means to use it directly. This can be used for example to convert
#     integers provided as strings by Ansible back into integers (that is a
#     current deficiency of Ansible).
ZHMC_LSD_PROPERTIES = {

    # create-only properties:
    'name': (False, True, False, None, casefold, None),
    # name: provided in 'name' module parm

    # update-only properties:
    'replication_overwrite_possible': (True, False, True, True, None, bool),

    # create+update properties:
    'description': (True, True, True, True, None, to_unicode),
    'primary_hostname_ipaddr': (True, True, True, True, None, to_unicode),
    # primary_hostname_ipaddr is required for create
    'connection_port': (True, True, True, True, None, int),
    'backup_hostname_ipaddr': (True, True, True, True, None, to_unicode),
    'use_ssl': (True, True, True, True, None, bool),
    'tolerate_untrusted_certificates': (True, True, True, True, None, bool),
    'bind_distinguished_name': (True, True, True, True, None, to_unicode),
    'bind_password': (True, True, True, True, None, to_unicode),
    # bind_password is not returned on facts
    'location_method': (True, True, True, True, None, to_unicode),
    'search_distinguished_name': (True, True, True, True, None, to_unicode),
    # search_distinguished_name is required for create
    'search_scope': (True, True, True, True, None, to_unicode),
    'search_filter': (True, True, True, True, None, to_unicode),
    # search_filter is required for create if location_method=="subtree"

    # read-only properties:
    'element_uri': (False, False, False, None, None, None),
    'element_id': (False, False, False, None, None, None),
    'parent': (False, False, False, None, None, None),
    'class': (False, False, False, None, None, None),
}


def process_properties(lsd, params):
    """
    Process the properties specified in the 'properties' module parameter,
    and return two dictionaries (create_props, update_props) that contain
    the properties that can be created, and the properties that can be updated,
    respectively. If the resource exists, the input property values are
    compared with the existing resource property values and the returned set
    of properties is the minimal set of properties that need to be changed.

    - Underscores in the property names are translated into hyphens.
    - The presence of read-only properties, invalid properties (i.e. not
      defined in the data model for LDAP Server Definitions), and properties
      that are not allowed because of restrictions is surfaced by raising
      ParameterError.

    Parameters:

      lsd (zhmcclient.LDAPServerDefinition): LDAP Server Definition object to
        be updated with the full set of current properties, or `None` if it did
        not previously exist.

      params (dict): Module input parameters.

    Returns:
      tuple of (create_props, update_props),
      where:
        * create_props: dict of properties for
          zhmcclient.UserManager.create()
        * update_props: dict of properties for
          zhmcclient.LDAPServerDefinition.update_properties()

    Raises:
      ParameterError: An issue with the module parameters.
    """
    create_props = {}
    update_props = {}

    # handle 'name' property
    lsd_name = to_unicode(params['name'])
    if lsd is None:
        # LDAP Server Definition object does not exist yet.
        create_props['name'] = lsd_name
    else:
        # LDAP Server Definition object does already exist.
        # We looked up the LDAP Server Definition by name, so we will never
        # have to update its name.
        pass

    # handle the other properties
    input_props = params.get('properties', None)
    if input_props is None:
        input_props = {}

    for prop_name in input_props:

        if prop_name not in ZHMC_LSD_PROPERTIES:
            raise ParameterError(
                f"Property {prop_name!r} is not defined in the data model for "
                "LDAP Server Definitions.")

        # pylint: disable=unused-variable
        allowed, create, update, update_while_active, eq_func, type_cast = \
            ZHMC_LSD_PROPERTIES[prop_name]

        if not allowed:
            raise ParameterError(
                f"Property {prop_name!r} is not allowed in the 'properties' "
                "module parameter.")

        # Process a normal (= non-artificial) property
        _create_props, _update_props, _stop = process_normal_property(
            prop_name, ZHMC_LSD_PROPERTIES, input_props, lsd)
        create_props.update(_create_props)
        update_props.update(_update_props)
        if _stop:
            raise AssertionError()
    return create_props, update_props


def create_check_mode_lsd(console, create_props, update_props):
    """
    Create and return a fake local LDAP Server Definition object.

    This is used when an LDAP Server Definition object needs to be created in
    check mode.

    This function must be consistent with the behavior of the "Create LDAP
    Server Definition" operation on the HMC. HTTP errors the HMC would return
    are indicated by raising zhmcclient.HTTPError.
    """

    input_props = {}
    input_props.update(create_props)
    input_props.update(update_props)

    # Check required input properties
    missing_props = []
    for pname in ('name', 'search-distinguished-name',
                  'primary-hostname-ipaddr'):
        if pname not in input_props:
            missing_props.append(pname)
    location_method = input_props.get('location-method', 'pattern')
    if location_method == 'subtree':
        if 'search-filter' not in input_props:
            missing_props.append('search-filter')
    if missing_props:
        raise zhmcclient.HTTPError({
            'http-status': 400,
            'reason': 4,
            'message': "Required input properties missing for Create LDAP "
            f"Server Definition: {missing_props}",
        })

    # Defaults for optional properties that are the same in all cases
    props = {
        'description': '',
        # primary-hostname-ipaddr is required
        'connection-port': None,
        'backup-hostname-ipaddr': None,
        'use-ssl': False,
        'tolerate-untrusted-certificates': None,
        'bind-distinguished-name': None,
        'bind-password': None,
        'location-method': 'pattern',
        # search-distinguished-name is required
        'search-scope': None,
        'search-filter': None,
        'replication-overwrite-possible': False,
    }

    # Apply specified input properties on top of the defaults
    props.update(input_props)

    lsd_oid = f'fake-{uuid.uuid4()}'
    lsd = console.ldap_server_definitions.resource_object(lsd_oid, props=props)

    return lsd


def ensure_present(params, check_mode):
    """
    Ensure that the LDAP Server Definition object exists and has the specified
    properties.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    lsd_name = params['name']

    changed = False
    result = {}

    session, logoff = open_session(params)
    try:
        client = zhmcclient.Client(session)
        console = client.consoles.console
        # The default exception handling is sufficient for the above.

        try:
            lsd = console.ldap_server_definitions.find(name=lsd_name)
        except zhmcclient.NotFound:
            lsd = None

        if lsd is None:
            # It does not exist. Create it and update it if there are
            # update-only properties.
            create_props, update_props = process_properties(lsd, params)
            update2_props = {}
            for name, value in update_props.items():
                if name not in create_props:
                    update2_props[name] = value
            if not check_mode:
                lsd = console.ldap_server_definitions.create(create_props)
                if update2_props:
                    lsd.update_properties(update2_props)
                # We refresh the properties after the update, in case an
                # input property value gets changed.
                lsd.pull_full_properties()
            else:
                # Create a LDAP Server Definition object locally
                lsd = create_check_mode_lsd(
                    console, create_props, update2_props)
            result = dict(lsd.properties)
            changed = True
        else:
            # It exists. Update its properties.
            lsd.pull_full_properties()
            result = dict(lsd.properties)
            create_props, update_props = process_properties(lsd, params)
            if create_props:
                raise AssertionError("Unexpected "
                                     "create_props: %r" % create_props)
            if update_props:
                LOGGER.debug(
                    "Existing LDAP Server Definition %r needs to get "
                    "properties updated: %r", lsd_name, update_props)
                if not check_mode:
                    lsd.update_properties(update_props)
                    # We refresh the properties after the update, in case an
                    # input property value gets changed.
                    lsd.pull_full_properties()
                    result = dict(lsd.properties)
                else:
                    # Update the local LDAP Server Definition object's
                    # properties
                    result.update(update_props)
                changed = True

        if not lsd:
            raise AssertionError()

        return changed, result

    finally:
        close_session(session, logoff)


def ensure_absent(params, check_mode):
    """
    Ensure that the LDAP Server Definition object does not exist.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    lsd_name = params['name']

    changed = False
    result = {}

    session, logoff = open_session(params)
    try:
        client = zhmcclient.Client(session)
        console = client.consoles.console
        # The default exception handling is sufficient for the above.

        try:
            lsd = console.ldap_server_definitions.find(name=lsd_name)
        except zhmcclient.NotFound:
            return changed, result

        if not check_mode:
            lsd.delete()
        changed = True

        return changed, result

    finally:
        close_session(session, logoff)


def facts(params, check_mode):
    # pylint: disable=unused-argument
    """
    Return facts about an LDAP Server Definition object.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    lsd_name = params['name']

    changed = False
    result = {}

    session, logoff = open_session(params)
    try:
        # The default exception handling is sufficient for this code
        client = zhmcclient.Client(session)
        console = client.consoles.console

        lsd = console.ldap_server_definitions.find(name=lsd_name)
        lsd.pull_full_properties()

        result = dict(lsd.properties)

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

    _params = dict(module.params)
    del _params['hmc_auth']
    LOGGER.debug("Module entry: params: %r", _params)

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
        "Module exit (success): changed: %r, ldap_server_definition: %r",
        changed, result)
    module.exit_json(changed=changed, ldap_server_definition=result)


if __name__ == '__main__':
    main()
