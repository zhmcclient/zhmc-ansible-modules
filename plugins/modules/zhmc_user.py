#!/usr/bin/python
# Copyright 2019,2020 IBM Corp. All Rights Reserved.
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
short_description: Manage an HMC user
description:
  - Gather facts about a user on an HMC of a Z system.
  - Create, delete, or update a user on an HMC.
author:
  - Andreas Maier (@andy-maier)
requirements:
  - "The HMC userid must have these task permissions:
    'Manage Users' (for standard users), 'Manage User Templates' (for template
    users)."
  - "For updating its own HMC password, it is sufficient if the HMC userid has
    task permission for Manage Users or object-access permission for its own
    User object."
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
      - The userid of the target user (i.e. the 'name' property of the User
        object).
    type: str
    required: true
  state:
    description:
      - "The desired state for the HMC user. All states are fully idempotent
         within the limits of the properties that can be changed:"
      - "* V(absent): Ensures that the user does not exist."
      - "* V(present): Ensures that the user exists and has the specified
         properties."
      - "* V(facts): Returns the user properties."
    type: str
    required: true
    choices: ['absent', 'present', 'facts']
  properties:
    description:
      - "Dictionary with desired properties for the user.
         Used for O(state=present); ignored for O(state=absent|facts).
         Dictionary key is the property name with underscores instead
         of hyphens, and dictionary value is the property value in YAML syntax.
         Integer properties may also be provided as decimal strings."
      - "The possible input properties in this dictionary are the properties
         defined as writeable in the data model for User resources
         (where the property names contain underscores instead of hyphens),
         with the following exceptions:"
      - "* C(name): Cannot be specified because the name has already been
         specified in the O(name) module parameter."
      - "* C(type): Cannot be changed once the user exists."
      - "* C(user_roles): Cannot be set directly, but indirectly via
         the artificial property C(user_role_names) which replaces the
         current user roles, if specified."
      - "* C(user_pattern_uri): Cannot be set directly, but indirectly via
         the artificial property C(user_pattern_name)."
      - "* C(user_template_uri): Cannot be set directly, but indirectly via
         the artificial property C(user_template_name)."
      - "* C(password_rule_uri): Cannot be set directly, but indirectly via
         the artificial property C(password_rule_name)."
      - "* C(ldap_server_definition_uri): Cannot be set directly, but
         indirectly via the artificial property
         C(ldap_server_definition_name)."
      - "* C(primary_mfa_server_definition_uri): Cannot be set directly, but
         indirectly via the artificial property
         C(primary_mfa_server_definition_name)."
      - "* C(backup_mfa_server_definition_uri): Cannot be set directly, but
         indirectly via the artificial property
         C(backup_mfa_server_definition_name)."
      - "* C(default_group_uri): Cannot be set directly, but indirectly via
         the artificial property C(default_group_name)."
      - "Properties omitted in this dictionary will remain unchanged when the
         user already exists, and will get the default value defined
         in the data model for users in the R(HMC API,HMC API) book when the
         user is being created."
    type: dict
    required: false
    default: null
  expand:
    description:
      - "Deprecated: The O(expand) parameter is deprecated because the
         returned password rule, user role, user pattern and LDAP server
         definition objects have an independent lifecycle, so the same objects
         are returned when invoking this module in a loop through all users.
         Use the respective other modules of this collection to get the
         properties of these objects."
      - "Boolean that controls whether the returned user contains
         additional artificial properties that expand certain URI or name
         properties to the full set of resource properties (see description of
         return values of this module)."
    type: bool
    required: false
    default: false
  expand_names:
    description:
      - "Boolean that controls whether the returned user contains additional
         artificial properties for the names of referenced objects, such as
         user roles, password rule, etc."
      - "For backwards compatibility, this parameter defaults to True."
    type: bool
    required: false
    default: true
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

- name: Gather facts about a user
  zhmc_user:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_user_name }}"
    state: facts
  register: user1

- name: Ensure the user does not exist
  zhmc_user:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_user_name }}"
    state: absent

- name: Ensure the user exists and has certain roles
  zhmc_user:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_user_name }}"
    state: present
    properties:
      description: "Example user 1"
      type: standard
      authentication_type: local
      password_rule_name: Basic
      password: foobar
      user_role_names:
        - hmc-access-administrator-tasks
        - hmc-all-system-managed-objects
  register: user1
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
user:
  description:
    - "For O(state=absent), an empty dictionary."
    - "For O(state=present|facts), a
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
      description: "Additional properties of the user, as described in the
        data model of the 'User' object in the R(HMC API,HMC API) book.
        Write-only properties in the data model are not included.
        The property names have hyphens (-) as described in that book."
      type: raw
    user-role-names:
      description: "Only present if O(expand_names=true): Name of the user
        roles referenced by property C(user-roles)."
      type: str
    user-role-objects:
      description:
        - "Deprecated: This result property is deprecated because the
           O(expand) parameter is deprecated."
        - "Only present if O(expand=true): User roles referenced by property
           C(user-roles)."
      type: dict
      contains:
        "{property}":
          description: "Properties of the user role, as described in the
            data model of the 'User Pattern' object in the R(HMC API,HMC API)
            book.
            The property names have hyphens (-) as described in that book."
          type: raw
    user-pattern-name:
      description: "Only present for users with C(type=pattern) and if
        O(expand_names=true): Name of the user pattern referenced by property
        C(user-pattern-uri)."
      type: str
    user-pattern:
      description:
        - "Deprecated: This result property is deprecated because the
           O(expand) parameter is deprecated."
        - "Only present for users with C(type=pattern) and if O(expand=true):
           User pattern referenced by property C(user-pattern-uri)."
      type: dict
      contains:
        "{property}":
          description: "Properties of the user pattern, as described in the
            data model of the 'User Pattern' object in the R(HMC API,HMC API)
            book.
            The property names have hyphens (-) as described in that book."
          type: raw
    user-template-name:
      description: "Only present for users with C(type=pattern) and if
        O(expand_names=true): Name of the template user referenced by property
        C(user-template-uri)."
      type: str
    user-template:
      description:
        - "Deprecated: This result property is deprecated because the
           O(expand) parameter is deprecated."
        - "Only present for users with C(type=pattern) and if O(expand=true):
           User template referenced by property C(user-template-uri)."
      type: dict
      contains:
        "{property}":
          description: "Properties of the template user, as described in the
            data model of the 'User' object in the R(HMC API,HMC API) book.
            The property names have hyphens (-) as described in that book."
          type: raw
    password-rule-name:
      description: "Only present if O(expand_names=true): Name of the password
        rule referenced by property C(password-rule-uri)."
      type: str
    password-rule:
      description:
        - "Deprecated: This result property is deprecated because the
           O(expand) parameter is deprecated."
        - "Only present if O(expand=true): Password rule referenced by property
           C(password-rule-uri)."
      type: dict
      contains:
        "{property}":
          description: "Properties of the password rule, as described in the
            data model of the 'Password Rule' object in the R(HMC API,HMC API)
            book.
            The property names have hyphens (-) as described in that book."
          type: raw
    ldap-server-definition-name:
      description: "Only present if O(expand_names=true): Name of the LDAP
        server definition referenced by property
        C(ldap-server-definition-uri)."
      type: str
    ldap-server-definition:
      description:
        - "Deprecated: This result property is deprecated because the
           O(expand) parameter is deprecated."
        - "Only present if O(expand=true): LDAP server definition referenced by
           property C(ldap-server-definition-uri)."
      type: dict
      contains:
        "{property}":
          description: "Properties of the LDAP server definition, as described
            in the data model of the 'LDAP Server Definition' object in the
            R(HMC API,HMC API) book.
            Write-only properties in the data model are not included.
            The property names have hyphens (-) as described in that book."
          type: raw
    primary-mfa-server-definition-name:
      description: "Only present if O(expand_names=true): Name of the MFA
        server definition referenced by property
        C(primary-mfa-server-definition-uri)."
      type: str
    primary-mfa-server-definition:
      description:
        - "Deprecated: This result property is deprecated because the
           O(expand) parameter is deprecated."
        - "Only present if O(expand=true): MFA server definition referenced by
           property C(primary-mfa-server-definition-uri)."
      type: dict
      contains:
        "{property}":
          description: "Properties of the MFA server definition, as described
            in the data model of the 'MFA Server Definition' object in the
            R(HMC API,HMC API) book.
            The property names have hyphens (-) as described in that book."
          type: raw
    backup-mfa-server-definition-name:
      description: "Only present if O(expand_names=true): Name of the MFA
        server definition referenced by property
        C(backup-mfa-server-definition-uri)."
      type: str
    backup-mfa-server-definition:
      description:
        - "Deprecated: This result property is deprecated because the
           O(expand) parameter is deprecated."
        - "Only present if O(expand=true): MFA server definition referenced by
           property C(backup-mfa-server-definition-uri)."
      type: dict
      contains:
        "{property}":
          description: "Properties of the MFA server definition, as described
            in the data model of the 'MFA Server Definition' object in the
            R(HMC API,HMC API) book.
            The property names have hyphens (-) as described in that book."
          type: raw
    default-group-name:
      description: "Only present if O(expand_names=true): Name of the Group
        referenced by property C(default-group-uri)."
      type: str
    default-group:
      description:
        - "Deprecated: This result property is deprecated because the
           O(expand) parameter is deprecated."
        - "Only present if O(expand=true): Group referenced by property
           C(default-group-uri)."
      type: dict
      contains:
        "{property}":
          description: "Properties of the Group, as described in the data model
            of the 'Group' object in the R(HMC API,HMC API) book.
            The property names have hyphens (-) as described in that book."
          type: raw
  sample:
    {
        "allow-management-interfaces": true,
        "allow-remote-access": true,
        "authentication-type": "local",
        "backup-mfa-server-definition-name": null,
        "backup-mfa-server-definition-uri": null,
        "class": "user",
        "default-group-name": null,
        "default-group-uri": null,
        "description": "",
        "disable-delay": 1,
        "disabled": false,
        "disruptive-pw-required": true,
        "disruptive-text-required": false,
        "email-address": null,
        "force-password-change": false,
        "force-shared-secret-key-change": null,
        "idle-timeout": 0,
        "inactivity-timeout": 0,
        "is-locked": false,
        "ldap-server-definition-name": null,
        "ldap-server-definition-uri": null,
        "max-failed-logins": 3,
        "max-web-services-api-sessions": 1000,
        "mfa-policy": null,
        "mfa-types": null,
        "mfa-userid": null,
        "mfa-userid-override": null,
        "min-pw-change-time": 0,
        "multi-factor-authentication-required": false,
        "name": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
        "object-id": "91773b88-0c99-11eb-b4d3-00106f237ab1",
        "object-uri": "/api/users/91773b88-0c99-11eb-b4d3-00106f237ab1",
        "parent": "/api/console",
        "parent-name": "HMC1",
        "password-expires": 87,
        "password-rule-name": "ZaaS",
        "password-rule-uri": "/api/console/password-rules/518ac1d8-bf98-11e9-b9dd-00106f237ab1",
        "primary-mfa-server-definition-name": null,
        "primary-mfa-server-definition-uri": null,
        "replication-overwrite-possible": true,
        "session-timeout": 0,
        "type": "standard",
        "user-role-names": [
            "hmc-system-programmer-tasks",
        ],
        "user-roles": [
            "/api/user-roles/19e90e27-1cae-422c-91ba-f76ac7fb8b82"
        ],
        "userid-on-ldap-server": null,
        "verify-timeout": 15,
        "web-services-api-session-idle-timeout": 360
    }
"""

import uuid  # noqa: E402
import logging  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402

from ..module_utils.common import log_init, open_session, close_session, \
    hmc_auth_parameter, Error, ParameterError, to_unicode, \
    process_normal_property, missing_required_lib, \
    common_fail_on_import_errors, parse_hmc_host, blanked_params, \
    blanked_dict, removed_dict, NOT_PRESENT  # noqa: E402

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

    # create+update properties:
    'name': (False, True, True, True, None, None),
    # name: provided in 'name' module parm
    'description': (True, True, True, True, None, to_unicode),
    'disabled': (True, True, True, True, None, bool),
    'authentication_type': (True, True, True, True, None, None),
    'user_roles': (False, False, False, None, None, None),
    # user_roles: Modified via user_role_names.
    'password_rule_uri': (False, True, True, None, None, None),
    # password_rule_uri: Modified via password_rule_name.
    'password': (True, True, True, True, None, None),
    # password: Write-only
    'force_password_change': (True, True, True, True, None, bool),
    'ldap_server_definition_uri': (False, True, True, None, None, None),
    # ldap_server_definition_uri: Modified via ldap_server_definition_name.
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
    'user_template_uri': (False, False, False, None, None, None),
    'password_expires': (False, False, False, None, None, None),
    'replication_overwrite_possible': (False, False, False, None, None, None),

    # read-only artificial if-expand properties:
    'user_role_objects': (False, False, False, None, None, None),
    'user_pattern': (False, False, False, None, None, None),
    'user_template': (False, False, False, None, None, None),
    'password_rule': (False, False, False, None, None, None),
    'ldap_server_definition': (False, False, False, None, None, None),
    'primary_mfa_server_definition': (False, False, False, None, None, None),
    'backup_mfa_server_definition': (False, False, False, None, None, None),
    'default_group': (False, False, False, None, None, None),

    # artificial if-expand-names properties:
    # Can be specxified as input, but are in output only if expand_names.
    'user_role_names': (True, True, True, True, None, None),
    'user_pattern_name': (True, True, True, True, None, None),
    'user_template_name': (True, True, True, True, None, None),
    'password_rule_name': (True, True, True, True, None, None),
    'ldap_server_definition_name': (True, True, True, True, None, None),
    'primary_mfa_server_definition_name': (True, True, True, True, None, None),
    'backup_mfa_server_definition_name': (True, True, True, True, None, None),
    'default_group_name': (True, True, True, True, None, None),
}

# Write-only properties (blanked out in logs and removed in output)
WRITEONLY_PROPERTIES_USCORE = ['password']
WRITEONLY_PROPERTIES_HYPHEN = [p.replace('_', '-')
                               for p in WRITEONLY_PROPERTIES_USCORE]


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
      tuple of (create_props, update_props, add_roles, rem_roles),
      where:
        * create_props: dict of properties for
          zhmcclient.UserManager.create()
        * update_props: dict of properties for
          zhmcclient.User.update_properties()
        * add_roles: list of UserRole objects to be added to user
        * rem_roles: list of UserRole objects to be removed from user

    Raises:
      ParameterError: An issue with the module parameters.
    """
    create_props = {}
    update_props = {}
    add_roles = []
    rem_roles = []

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
    input_props = params['properties']
    if input_props is None:
        input_props = {}

    for prop_name in input_props:

        if prop_name not in ZHMC_USER_PROPERTIES:
            raise ParameterError(
                f"Property {prop_name!r} is not defined in the data model for "
                "users.")

        # pylint: disable=unused-variable
        allowed, create, update, update_while_active, eq_func, type_cast = \
            ZHMC_USER_PROPERTIES[prop_name]

        if not allowed:
            raise ParameterError(
                f"Property {prop_name!r} is not allowed in the 'properties' "
                "module parameter.")

        # Process artificial properties allowed in input parameters

        if prop_name == 'user_role_names':
            user_role_names = input_props[prop_name]
            all_user_roles = console.user_roles.list()
            user_roles = []
            for user_role_name in user_role_names:
                for r in all_user_roles:
                    if r.name == user_role_name:
                        user_roles.append(r)
                        break
                else:
                    raise ParameterError(
                        f"User role {user_role_name!r} specified in parameter "
                        f"{prop_name!r} does not exist.")
            if user is None:
                # All roles need to be added to the user
                add_roles.extend(user_roles)
            else:
                current_user_role_uris = user.get_property('user-roles')
                current_user_roles = [r for r in all_user_roles
                                      if r.uri in current_user_role_uris]
                current_user_role_names = [r.name for r in current_user_roles]
                for user_role in current_user_roles:
                    if user_role.name not in user_role_names:
                        # An existing role needs to be removed from the user
                        rem_roles.append(user_role)
                for user_role in user_roles:
                    if user_role.name not in current_user_role_names:
                        # A new role needs to be added to the user
                        add_roles.append(user_role)
            continue

        if prop_name == 'user_pattern_name':
            user_pattern_name = input_props[prop_name]
            if user_pattern_name:
                try:
                    user_pattern = console.user_patterns.find_by_name(
                        user_pattern_name)
                except zhmcclient.NotFound:
                    raise ParameterError(
                        f"User pattern {user_pattern_name!r} specified in "
                        f"parameter {prop_name!r} does not exist.")
                user_pattern_uri = user_pattern.uri
            else:
                user_pattern_uri = None
            if user is None:
                create_props['user-pattern-uri'] = user_pattern_uri
            elif user.prop('user-pattern-uri') != user_pattern_uri:
                update_props['user-pattern-uri'] = user_pattern_uri
            continue

        if prop_name == 'user_template_name':
            user_template_name = input_props[prop_name]
            if user_template_name:
                try:
                    user_template = console.users.find_by_name(
                        user_template_name)
                except zhmcclient.NotFound:
                    raise ParameterError(
                        f"Template user {user_template_name!r} specified in "
                        f"parameter {prop_name!r} does not exist.")
                user_template_uri = user_template.uri
            else:
                user_template_uri = None
            if user is None:
                create_props['user-template-uri'] = user_template_uri
            elif user.prop('user-template-uri') != user_template_uri:
                update_props['user-template-uri'] = user_template_uri
            continue

        if prop_name == 'password_rule_name':
            password_rule_name = input_props[prop_name]
            if password_rule_name:
                try:
                    password_rule = console.password_rules.find_by_name(
                        password_rule_name)
                except zhmcclient.NotFound:
                    raise ParameterError(
                        f"Password rule {password_rule_name!r} specified in "
                        f"parameter {prop_name!r} does not exist.")
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
                try:
                    ldap_srv_def = console.ldap_server_definitions.find_by_name(
                        ldap_srv_def_name)
                except zhmcclient.NotFound:
                    raise ParameterError(
                        f"LDAP server definition {ldap_srv_def_name!r} "
                        f"specified in parameter {prop_name!r} does not exist.")
                ldap_srv_def_uri = ldap_srv_def.uri
            else:
                ldap_srv_def_uri = None
            if user is None:
                create_props['ldap-server-definition-uri'] = ldap_srv_def_uri
            elif user.prop('ldap-server-definition-uri') != ldap_srv_def_uri:
                update_props['ldap-server-definition-uri'] = ldap_srv_def_uri
            continue

        if prop_name == 'primary_mfa_server_definition_name':
            pri_mfa_srv_def_name = input_props[prop_name]
            if pri_mfa_srv_def_name:
                try:
                    pri_mfa_srv_def = \
                        console.mfa_server_definitions.find_by_name(
                            pri_mfa_srv_def_name)
                except zhmcclient.NotFound:
                    raise ParameterError(
                        f"MFA server definition {pri_mfa_srv_def_name!r} "
                        f"specified in parameter {prop_name!r} does not exist.")
                pri_mfa_srv_def_uri = pri_mfa_srv_def.uri
            else:
                pri_mfa_srv_def_uri = None
            if user is None:
                create_props['primary-mfa-server-definition-uri'] = \
                    pri_mfa_srv_def_uri
            elif user.prop('primary-mfa-server-definition-uri') != \
                    pri_mfa_srv_def_uri:
                update_props['primary-mfa-server-definition-uri'] = \
                    pri_mfa_srv_def_uri
            continue

        if prop_name == 'backup_mfa_server_definition_name':
            bac_mfa_srv_def_name = input_props[prop_name]
            if bac_mfa_srv_def_name:
                try:
                    bac_mfa_srv_def = \
                        console.mfa_server_definitions.find_by_name(
                            bac_mfa_srv_def_name)
                except zhmcclient.NotFound:
                    raise ParameterError(
                        f"MFA server definition {bac_mfa_srv_def_name!r} "
                        f"specified in parameter {prop_name!r} does not exist.")
                bac_mfa_srv_def_uri = bac_mfa_srv_def.uri
            else:
                bac_mfa_srv_def_uri = None
            if user is None:
                create_props['backup-mfa-server-definition-uri'] = \
                    bac_mfa_srv_def_uri
            elif user.prop('backup-mfa-server-definition-uri') != \
                    bac_mfa_srv_def_uri:
                update_props['backup-mfa-server-definition-uri'] = \
                    bac_mfa_srv_def_uri
            continue

        if prop_name == 'default_group_name':
            default_group_name = input_props[prop_name]
            if default_group_name:
                try:
                    default_group = console.groups.find_by_name(
                        default_group_name)
                except zhmcclient.NotFound:
                    raise ParameterError(
                        f"Group {default_group_name!r} "
                        f"specified in parameter {prop_name!r} does not exist.")
                default_group_uri = default_group.uri
            else:
                default_group_uri = None
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
    return create_props, update_props, add_roles, rem_roles


def add_artificial_properties(
        user_properties, console, user, expand, expand_names):
    """
    Add artificial properties to the user_properties dict.

    Upon return, the user_properties dict has been extended by these properties:

    If O(expand_names) is True:

    * 'user-role-names': Names of UserRole objects corresponding to the URIs
      in the 'user-roles' property.

    * 'user-pattern-name': Name of UserPattern object corresponding to the URI
      in the 'user-pattern-uri' property, if type='pattern-based'.

    * 'user-template-name': Name of UserTemplate object corresponding to the
      URI in the 'user-template-uri' property, if type='pattern-based'.

    * 'password-rule-name': Name of PasswordRule object corresponding to the
      URI in the 'password-rule-uri' property.

    * 'ldap-server-definition-name': Name of LdapServerDefinition object
      corresponding to the URI in the 'ldap-server-definition-uri' property.

    * 'primary-mfa-server-definition-name': Name of MfaServerDefinition object
      corresponding to the URI in the 'primary-mfa-server-definition-uri'
      property.

    * 'backup-mfa-server-definition-name': Name of MfaServerDefinition object
      corresponding to the URI in the 'backup-mfa-server-definition-uri'
      property.

    * 'default-group-name': Name of the Group object corresponding to the URI
      in the 'default-group-uri' property.

    If O(expand) (deprecated) is True, in addition:

    * 'user-role-objects': List of UserRole objects corresponding to the
      URIs in the 'user-roles' property.

    * 'user-pattern': UserPattern object corresponding to the URI in the
      'user-pattern-uri' property, if type='pattern-based'.

    * 'user-template': UserTemplate object corresponding to the URI in the
      'user-template-uri' property, if type='pattern-based'.

    * 'password-rule': PasswordRule object corresponding to the URI in the
      'password-rule-uri' property.

    * 'ldap-server-definition': LdapServerDefinition object corresponding to
      the URI in the 'ldap-server-definition-uri' property.

    * 'primary-mfa-server-definition': MfaServerDefinition object corresponding
      to the URI in the 'primary-mfa-server-definition-uri' property.

    * 'backup-mfa-server-definition': MfaServerDefinition object corresponding
      to the URI in the 'backup-mfa-server-definition-uri' property.

    * 'default-group': Group object corresponding to the URI in the
      'default-group-uri' property.
    """

    if expand or expand_names:

        # Handle User Role references
        user_role_uris = user.properties['user-roles']
        # This property always exists
        all_uroles_by_uri = {ur.uri: ur for ur in console.user_roles.list()}
        uroles = [all_uroles_by_uri[uri] for uri in user_role_uris]
        if expand_names:
            user_properties['user-role-names'] = [ur.name for ur in uroles]
        if expand:
            user_role_objects = []
            for urole in uroles:
                urole.pull_full_properties()
                user_role_objects.append(dict(urole.properties))
            user_properties['user-role-objects'] = user_role_objects

        # Handle User Pattern reference
        if user.properties['type'] == 'pattern-based':

            # The 'user-pattern-uri' property exists only for
            # type='pattern-based', and will not be None.
            user_pattern_uri = user.properties['user-pattern-uri']
            if user_pattern_uri is None:  # Defensive programming
                if expand_names:
                    user_properties['user-pattern-name'] = None
                if expand:
                    user_properties['user-pattern'] = None
            else:
                user_pattern = \
                    console.user_patterns.resource_object(user_pattern_uri)
                # Note: Accessing 'name' triggers a full pull, and the
                # User Pattern object does not support selective get.
                user_pattern.pull_full_properties()
                if expand_names:
                    user_properties['user-pattern-name'] = user_pattern.name
                if expand:
                    user_properties['user-pattern'] = \
                        dict(user_pattern.properties)

            # The 'user-template-uri' property exists only for
            # type='pattern-based' and if the user is template-based, and may
            # be None.
            user_template_uri = user.properties.get(
                'user-template-uri', NOT_PRESENT)
            if user_template_uri == NOT_PRESENT:
                pass
            elif user_template_uri is None:
                if expand_names:
                    user_properties['user-template-name'] = None
                if expand:
                    user_properties['user-template'] = None
            else:
                user_template = console.users.resource_object(user_template_uri)
                # Note: Accessing 'name' triggers a full pull, and the
                # User object does not support selective get.
                user_template.pull_full_properties()
                if expand_names:
                    user_properties['user-template-name'] = user_template.name
                if expand:
                    user_properties['user-template'] = \
                        dict(user_template.properties)

        # Handle Password Rule reference
        password_rule_uri = user.properties['password-rule-uri']
        # This property always exists. It will be non-Null for
        # auth-type='local'.
        if password_rule_uri is None:
            if expand_names:
                user_properties['password-rule-name'] = None
            if expand:
                user_properties['password-rule'] = None
        else:
            password_rule = console.password_rules.resource_object(
                password_rule_uri)
            # Note: Accessing 'name' triggers a full pull, and the
            # Password Rule object does not support selective get.
            password_rule.pull_full_properties()
            if expand_names:
                user_properties['password-rule-name'] = password_rule.name
            if expand:
                user_properties['password-rule'] = \
                    dict(password_rule.properties)

        # Handle LDAP Server Definition reference
        ldap_srv_def_uri = user.properties['ldap-server-definition-uri']
        # This property always exists and is non-Null for auth.-type='ldap'.
        if ldap_srv_def_uri is None:
            if expand_names:
                user_properties['ldap-server-definition-name'] = None
            if expand:
                user_properties['ldap-server-definition'] = None
        else:
            ldap_srv_def = console.ldap_server_definitions.resource_object(
                ldap_srv_def_uri)
            # Note: Accessing 'name' triggers a full pull, and the
            # LDAP Server Definition object does not support selective get.
            ldap_srv_def.pull_full_properties()
            if expand_names:
                user_properties['ldap-server-definition-name'] = \
                    ldap_srv_def.name
            if expand:
                user_properties['ldap-server-definition'] = \
                    dict(ldap_srv_def.properties)

        # Handle primary MFA Server Definition reference
        pri_mfa_srv_def_uri = \
            user.properties['primary-mfa-server-definition-uri']
        # This property always exists and may be None
        if pri_mfa_srv_def_uri is None:
            if expand_names:
                user_properties['primary-mfa-server-definition-name'] = None
            if expand:
                user_properties['primary-mfa-server-definition'] = None
        else:
            pri_mfa_srv_def = console.mfa_server_definitions.resource_object(
                pri_mfa_srv_def_uri)
            # Note: Accessing 'name' triggers a full pull, and the
            # MFA Server Definition object does not support selective get.
            pri_mfa_srv_def.pull_full_properties()
            if expand_names:
                user_properties['primary-mfa-server-definition-name'] = \
                    pri_mfa_srv_def.name
            if expand:
                user_properties['primary-mfa-server-definition'] = \
                    dict(pri_mfa_srv_def.properties)

        # Handle backu0p MFA Server Definition reference
        bac_mfa_srv_def_uri = \
            user.properties['backup-mfa-server-definition-uri']
        # This property always exists and may be None
        if bac_mfa_srv_def_uri is None:
            if expand_names:
                user_properties['backup-mfa-server-definition-name'] = None
            if expand:
                user_properties['backup-mfa-server-definition'] = None
        else:
            bac_mfa_srv_def = console.mfa_server_definitions.resource_object(
                bac_mfa_srv_def_uri)
            # Note: Accessing 'name' triggers a full pull, and the
            # MFA Server Definition object does not support selective get.
            bac_mfa_srv_def.pull_full_properties()
            if expand_names:
                user_properties['backup-mfa-server-definition-name'] = \
                    bac_mfa_srv_def.name
            if expand:
                user_properties['backup-mfa-server-definition'] = \
                    dict(bac_mfa_srv_def.properties)

        # Handle default Group reference
        default_group_uri = user.properties['default-group-uri']
        # This property always exists, and may be None
        if default_group_uri is None:
            if expand_names:
                user_properties['default-group-name'] = None
            if expand:
                user_properties['default-group'] = None
        else:
            default_group = console.groups.resource_object(
                default_group_uri)
            # Note: Accessing 'name' triggers a full pull, and the
            # Password Rule object does not support selective get.
            default_group.pull_full_properties()
            if expand_names:
                user_properties['default-group-name'] = default_group.name
            if expand:
                user_properties['default-group'] = \
                    dict(default_group.properties)


def create_check_mode_user(console, create_props, update_props):
    """
    Create and return a fake local User object.

    This is used when a user needs to be created in check mode.

    This function must be consistent with the behavior of the "Create User"
    operation on the HMC. HTTP errors the HMC would return are indicated by
    raising zhmcclient.HTTPError.
    """

    input_props = {}
    input_props.update(create_props)
    input_props.update(update_props)

    # Check required input properties
    missing_props = []
    for pname in ('name', 'type', 'authentication-type'):
        if pname not in input_props:
            missing_props.append(pname)
    name = input_props['name']
    user_type = input_props['type']
    auth_type = input_props['authentication-type']
    if auth_type == 'local':
        for pname in ('password-rule-uri', 'password'):
            if pname not in input_props:
                missing_props.append(pname)
    if auth_type == 'ldap':
        for pname in ('ldap-server-definition-uri'):
            if pname not in input_props:
                missing_props.append(pname)
    mfa_types = input_props.get('mfa-types', [])
    if 'mfa-server' in mfa_types:
        for pname in ('primary-mfa-server-definition-uri', 'mfa-policy'):
            if pname not in input_props:
                missing_props.append(pname)
    if missing_props:
        raise zhmcclient.HTTPError({
            'http-status': 400,
            'reason': 4,
            'message': "Required input properties missing for Create User: "
            f"{missing_props}",
        })

    # Defaults for optional properties that are the same in all cases
    props = {
        'description': '',
        'session-timeout': 0,
        'verify-timeout': 15,
        'idle-timeout': 0,
        'max-failed-logins': 3,
        'disable-delay': 1,
        'inactivity-timeout': 0,
        'disruptive-pw-required': True,
        'disruptive-text-required': False,
        'allow-remote-access': False,
        'allow-management-interfaces': False,
        'max-web-services-api-sessions': 100,
        'web-services-api-session-idle-timeout': 360,
        'user-roles': [],
        'default-group-uri': None,
        'replication-overwrite-possible': False,  # Default not in WS-API book
        'multi-factor-authentication-required': False,
        'email-address': None,
        'mfa-types': None,
        'password-rule-uri': None,
        'force-password-change': True,
        'min-pw-change-time': 0,
        'ldap-server-definition-uri': None,
        'primary-mfa-server-definition-uri': None,
        'backup-mfa-server-definition-uri': None,
        'mfa-policy': None,
        'mfa-userid-override': None,
    }

    # Defaults for optional properties that depend on the case
    if user_type == 'pattern-based':
        props['user-pattern-uri'] = None
        props['user-template-uri'] = None
    if user_type != 'template':
        props['disabled'] = False
        props['password-expires'] = None
        props['userid-on-ldap-server'] = ''
    if auth_type == 'local':
        props['password'] = None
    mfa_required = input_props.get(
        'multi-factor-authentication-required', False)
    if mfa_required:
        props['force-shared-secret-key-change'] = False
    else:
        props['force-shared-secret-key-change'] = None
    if 'mfa-server' in mfa_types and user_type != 'template':
        props['mfa-userid'] = name
    else:
        props['mfa-userid'] = None

    # Apply specified input properties on top of the defaults
    props.update(input_props)

    user_oid = f'fake-{uuid.uuid4()}'
    user = console.users.resource_object(user_oid, props=props)

    return user


def ensure_present(params, check_mode):
    """
    Ensure that the user exists and has the specified properties.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    user_name = params['name']
    expand = params['expand']
    expand_names = params['expand_names']

    changed = False
    result = {}

    session, logoff = open_session(params)
    try:
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
            create_props, update_props, add_roles, rem_roles = \
                process_properties(console, user, params)
            update2_props = {}
            for name, value in update_props.items():
                if name not in create_props:
                    update2_props[name] = value
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
            result = dict(user.properties)
            changed = True
            for role in add_roles:
                LOGGER.debug(
                    "Adding role %r to user %r", role.name, user_name)
                if not check_mode:
                    user.add_user_role(role)
                if 'user-roles' not in result:
                    result['user-roles'] = []
                result['user-roles'].append(role.uri)
            if rem_roles:
                raise AssertionError(
                    f"Unexpected attempt to remove user roles {rem_roles!r} "
                    f"from newly created user {user.name!r}")
        else:
            # It exists. Update its properties.
            user.pull_full_properties()
            result = dict(user.properties)
            create_props, update_props, add_roles, rem_roles = \
                process_properties(console, user, params)
            if create_props:
                raise AssertionError("Unexpected "
                                     "create_props: %r" % create_props)
            if update_props:
                if LOGGER.isEnabledFor(logging.DEBUG):
                    LOGGER.debug(
                        "Existing user %r needs to get properties updated: %r",
                        user_name,
                        blanked_dict(update_props, WRITEONLY_PROPERTIES_USCORE))
                if not check_mode:
                    user.update_properties(update_props)
                    # We refresh the properties after the update, in case an
                    # input property value gets changed.
                    user.pull_full_properties()
                    result = dict(user.properties)
                else:
                    # Update the local User object's properties
                    result.update(update_props)
                changed = True
            for role in add_roles:
                LOGGER.debug(
                    "Adding role %r to user %r", role.name, user_name)
                if not check_mode:
                    user.add_user_role(role)
                if 'user-roles' not in result:
                    result['user-roles'] = []
                result['user-roles'].append(role.uri)
                changed = True
            for role in rem_roles:
                LOGGER.debug(
                    "Removing role %r from user %r", role.name, user_name)
                if not check_mode:
                    user.remove_user_role(role)
                if 'user-roles' not in result:
                    raise AssertionError(
                        f"User {user.name!r} unexpectedly does not have a "
                        "'user-roles' property")
                result['user-roles'].remove(role.uri)
                changed = True

        if not user:
            raise AssertionError()

        add_artificial_properties(
            result, console, user, expand, expand_names)

        result = removed_dict(result, WRITEONLY_PROPERTIES_HYPHEN)

        return changed, result

    finally:
        close_session(session, logoff)


def ensure_absent(params, check_mode):
    """
    Ensure that the user does not exist.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    user_name = params['name']

    changed = False
    result = {}

    session, logoff = open_session(params)
    try:
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
        close_session(session, logoff)


def facts(params, check_mode):
    # pylint: disable=unused-argument
    """
    Return facts about a user.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    user_name = params['name']
    expand = params['expand']
    expand_names = params['expand_names']

    changed = False
    result = {}

    session, logoff = open_session(params)
    try:
        # The default exception handling is sufficient for this code
        client = zhmcclient.Client(session)
        console = client.consoles.console

        user = console.users.find(name=user_name)
        user.pull_full_properties()

        result = dict(user.properties)
        add_artificial_properties(
            result, console, user, expand, expand_names)

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
        expand=dict(required=False, type='bool', default=False),
        expand_names=dict(required=False, type='bool', default=True),
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
                     blanked_params(module.params, WRITEONLY_PROPERTIES_USCORE))

    if module.params['expand']:
        LOGGER.warning(
            "Deprecated parameter 'expand' is used for zhmc_user module")

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
        "Module exit (success): changed: %r, user: %r", changed, result)
    module.exit_json(changed=changed, user=result)


if __name__ == '__main__':
    main()
