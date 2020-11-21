#!/usr/bin/python
# Copyright 2019-2020 IBM Corp. All Rights Reserved.
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
module: zhmc_user
version_added: "2.9.0"
short_description: Create HMC users
description:
  - Gather facts about a user on an HMC of a Z system.
  - Create, delete, or update a user on an HMC.
author:
  - Andreas Maier (@andy-maier)
requirements:
  - Access to the WS API of the HMC of the targeted Z system
    (see :term:`HMC API`). The targeted Z system can be in any operational
    mode (classic, DPM)
options:
  hmc_host:
    description:
      - The hostname or IP address of the HMC.
    type: str
    required: true
  hmc_auth:
    description:
      - The authentication credentials for the HMC, as a dictionary of
        C(userid), C(password).
    type: dict
    required: true
    suboptions:
      userid:
        description:
          - The userid (username) for authenticating with the HMC.
        type: str
        required: true
      password:
        description:
          - The password for authenticating with the HMC.
        type: str
        required: true
  name:
    description:
      - The userid of the target user (i.e. the 'name' property of the User
        object).
    type: str
    required: true
  state:
    description:
      - "The desired state for the target user:"
      - "* C(absent): Ensures that the user does not exist."
      - "* C(present): Ensures that the user exists and has the specified
         properties."
      - "* C(facts): Does not change anything on the user and returns
         the user properties."
    type: str
    required: true
    choices: ['absent', 'present', 'facts']
  properties:
    description:
      - "Dictionary with desired properties for the user.
         Used for C(state=present); ignored for C(state=absent|facts).
         Dictionary key is the property name with underscores instead
         of hyphens, and dictionary value is the property value in YAML syntax.
         Integer properties may also be provided as decimal strings."
      - "The possible input properties in this dictionary are the properties
         defined as writeable in the data model for User resources
         (where the property names contain underscores instead of hyphens),
         with the following exceptions:"
      - "* C(name): Cannot be specified because the name has already been
         specified in the C(name) module parameter."
      - "* C(type): Cannot be changed once the user exists."
      - "* C(user-pattern-uri): Cannot be set directly, but indirectly via
         the artificial property C(user-pattern-name)."
      - "* C(password-rule-uri): Cannot be set directly, but indirectly via
         the artificial property C(password-rule-name)."
      - "* C(ldap-server-definition-uri): Cannot be set directly, but
         indirectly via the artificial property
         C(ldap-server-definition-name)."
      - "* C(default-group-uri): Cannot be set directly, but indirectly via
         the artificial property C(default-group-name)."
      - "Properties omitted in this dictionary will remain unchanged when the
         user already exists, and will get the default value defined
         in the data model for users in the :term:`HMC API` when the
         user is being created."
    type: dict
    required: false
    default: null
  expand:
    description:
      - "Boolean that controls whether the returned user contains
         additional artificial properties that expand certain URI or name
         properties to the full set of resource properties (see description of
         return values of this module)."
    type: bool
    required: false
    default: false
  log_file:
    description:
      - "File path of a log file to which the logic flow of this module as well
         as interactions with the HMC are logged. If null, logging will be
         propagated to the Python root logger."
    type: str
    required: false
    default: null
  faked_session:
    description:
      - "A C(zhmcclient_mock.FakedSession) object that has a mocked HMC set up.
         If not null, this session will be used instead of connecting to the
         HMC specified in C(hmc_host). This is used for testing purposes only."
    required: false
    type: raw
    default: null
"""

EXAMPLES = """
---
# Note: The following examples assume that some variables named 'my_*' are set.

- name: Gather facts about a user
  zhmc_user:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_user_name }}"
    state: facts
    expand: true
  register: user1

- name: Ensure the user does not exist
  zhmc_user:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_user_name }}"
    state: absent

- name: Ensure the user exists
  zhmc_user:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_user_name }}"
    state: present
    expand: true
    properties:
      description: "Example user 1"
      type: standard
  register: user1

"""

RETURN = """
user:
  description:
    - "For C(state=absent), an empty dictionary."
    - "For C(state=present|facts), a
       dictionary with the resource properties of the target user,
       plus additional artificial properties as described in the following
       list items."
  returned: success
  type: dict
  contains:
    name:
      description: "User name"
      type: str
    "{property}":
      description: "Additional properties of the user, as described
        in the :term:`HMC API` (using hyphens (-) in the property names)."
    user-pattern-name:
      description: "Name of the user pattern referenced by property
        C(user-pattern-uri)."
      type: str
    password-rule-name:
      description: "Name of the password rule referenced by property
        C(password-rule-uri)."
      type: str
    ldap-server-definition-name:
      description: "Name of the LDAP server definition referenced by property
        C(ldap-server-definition-uri)."
      type: str
    default-group-name:
      description: "Name of the group referenced by property
        C(default-group-uri)."
      type: str
"""

import uuid  # noqa: E402
import logging  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402

from ..module_utils.common import log_init, Error, ParameterError, \
    get_hmc_auth, get_session, to_unicode, process_normal_property, \
    missing_required_lib  # noqa: E402

try:
    import requests.packages.urllib3
    IMP_URLLIB3 = True
except ImportError:
    IMP_URLLIB3 = False
    IMP_URLLIB3_ERR = traceback.format_exc()

try:
    import zhmcclient
    IMP_ZHMCCLIENT = True
except ImportError:
    IMP_ZHMCCLIENT = False
    IMP_ZHMCCLIENT_ERR = traceback.format_exc()

# Python logger name for this module
LOGGER_NAME = 'zhmc_user'

LOGGER = logging.getLogger(LOGGER_NAME)

# Dictionary of properties of user resources, in this format:
#   name: (allowed, create, update, eq_func, type_cast)
# where:
#   name: Name of the property according to the data model, with hyphens
#     replaced by underscores (this is how it is or would be specified in
#     the 'properties' module parameter).
#   allowed: Indicates whether it is allowed in the 'properties' module
#     parameter.
#   create: Indicates whether it can be specified for the "Create User"
#    operation.
#   update: Indicates whether it can be specified for the "Modify User
#     Properties" operation (at all).
#   update_while_active: Indicates whether it can be specified for the "Modify
#     User Properties" operation while the user is attached
#     to any partition. None means "not applicable" (used for update=False).
#   eq_func: Equality test function for two values of the property; None means
#     to use Python equality.
#   type_cast: Type cast function for an input value of the property; None
#     means to use it directly. This can be used for example to convert
#     integers provided as strings by Ansible back into integers (that is a
#     current deficiency of Ansible).
ZHMC_USER_PROPERTIES = {

    # create-only properties:
    'type': (True, True, False, None, None, None),

    # update-only properties:
    'default_group_uri': (False, False, True, None, None, None),
    # default_group_uri: Modified via default_group_name.
    'default_group_name': (True, True, True, True, None, None),
    # default_group_name: Artificial property, based on default_group_uri

    # create+update properties:
    'name': (False, True, True, True, None, None),
    # name: provided in 'name' module parm
    'description': (True, True, True, True, None, to_unicode),
    'disabled': (True, True, True, True, None, bool),
    'authentication_type': (True, True, True, True, None, None),
    'password_rule_uri': (False, True, True, None, None, None),
    # password_rule_uri: Modified via password_rule_name.
    'password_rule_name': (True, True, True, True, None, None),
    # password_rule_name: Artificial property, based on password_rule_uri
    'password': (True, True, True, True, None, None),
    # password: Write-only
    'force_password_change': (True, True, True, True, None, bool),
    'ldap_server_definition_uri': (False, True, True, None, None, None),
    # ldap_server_definition_uri: Modified via ldap_server_definition_name.
    'ldap_server_definition_name': (True, True, True, True, None, None),
    # ldap_server_definition_name: Artificial property, based on
    # ldap_server_definition_uri
    'userid_on_ldap_server': (True, True, True, True, None, None),
    'session_timeout': (True, True, True, True, None, int),
    'verify_timeout': (True, True, True, True, None, int),
    'idle_timeout': (True, True, True, True, None, int),
    'min_pw_change_time': (True, True, True, True, None, int),
    'max_failed_logins': (True, True, True, True, None, int),
    'disable_delay': (True, True, True, True, None, int),
    'inactivity_timeout': (True, True, True, True, None, int),
    'disruptive_pw_required': (True, True, True, True, None, bool),
    'disruptive_text_required': (True, True, True, True, None, bool),
    'allow_remote_access': (True, True, True, True, None, bool),
    'allow_management_interfaces': (True, True, True, True, None, bool),
    'max_web_services_api_sessions': (True, True, True, True, None, int),
    'web_services_api_session_idle_timeout':
        (True, True, True, True, None, int),
    'multi_factor_authentication_required':
        (True, True, True, True, None, bool),
    'force_shared_secret_key_change': (True, True, True, True, None, bool),
    # TODO: The above property not in 'create user' in the 2.14.0 WS API book
    'email_address': (True, True, True, True, None, None),
    # TODO: The above property not in 'Create User' in the 2.14.0 WS API book

    # read-only properties:
    'object_uri': (False, False, False, None, None, None),
    'object_id': (False, False, False, None, None, None),
    'parent': (False, False, False, None, None, None),
    'class': (False, False, False, None, None, None),
    'user_pattern_uri': (False, False, False, None, None, None),
    'password_expires': (False, False, False, None, None, None),
    'user_roles': (False, False, False, None, None, None),
    'replication_overwrite_possible': (False, False, False, None, None, None),

    # read-only artificial if-expand properties:
    'user_pattern': (False, False, False, None, None, None),
    'default_group': (False, False, False, None, None, None),
    'password_rule': (False, False, False, None, None, None),
    'ldap_server_definition': (False, False, False, None, None, None),
    'user_role_objects': (False, False, False, None, None, None),
}


def process_properties(console, user, params):
    """
    Process the properties specified in the 'properties' module parameter,
    and return two dictionaries (create_props, update_props) that contain
    the properties that can be created, and the properties that can be updated,
    respectively. If the resource exists, the input property values are
    compared with the existing resource property values and the returned set
    of properties is the minimal set of properties that need to be changed.

    - Underscores in the property names are translated into hyphens.
    - The presence of read-only properties, invalid properties (i.e. not
      defined in the data model for users), and properties that are
      not allowed because of restrictions or because they are auto-created from
      an artificial property is surfaced by raising ParameterError.

    Parameters:

      user (zhmcclient.User): User object to be updated with the full set of
        current properties, or `None` if it did not previously exist.

      params (dict): Module input parameters.

    Returns:
      tuple of (create_props, update_props), where:
        * create_props: dict of properties for
          zhmcclient.UserManager.create()
        * update_props: dict of properties for
          zhmcclient.User.update_properties()

    Raises:
      ParameterError: An issue with the module parameters.
    """
    create_props = {}
    update_props = {}

    # handle 'name' property
    user_name = to_unicode(params['name'])
    if user is None:
        # User does not exist yet.
        create_props['name'] = user_name
    else:
        # User does already exist.
        # We looked up the user by name, so we will never have to
        # update the user name.
        pass

    # handle the other properties
    input_props = params.get('properties', None)
    if input_props is None:
        input_props = {}

    # Check required input properties
    for prop_name in ('type', 'authentication_type'):
        if prop_name not in input_props:
            raise ParameterError(
                "Property {0!r} is required but is missing in the module "
                "input parameters.".format(prop_name))
    auth_type = input_props['authentication_type']
    if auth_type == 'local':
        for prop_name in ('password_rule_name', 'password'):
            if prop_name not in input_props:
                raise ParameterError(
                    "Property {0!r} is required for "
                    "authentication_type='local' but is missing in the "
                    "module input parameters.".format(prop_name))
    if auth_type == 'ldap':
        for prop_name in ('ldap_server_definition_name', ):
            if prop_name not in input_props:
                raise ParameterError(
                    "Property {0!r} is required for "
                    "authentication_type='ldap' but is missing in the "
                    "module input parameters.".format(prop_name))

    for prop_name in input_props:

        if prop_name not in ZHMC_USER_PROPERTIES:
            raise ParameterError(
                "Property {0!r} is not defined in the data model for "
                "users.".format(prop_name))

        allowed, create, update, update_while_active, eq_func, type_cast = \
            ZHMC_USER_PROPERTIES[prop_name]

        if not allowed:
            raise ParameterError(
                "Property {0!r} is not allowed in the 'properties' module "
                "parameter.".format(prop_name))

        # Process artificial properties allowed in input parameters

        if prop_name == 'user_pattern_name':
            user_pattern_name = input_props[prop_name]
            if user_pattern_name:
                user_pattern = console.user_patterns.find_by_name(
                    user_pattern_name)
                user_pattern_uri = user_pattern.uri
            else:
                user_pattern_uri = None
            if user is None:
                create_props['user-pattern-uri'] = user_pattern_uri
            elif user.prop('user-pattern-uri') != user_pattern_uri:
                update_props['user-pattern-uri'] = user_pattern_uri
            continue

        if prop_name == 'password_rule_name':
            password_rule_name = input_props[prop_name]
            if password_rule_name:
                password_rule = console.password_rules.find_by_name(
                    password_rule_name)
                password_rule_uri = password_rule.uri
            else:
                password_rule_uri = None
            if user is None:
                create_props['password-rule-uri'] = password_rule_uri
            elif user.prop('password-rule-uri') != password_rule_uri:
                update_props['password-rule-uri'] = password_rule_uri
            continue

        if prop_name == 'ldap_server_definition_name':
            ldap_srv_def_name = input_props[prop_name]
            if ldap_srv_def_name:
                ldap_srv_def = console.ldap_server_definitions.find_by_name(
                    ldap_srv_def_name)
                ldap_srv_def_uri = ldap_srv_def.uri
            else:
                ldap_srv_def_uri = None
            if user is None:
                create_props['ldap-server-definition-uri'] = ldap_srv_def_uri
            elif user.prop('ldap-server-definition-uri') != ldap_srv_def_uri:
                update_props['ldap-server-definition-uri'] = ldap_srv_def_uri
            continue

        if prop_name == 'default_group_name':
            default_group_name = input_props[prop_name]
            # TODO: Add support for Group objects to zhmcclient
            # default_group = console.groups.find_by_name(default_group_name)
            default_group_uri = 'fake-uri-{0}'.format(default_group_name)
            if user is None:
                create_props['default-group-uri'] = default_group_uri
            elif user.prop('default-group-uri') != default_group_uri:
                update_props['default-group-uri'] = default_group_uri
            continue

        # Process a normal (= non-artificial) property
        _create_props, _update_props, _stop = process_normal_property(
            prop_name, ZHMC_USER_PROPERTIES, input_props, user)
        create_props.update(_create_props)
        update_props.update(_update_props)
        if _stop:
            raise AssertionError()
    return create_props, update_props


def add_artificial_properties(console, user, expand, check_mode):
    """
    Add artificial properties to the user object (class User).

    Upon return, the properties of the user object have been extended by these
    properties:

    Regardless of expand:

    * 'user-pattern-name': Name of UserPattern object corresponding to the URI
      in the 'user-pattern-uri' property. That property only exists for
      type='pattern-based'.

    * 'password-rule-name': Name of PasswordRule object corresponding to the
      URI in the 'password-rule-uri' property.

    * 'ldap-server-definition-name': Name of LdapServerDefinition object
      corresponding to the URI in the 'ldap-server-definition-uri' property.

    * 'default-group-name': Name of Group object corresponding to the URI in
      the 'default-group-uri' property.

      TODO: Implement default-group-name; requires support for Group objects in
      zhmcclient

    If expand is True:

    * 'user-pattern': UserPattern object corresponding to the URI in the
      'user-pattern-uri' property. That property only exists for
      type='pattern-based'.

    * 'password-rule': PasswordRule object corresponding to the URI in the
      'password-rule-uri' property.

    * 'ldap-server-definition': LdapServerDefinition object corresponding to
      the URI in the 'ldap-server-definition-uri' property.

    * 'user-role-objects': List of UserRole objects corresponding to the
      URIs in the 'user-roles' property.

    * 'default-group': Group object corresponding to the URI in the
      'default-group-uri' property.

      TODO: Implement default-group; requires support for Group objects in
      zhmcclient
    """

    # The User object either exists on the HMC, or in case of creating a user
    # in check mode it is a local User object that does not exist on the HMC.
    # In that case, we cannot retrieve properties from the HMC, so we take them
    # from the user object directly.
    type_ = user.properties['type']
    auth_type = user.properties['authentication-type']

    if type_ == 'pattern-based':
        # For that type, the property exists, but may be null.
        # Note: For other types, the property does not exist.
        user_pattern_uri = user.properties['user-pattern-uri']
        if user_pattern_uri is None:
            raise AssertionError()
        user_pattern = console.user_patterns.resource_object(user_pattern_uri)
        if check_mode:
            user.properties['user-pattern-name'] = user_pattern.oid
            if expand:
                user.properties['user-pattern'] = dict()
        else:
            user_pattern.pull_full_properties()
            user.properties['user-pattern-name'] = user_pattern.name
            if expand:
                user.properties['user-pattern'] = user_pattern.properties

    if auth_type == 'local':
        # For that auth type, the property exists and is non-null.
        # Note: For other auth types, the property does not exist.
        password_rule_uri = user.properties['password-rule-uri']
        if password_rule_uri is None:
            raise AssertionError()
        password_rule = console.password_rules.resource_object(
            password_rule_uri)
        if check_mode:
            user.properties['password-rule-name'] = \
                password_rule.uri.split('/')[-1]
            if expand:
                user.properties['password-rule'] = dict()
        else:
            password_rule.pull_full_properties()
            user.properties['password-rule-name'] = password_rule.name
            if expand:
                user.properties['password-rule'] = password_rule.properties

    if auth_type == 'ldap':
        # For that auth type, the property exists and is non-null.
        # Note: For other auth types, the property exists and is null.
        ldap_srv_def_uri = user.properties['ldap-server-definition-uri']
        if ldap_srv_def_uri is None:
            raise AssertionError()
        ldap_srv_def = console.ldap_srv_defs.resource_object(ldap_srv_def_uri)
        if check_mode:
            user.properties['ldap-server-definition-name'] = ldap_srv_def.oid
            if expand:
                user.properties['ldap-server-definition'] = dict()
        else:
            ldap_srv_def.pull_full_properties()
            user.properties['ldap-server-definition-name'] = ldap_srv_def.name
            if expand:
                user.properties['ldap-server-definition'] = \
                    ldap_srv_def.properties

    user_roles = list()
    user_role_uris = user.properties['user-roles']
    for user_role_uri in user_role_uris:
        user_role = console.user_roles.resource_object(user_role_uri)
        if not check_mode:
            user_role.pull_full_properties()
        user_roles.append(user_role)
    user.properties['user-role-names'] = [ur.name for ur in user_roles]
    if expand:
        user.properties['user-role-objects'] = \
            [ur.properties for ur in user_roles]


def create_check_mode_user(console, create_props, update_props):
    """
    Create and return a fake local User object.
    This is used when a user needs to be created in check mode.
    """
    type_ = create_props['type']
    props = dict()

    # Defaults for some read-only properties
    if type_ == 'pattern-based':
        props['user-pattern-uri'] = 'fake-uri-{0}'.format(uuid.uuid4())
    props['password-expires'] = -1
    props['user-roles'] = []
    props['replication-overwrite-possible'] = False

    props.update(create_props)
    props.update(update_props)

    user_oid = 'fake-{0}'.format(uuid.uuid4())
    user = console.users.resource_object(user_oid, props=props)

    return user


def ensure_present(params, check_mode):
    """
    Ensure that the user exists and has the specified properties.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    user_name = params['name']
    expand = params['expand']
    faked_session = params.get('faked_session', None)

    changed = False
    result = {}

    try:
        session = get_session(faked_session, host, userid, password)
        client = zhmcclient.Client(session)
        console = client.consoles.console
        # The default exception handling is sufficient for the above.

        try:
            user = console.users.find(name=user_name)
        except zhmcclient.NotFound:
            user = None

        if user is None:
            # It does not exist. Create it and update it if there are
            # update-only properties.
            create_props, update_props = process_properties(
                console, user, params)
            update2_props = {}
            for name in update_props:
                if name not in create_props:
                    update2_props[name] = update_props[name]
            if not check_mode:
                user = console.users.create(create_props)
                if update2_props:
                    user.update_properties(update2_props)
                # We refresh the properties after the update, in case an
                # input property value gets changed.
                user.pull_full_properties()
            else:
                # Create a User object locally
                user = create_check_mode_user(
                    console, create_props, update2_props)
            changed = True
        else:
            # It exists. Update its properties.
            user.pull_full_properties()
            create_props, update_props = process_properties(
                console, user, params)
            if create_props:
                raise AssertionError("Unexpected "
                                     "create_props: %r" % create_props)
            if update_props:
                LOGGER.debug(
                    "Existing user %r needs to get properties updated: %r",
                    user_name, update_props)
                if not check_mode:
                    user.update_properties(update_props)
                    # We refresh the properties after the update, in case an
                    # input property value gets changed.
                    user.pull_full_properties()
                else:
                    # Update the local User object's properties
                    user.properties.update(update_props)
                changed = True

        if not user:
            raise AssertionError()
        add_artificial_properties(console, user, expand, check_mode)
        result = user.properties

        return changed, result

    finally:
        session.logoff()


def ensure_absent(params, check_mode):
    """
    Ensure that the user does not exist.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    user_name = params['name']
    faked_session = params.get('faked_session', None)

    changed = False
    result = {}

    try:
        session = get_session(faked_session, host, userid, password)
        client = zhmcclient.Client(session)
        console = client.consoles.console
        # The default exception handling is sufficient for the above.

        try:
            user = console.users.find(name=user_name)
        except zhmcclient.NotFound:
            return changed, result

        if not check_mode:
            user.delete()
        changed = True

        return changed, result

    finally:
        session.logoff()


def facts(params, check_mode):
    """
    Return facts about a user.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    user_name = params['name']
    expand = params['expand']
    faked_session = params.get('faked_session', None)

    changed = False
    result = {}

    try:
        # The default exception handling is sufficient for this code

        session = get_session(faked_session, host, userid, password)
        client = zhmcclient.Client(session)
        console = client.consoles.console

        user = console.users.find(name=user_name)
        user.pull_full_properties()

        add_artificial_properties(console, user, expand, check_mode)
        result = user.properties

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
        name=dict(required=True, type='str'),
        state=dict(required=True, type='str',
                   choices=['absent', 'present', 'facts']),
        properties=dict(required=False, type='dict', default={}),
        expand=dict(required=False, type='bool', default=False),
        log_file=dict(required=False, type='str', default=None),
        faked_session=dict(required=False, type='raw'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True)

    if not IMP_URLLIB3:
        module.fail_json(msg=missing_required_lib("requests"),
                         exception=IMP_URLLIB3_ERR)

    requests.packages.urllib3.disable_warnings()

    if not IMP_ZHMCCLIENT:
        module.fail_json(msg=missing_required_lib("zhmcclient"),
                         exception=IMP_ZHMCCLIENT_ERR)

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
            "Module exit (failure): msg: %s", msg)
        module.fail_json(msg=msg)
    # Other exceptions are considered module errors and are handled by Ansible
    # by showing the traceback.

    LOGGER.debug(
        "Module exit (success): changed: %r, user: %r", changed, result)
    module.exit_json(changed=changed, user=result)


if __name__ == '__main__':
    main()
