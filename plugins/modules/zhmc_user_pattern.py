#!/usr/bin/python
# Copyright 2024 IBM Corp. All Rights Reserved.
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
module: zhmc_user_pattern
version_added: "2.15.0"
short_description: Manage an HMC user pattern
description:
  - Gather facts about a user pattern on an HMC of a Z system.
  - Create, delete, or update a user pattern on an HMC.
author:
  - Andreas Maier (@andy-maier)
requirements:
  - "The HMC userid must have these task permissions:
    'Manage User Patterns'."
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
  name:
    description:
      - The name of the target user pattern.
    type: str
    required: true
  state:
    description:
      - "The desired state for the HMC user pattern. All states are fully
         idempotent within the limits of the properties that can be changed:"
      - "* V(absent): Ensures that the user pattern does not exist."
      - "* V(present): Ensures that the user pattern exists and has the
         specified properties."
      - "* V(facts): Returns the user pattern properties."
    type: str
    required: true
    choices: ['absent', 'present', 'facts']
  properties:
    description:
      - "Dictionary with desired properties for the user pattern.
         Used for O(state=present); ignored for O(state=absent|facts).
         Dictionary key is the property name with underscores instead
         of hyphens, and dictionary value is the property value in YAML syntax.
         Integer properties may also be provided as decimal strings."
      - "The possible input properties in this dictionary are the properties
         defined as writeable in the data model for User Pattern resources
         (where the property names contain underscores instead of hyphens),
         with the following exceptions:"
      - "* C(name): Cannot be specified because the name has already been
         specified in the O(name) module parameter."
      - "* C(..._uri): Cannot be set directly, but indirectly via the
         corresponding artificial property C(..._name). An empty string for
         the name will set the URI to null."
      - "Properties omitted in this dictionary will remain unchanged when the
         user pattern already exists, and will get the default value defined
         in the data model for user patterns in the R(HMC API,HMC API) book
         when the user pattern is being created."
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

- name: Gather facts about a user pattern
  zhmc_user_pattern:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_user_pattern_name }}"
    state: facts
  register: userpattern1

- name: Ensure the user pattern does not exist
  zhmc_user_pattern:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_user_pattern_name }}"
    state: absent

- name: Ensure the user pattern exists and has certain properties
  zhmc_user_pattern:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_user_pattern_name }}"
    state: present
    properties:
      description: "Example user pattern 1"
  register: userpattern1
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
user_pattern:
  description:
    - "For O(state=absent), an empty dictionary."
    - "For O(state=present|facts), a dictionary with the resource properties of
      the target user pattern and some additional artificial properties."
  returned: success
  type: dict
  contains:
    name:
      description: "User Pattern name"
      type: str
    "{property}":
      description:
        - "Additional properties of the user pattern, as described in the
          data model of the 'User Pattern' object in the R(HMC API,HMC API) book.
          The property names will have underscores instead of hyphens."
        - "The items in the C(ldap_group_to_template_mappings) property have
          an additional item C(template-name) which is the name of the
          resource object referenced by C(template-uri)."
      type: raw
    domain_name_restrictions_ldap_server_definition_name:
      description: "Name of the resource object referenced by the corresponding
        ..._uri property."
      type: str
    ldap_group_default_template_name:
      description: "Name of the resource object referenced by the corresponding
        ..._uri property."
      type: str
    ldap_group_ldap_server_definition_name:
      description: "Name of the resource object referenced by the corresponding
        ..._uri property."
      type: str
    ldap_server_definition_name:
      description: "Name of the resource object referenced by the corresponding
        ..._uri property."
      type: str
    specific_template_name:
      description: "Name of the resource object referenced by the corresponding
        ..._uri property."
      type: str
    template_name_override_default_template_name:
      description: "Name of the resource object referenced by the corresponding
        ..._uri property."
      type: str
    template_name_override_ldap_server_definition_name:
      description: "Name of the resource object referenced by the corresponding
        ..._uri property."
      type: str
    user_template_name:
      description: "Name of the resource object referenced by the corresponding
        ..._uri property."
      type: str
  sample:
    {
        "class": "user-pattern",
        "description": "A pattern that matches a bluepages email address.",
        "domain_name_restrictions": null,
        "domain_name_restrictions_ldap_server_definition_name": null,
        "domain_name_restrictions_ldap_server_definition_uri": null,
        "element_id": "cbcaf7a0-46cc-11e9-bfd3-f44a39cd42f9",
        "element_uri": "/api/console/user-patterns/cbcaf7a0-46cc-11e9-bfd3-f44a39cd42f9",
        "ldap_group_default_template_name": null,
        "ldap_group_default_template_uri": null,
        "ldap_group_ldap_server_definition_name": null,
        "ldap_group_ldap_server_definition_uri": null,
        "ldap_group_to_template_mappings": null,
        "ldap_server_definition_name": null,
        "ldap_server_definition_uri": null,
        "name": "Bluepages email address",
        "parent": "/api/console",
        "pattern": "*@*ibm.com",
        "replication_overwrite_possible": false,
        "retention_time": 90,
        "search_order_index": 0,
        "specific_template_name": "Product Engineering and Access Administrator",
        "specific_template_uri": "/api/users/97769500-4a81-11e9-aa1b-00106f23f636",
        "template_name_override": null,
        "template_name_override_default_template_name": null,
        "template_name_override_default_template_uri": null,
        "template_name_override_ldap_server_definition_name": null,
        "template_name_override_ldap_server_definition_uri": null,
        "type": "glob-like",
        "user_template_name": "Product Engineering and Access Administrator",
        "user_template_uri": "/api/users/97769500-4a81-11e9-aa1b-00106f23f636"
    }
"""

import uuid  # noqa: E402
import logging  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule, \
    missing_required_lib  # noqa: E402

from ..module_utils.common import log_init, open_session, close_session, \
    hmc_auth_parameter, Error, ParameterError, to_unicode, \
    process_normal_property, underscore_properties, \
    common_fail_on_import_errors, parse_hmc_host, blanked_params  # noqa: E402

try:
    import zhmcclient
    IMP_ZHMCCLIENT_ERR = None
except ImportError:
    IMP_ZHMCCLIENT_ERR = traceback.format_exc()

# Python logger name for this module
LOGGER_NAME = 'zhmc_user_pattern'

LOGGER = logging.getLogger(LOGGER_NAME)

# Dictionary of properties of user pattern resources, in this format:
#   name: (allowed, create, update, eq_func, type_cast)
# where:
#   name: Name of the property according to the data model, with hyphens
#     replaced by underscores (this is how it is or would be specified in
#     the 'properties' module parameter).
#   allowed: Indicates whether it is allowed in the 'properties' module
#     parameter.
#   create: Indicates whether it can be specified for the "Create User Pattern"
#    operation.
#   update: Indicates whether it can be specified for the "Modify User Pattern
#     Properties" operation (at all).
#   update_while_active: Not used for this module, always True.
#   eq_func: Equality test function for two values of the property; None means
#     to use Python equality.
#   type_cast: Type cast function for an input value of the property; None
#     means to use it directly. This can be used for example to convert
#     integers provided as strings by Ansible back into integers (that is a
#     current deficiency of Ansible).
ZHMC_USER_PATTERN_PROPERTIES = {

    # create+update properties:
    'name': (False, True, True, True, None, None),
    # name: provided in 'name' module parm
    'description': (True, True, True, True, None, to_unicode),
    'type': (True, True, True, True, None, None),
    'pattern': (True, True, True, True, None, to_unicode),
    'retention_time': (True, True, True, True, None, int),
    'user_template_uri': (False, False, True, True, None, None),
    'user_template_name': (True, True, True, True, None, None),
    # user_template_name: Artificial property, based on
    # user_template_uri
    'ldap_server_definition_uri': (False, False, True, True, None, None),
    'ldap_server_definition_name': (True, True, True, True, None, None),
    # ldap_server_definition_name: Artificial property, based on
    # ldap_server_definition_uri
    'template_name_override': (True, True, True, True, None, None),
    'domain_name_restrictions': (True, True, True, True, None, None),
    'specific_template_uri': (False, False, True, True, None, None),
    'specific_template_name': (True, True, True, True, None, None),
    # specific_template_name: Artificial property, based on
    # specific_template_uri
    'template_name_override_ldap_server_definition_uri':
        (False, False, True, True, None, None),
    'template_name_override_ldap_server_definition_name':
        (True, True, True, True, None, None),
    # template_name_override_ldap_server_definition_name: Artificial property,
    # based on template_name_override_ldap_server_definition_uri
    'template_name_override_default_template_uri':
        (False, False, True, True, None, None),
    'template_name_override_default_template_name':
        (True, True, True, True, None, None),
    # template_name_override_default_template_name: Artificial property,
    # based on template_name_override_default_template_uri
    'ldap_group_to_template_mappings':
        (True, True, True, True, None, list),
    # ldap_group_to_template_mappings is an array of group-to-template-mapping
    # objects:
    #   ldap_group_name: String
    #   template_uri: String
    #   template_name: String - Additional artificial property
    'ldap_group_ldap_server_definition_uri':
        (False, False, True, True, None, None),
    'ldap_group_ldap_server_definition_name':
        (True, True, True, True, None, None),
    # ldap_group_ldap_server_definition_name: Artificial property,
    # based on ldap_group_ldap_server_definition_uri
    'ldap_group_default_template_uri':
        (False, False, True, True, None, None),
    'ldap_group_default_template_name':
        (True, True, True, True, None, None),
    # ldap_group_default_template_name: Artificial property,
    # based on ldap_group_default_template_uri
    'domain_name_restrictions_ldap_server_definition_uri':
        (False, False, True, True, None, None),
    'domain_name_restrictions_ldap_server_definition_name':
        (True, True, True, True, None, None),
    # domain_name_restrictions_ldap_server_definition_name: Artificial property,
    # based on domain_name_restrictions_ldap_server_definition_uri

    # read-only properties:
    'element_uri': (False, False, False, None, None, None),
    'element_id': (False, False, False, None, None, None),
    'parent': (False, False, False, None, None, None),
    'class': (False, False, False, None, None, None),
    'search_order_index': (False, False, False, None, None, int),
    'replication_overwrite_possible': (False, False, False, None, None, bool),
}


def process_properties(console, upattern, params):
    """
    Process the properties specified in the 'properties' module parameter,
    and return two dictionaries (create_props, update_props) that contain
    the properties that can be created, and the properties that can be updated,
    respectively. If the resource exists, the input property values are
    compared with the existing resource property values and the returned set
    of properties is the minimal set of properties that need to be changed.

    - Underscores in the property names are translated into hyphens.
    - The presence of read-only properties, invalid properties (i.e. not
      defined in the data model for user patterns), and properties that are
      not allowed because of restrictions or because they are auto-created from
      an artificial property is surfaced by raising ParameterError.

    Parameters:

      upattern (zhmcclient.UserPattern): User Pattern object to be updated with
        the full set of current properties, or `None` if it did not previously
        exist.

      params (dict): Module input parameters.

    Returns:
      tuple of (create_props, update_props),
      where:
        * create_props: dict of properties for
          zhmcclient.UserPatternManager.create()
        * update_props: dict of properties for
          zhmcclient.UserPattern.update_properties()

    Raises:
      ParameterError: An issue with the module parameters.
    """

    def find_by_name(res_mgr, res_name, res_kind, specified):
        try:
            res = res_mgr.find_by_name(res_name)
        except zhmcclient.NotFound:
            raise ParameterError(
                f"{res_kind} {res_name!r} specified in {specified} does not "
                "exist.")
        return res.uri

    def set_uri_prop(res_mgr, res_name, uri_pname_hyphen, res_kind, specified):
        """
        Set a resource URI property in the create_props or update_props
        dict.
        """
        if res_name:
            res_uri = find_by_name(res_mgr, res_name, res_kind, specified)
        else:
            # An empty string for name should result in setting URI to null
            res_uri = None
        if upattern is None:
            if res_uri is not None:
                create_props[uri_pname_hyphen] = res_uri
        else:
            if upattern.prop(uri_pname_hyphen) != res_uri:
                update_props[uri_pname_hyphen] = res_uri

    create_props = {}
    update_props = {}

    # handle 'name' property
    upattern_name = to_unicode(params['name'])
    if upattern is None:
        # User Pattern does not exist yet.
        create_props['name'] = upattern_name
    else:
        # User Pattern does already exist.
        # We looked up the user pattern by name, so we will never have to
        # update the user pattern name.
        pass

    # handle the other properties
    input_props = params['properties']
    if input_props is None:
        input_props = {}

    for prop_name in input_props:

        if prop_name not in ZHMC_USER_PATTERN_PROPERTIES:
            raise ParameterError(
                f"Property {prop_name!r} is not defined in the data model for "
                "user patterns.")

        # pylint: disable=unused-variable
        allowed, create, update, update_while_active, eq_func, type_cast = \
            ZHMC_USER_PATTERN_PROPERTIES[prop_name]

        if not allowed:
            raise ParameterError(
                f"Property {prop_name!r} is not allowed in the 'properties' "
                "module parameter.")

        # Process artificial properties allowed in input parameters

        if prop_name == 'user_template_name':
            set_uri_prop(console.users,
                         input_props[prop_name],
                         'user-template-uri',
                         "User", f"property {prop_name!r}")
            continue

        if prop_name == 'ldap_server_definition_name':
            set_uri_prop(console.ldap_server_definitions,
                         input_props[prop_name],
                         'ldap-server-definition-uri',
                         "LDAP Server Definition", f"property {prop_name!r}")
            continue

        if prop_name == 'specific_template_name':
            set_uri_prop(console.users,
                         input_props[prop_name],
                         'specific-template-uri',
                         "User", f"property {prop_name!r}")
            continue

        if prop_name == 'template_name_override_ldap_server_definition_name':
            set_uri_prop(console.ldap_server_definitions,
                         input_props[prop_name],
                         'template-name-override-ldap-server-definition-uri',
                         "LDAP Server Definition", f"property {prop_name!r}")
            continue

        if prop_name == 'template_name_override_default_template_name':
            set_uri_prop(console.users,
                         input_props[prop_name],
                         'template-name-override-default-template-uri',
                         "User", f"property {prop_name!r}")
            continue

        if prop_name == 'ldap_group_ldap_server_definition_name':
            set_uri_prop(console.ldap_server_definitions,
                         input_props[prop_name],
                         'ldap-group-ldap-server-definition-uri',
                         "LDAP Server Definition", f"property {prop_name!r}")
            continue

        if prop_name == 'ldap_group_default_template_name':
            set_uri_prop(console.users,
                         input_props[prop_name],
                         'ldap-group-default-template-uri',
                         "User", f"property {prop_name!r}")
            continue

        if prop_name == 'domain_name_restrictions_ldap_server_definition_name':
            set_uri_prop(console.ldap_server_definitions,
                         input_props[prop_name],
                         'domain-name-restrictions-ldap-server-definition-uri',
                         "LDAP Server Definition", f"property {prop_name!r}")
            continue

        if prop_name == 'ldap_group_to_template_mappings':
            # Process normal and artificial properties
            input_mappings = input_props['ldap_group_to_template_mappings']
            mappings = []  # used for the HMC operation
            if input_mappings is not None:
                for item in input_mappings:
                    mapping_item = {}
                    for pname, pvalue in item.items():
                        pname_hyphen = pname.replace('_', '-')
                        if pname == 'template_uri':
                            raise ParameterError(
                                "Property 'template_uri' in an item of "
                                "'ldap_group_to_template_mappings' is not "
                                "allowed in the 'properties' module parameter.")
                        if pname == 'template_name':
                            mapping_item['template-uri'] = find_by_name(
                                console.users, pvalue, "User",
                                "property 'template_uri' in an item of "
                                "'ldap_group_to_template_mappings'")
                        else:
                            mapping_item[pname_hyphen] = pvalue
                    mappings.append(mapping_item)
            if not mappings:
                mappings = None
            if upattern is None:
                create_props['ldap-group-to-template-mappings'] = mappings
            else:
                update_props['ldap-group-to-template-mappings'] = mappings

        # Process a normal (= non-artificial) property
        _create_props, _update_props, _stop = process_normal_property(
            prop_name, ZHMC_USER_PATTERN_PROPERTIES, input_props, upattern)
        create_props.update(_create_props)
        update_props.update(_update_props)
        if _stop:
            raise AssertionError(
                f"Input property {prop_name!r} unexpectedly defined with stop")
    return create_props, update_props


def add_artificial_properties(upattern_props, upattern):
    """
    Add artificial properties to the user pattern result properties.

    Upon return, the upattern_props dict has been extended by these
    properties:

    * The following properties with the name of corresponding '...-uri' object:
      - 'user-template-name'
      - 'ldap-server-definition-name'
      - 'specific-template-name'
      - 'template-name-override-ldap-server-definition-name'
      - 'template-name-override-default-template-name'
      - 'ldap-group-ldap-server-definition-name'
      - 'ldap-group-default-template-name'
      - 'domain-name-restrictions-ldap-server-definition-name'

    * In each item of the 'ldap-group-to-template-mappings' list:
      - 'template-name' with the name of corresponding '...-uri' object
    """
    console = upattern.manager.parent

    def set_name(set_dict, name_prop_name, mgr, uri_prop_name):
        """Set the name property in set_dict by looking up the resource URI."""
        try:
            uri = upattern.get_property(uri_prop_name)
        except KeyError:
            # If the property does not exist (e.g. in a mocked environment),
            # we also don't set the name property.
            return
        if uri is not None:
            # pylint: disable=protected-access
            filter_args = {mgr._uri_prop: uri}
            res = mgr.find(**filter_args)
            res_name = res.name
        else:
            res_name = None

        set_dict[name_prop_name] = res_name

    set_name(upattern_props,
             'user_template_name',
             console.users,
             'user-template-uri')

    set_name(upattern_props,
             'ldap_server_definition_name',
             console.ldap_server_definitions,
             'ldap-server-definition-uri')

    set_name(upattern_props,
             'specific_template_name',
             console.users,
             'specific-template-uri')

    set_name(upattern_props,
             'template_name_override_ldap_server_definition_name',
             console.ldap_server_definitions,
             'template-name-override-ldap-server-definition-uri')

    set_name(upattern_props,
             'template_name_override_default_template_name',
             console.users,
             'template-name-override-default-template-uri')

    set_name(upattern_props,
             'ldap_group_ldap_server_definition_name',
             console.ldap_server_definitions,
             'ldap-group-ldap-server-definition-uri')

    set_name(upattern_props,
             'ldap_group_default_template_name',
             console.users,
             'ldap-group-default-template-uri')

    set_name(upattern_props,
             'domain_name_restrictions_ldap_server_definition_name',
             console.ldap_server_definitions,
             'domain-name-restrictions-ldap-server-definition-uri')

    mappings = upattern_props.get('ldap-group-to-template-mappings')
    if mappings is not None:
        for item in mappings:
            set_name(item, 'template-name', console.users, 'template-uri')


def create_check_mode_upattern(console, create_props, update_props):
    """
    Create and return a fake local User Pattern object.

    This is used when a user pattern needs to be created in check mode.

    This function must be consistent with the behavior of the "Create Password
    Rule" operation on the HMC. HTTP errors the HMC would return are indicated
    by raising zhmcclient.HTTPError.
    """

    input_props = {}
    input_props.update(create_props)
    input_props.update(update_props)

    # Check required input properties
    missing_props = []
    for pname in ('name',):
        if pname not in input_props:
            missing_props.append(pname)
    if missing_props:
        raise zhmcclient.HTTPError({
            'http-status': 400,
            'reason': 4,
            'message': "Required input properties missing for Create "
            f"User Pattern: {missing_props}",
        })

    # Defaults for optional properties
    props = {
        # createable/updateable
        'description': '',
        'domain-name-restrictions': None,
        'domain-name-restrictions-ldap-server-definition-uri': None,
        'ldap-group-default-template-uri': None,
        'ldap-group-ldap-server-definition-uri': None,
        'ldap-group-to-template-mappings': None,
        'ldap-server-definition-uri': None,
        'specific-template-uri': None,
        'template-name-override': None,
        'template-name-override-default-template-uri': None,
        'template-name-override-ldap-server-definition-uri': None,
        'user-template-uri': None,
        # read-only
        'replication-overwrite-possible': False,
        'search-order-index': 0,
    }

    # Apply specified input properties on top of the defaults
    props.update(input_props)

    upattern_oid = f'fake-{uuid.uuid4()}'
    upattern = console.user_patterns.resource_object(upattern_oid, props=props)

    return upattern


def ensure_present(params, check_mode):
    """
    Ensure that the user pattern exists and has the specified properties.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    upattern_name = params['name']

    changed = False
    result = {}

    session, logoff = open_session(params)
    try:
        client = zhmcclient.Client(session)
        console = client.consoles.console
        # The default exception handling is sufficient for the above.

        try:
            upattern = console.user_patterns.find(name=upattern_name)
        except zhmcclient.NotFound:
            upattern = None

        if upattern is None:
            # It does not exist. Create it and update it if there are
            # update-only properties.
            create_props, update_props = \
                process_properties(console, upattern, params)
            update2_props = {}
            for name, value in update_props.items():
                if name not in create_props:
                    update2_props[name] = value
            if not check_mode:
                upattern = console.user_patterns.create(create_props)
                if update2_props:
                    upattern.update_properties(update2_props)
                # We refresh the properties after the update, in case an
                # input property value gets changed.
                upattern.pull_full_properties()
            else:
                # Create a User Pattern object locally
                upattern = create_check_mode_upattern(
                    console, create_props, update2_props)
            result = underscore_properties(upattern.properties)
            changed = True
        else:
            # It exists. Update its properties.
            upattern.pull_full_properties()
            result = underscore_properties(upattern.properties)
            create_props, update_props = \
                process_properties(console, upattern, params)
            if create_props:
                raise AssertionError("Unexpected "
                                     "create_props: %r" % create_props)
            if update_props:
                LOGGER.debug(
                    "Existing user pattern %r needs to get properties "
                    "updated: %r", upattern_name, update_props)
                if not check_mode:
                    upattern.update_properties(update_props)
                    # We refresh the properties after the update, in case an
                    # input property value gets changed.
                    upattern.pull_full_properties()
                    result = underscore_properties(upattern.properties)
                else:
                    # Update the local User Pattern object's properties
                    result.update(update_props)
                changed = True

        if not upattern:
            raise AssertionError()

        add_artificial_properties(result, upattern)

        return changed, result

    finally:
        close_session(session, logoff)


def ensure_absent(params, check_mode):
    """
    Ensure that the user pattern does not exist.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    upattern_name = params['name']

    changed = False
    result = {}

    session, logoff = open_session(params)
    try:
        client = zhmcclient.Client(session)
        console = client.consoles.console
        # The default exception handling is sufficient for the above.

        try:
            upattern = console.user_patterns.find(name=upattern_name)
        except zhmcclient.NotFound:
            return changed, result

        if not check_mode:
            upattern.delete()
        changed = True

        return changed, result

    finally:
        close_session(session, logoff)


def facts(params, check_mode):
    # pylint: disable=unused-argument
    """
    Return facts about a user pattern.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    upattern_name = params['name']

    changed = False
    result = {}

    session, logoff = open_session(params)
    try:
        # The default exception handling is sufficient for this code
        client = zhmcclient.Client(session)
        console = client.consoles.console

        upattern = console.user_patterns.find(name=upattern_name)
        upattern.pull_full_properties()

        result = underscore_properties(upattern.properties)
        add_artificial_properties(result, upattern)

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
        "Module exit (success): changed: %r, user_pattern: %r",
        changed, result)
    module.exit_json(changed=changed, user_pattern=result)


if __name__ == '__main__':
    main()
