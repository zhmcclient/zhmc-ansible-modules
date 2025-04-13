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
module: zhmc_user_list
version_added: "2.9.0"
short_description: List HMC users
description:
  - List users on the HMC.
author:
  - Andreas Maier (@andy-maier)
requirements:
  - The HMC userid must have object-access permission to the target users, or task permission to the 'Manage Users' task.
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
  full_properties:
    description:
      - "If True, all properties of each user will be returned.
        Default: False."
      - "Note: Setting this to True causes a loop of 'Get User Properties'
        operations to be executed."
    type: bool
    required: false
    default: false
  expand_names:
    description:
      - "If True and O(full_properties) is set, additional artificial properties
         will be returned for the names of referenced objects, such as user
         roles, password rule, etc. Default: False."
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

- name: List users
  zhmc_user_list:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
  register: user_list
"""

RETURN = """
changed:
  description: Indicates if any change has been made by the module.
    This will always be false.
  returned: always
  type: bool
msg:
  description: An error message that describes the failure.
  returned: failure
  type: str
users:
  description: The list of users, with a subset of their properties.
  returned: success
  type: list
  elements: dict
  contains:
    name:
      description: "User name"
      type: str
    type:
      description: "Type of the user (V(standard), V(template),
        V(pattern-based), V(system-defined))"
      type: str
    "{additional_property}":
      description: Additional properties requested via O(full_properties).
        The property names will have underscores instead of hyphens.
      type: raw
    user_role_names:
      description: "Only present if O(expand_names=true): Name of the user
        roles referenced by property C(user_roles)."
      type: str
    user_pattern_name:
      description: "Only present for users with C(type=pattern) and if
        O(expand_names=true): Name of the user pattern referenced by property
        C(user_pattern_uri)."
      type: str
    user_template_name:
      description: "Only present for users with C(type=pattern) and if
        O(expand_names=true): Name of the template user referenced by property
        C(user_template_uri)."
      type: str
    password_rule_name:
      description: "Only present if O(expand_names=true): Name of the password
        rule referenced by property C(password_rule_uri)."
      type: str
    ldap_server_definition_name:
      description: "Only present if O(expand_names=true): Name of the LDAP
        server definition referenced by property
        C(ldap_server_definition_uri)."
      type: str
    primary_mfa_server_definition_name:
      description: "Only present if O(expand_names=true): Name of the MFA
        server definition referenced by property
        C(primary_mfa_server_definition_uri)."
      type: str
    backup_mfa_server_definition_name:
      description: "Only present if O(expand_names=true): Name of the MFA
        server definition referenced by property
        C(backup_mfa_server_definition_uri)."
      type: str
    default_group_name:
      description: "Only present if O(expand_names=true): Name of the Group
        referenced by property C(default_group_uri)."
      type: str
  sample:
    [
        {
            "name": "Standard",
            "type": "system-defined"
        },
        {
            "name": "User 1",
            "type": "standard"
        }
    ]
"""

import logging  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402

from ..module_utils.common import log_init, open_session, close_session, \
    hmc_auth_parameter, Error, missing_required_lib, \
    common_fail_on_import_errors, parse_hmc_host, blanked_params, \
    NOT_PRESENT  # noqa: E402

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
LOGGER_NAME = 'zhmc_user_list'

LOGGER = logging.getLogger(LOGGER_NAME)


def add_artificial_properties_expand(
        user_properties, user, user_roles_by_uri, user_patterns_by_uri,
        users_by_uri, password_rules_by_uri, ldap_server_definitions_by_uri,
        mfa_server_definitions_by_uri, groups_by_uri):
    """
    Add artificial properties to the user_properties dict. This function is
    called only when full_properties and expand_names are specified.

    Upon return, the user_properties dict has been extended by these properties:

    * 'user-role-names': Names of UserRole objects corresponding to the URIs
      in the 'user-roles' property.

    * 'user-pattern-name': Name of UserPattern object corresponding to the URI
      in the 'user-pattern-uri' property, if type='pattern-based'.

    * 'user-template-name': Name of User object corresponding to the
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
    """

    # Handle User Role references
    user_role_uris = user.properties['user-roles']
    # This property always exists
    uroles = [user_roles_by_uri[uri] for uri in user_role_uris]
    user_properties['user-role-names'] = [ur.name for ur in uroles]

    # Handle User Pattern reference
    if user.properties['type'] == 'pattern-based':

        # This property exists only for type='pattern-based', and will not be
        # None.
        user_pattern_uri = user.properties['user-pattern-uri']
        if user_pattern_uri is None:  # Defensive programming
            user_properties['user-pattern-name'] = None
        else:
            # Note: Accessing 'name' triggers a full pull, and the
            # User Pattern object does not support selective get.
            user_properties['user-pattern-name'] = \
                user_patterns_by_uri[user_pattern_uri].name

        # This property exists only for type='pattern-based' and if the user
        # is template-based, and may be None.
        user_template_uri = user.properties.get(
            'user-template-uri', NOT_PRESENT)
        if user_template_uri == NOT_PRESENT:
            pass
        elif user_template_uri is None:
            user_properties['user-template-name'] = None
        else:
            # Note: Accessing 'name' triggers a full pull, and the
            # User object does not support selective get.
            user_properties['user-template-name'] = \
                users_by_uri[user_template_uri].name

    # Handle Password Rule reference
    password_rule_uri = user.properties['password-rule-uri']
    # This property always exists. It will be non-Null for auth-type='local'.
    if password_rule_uri is None:
        user_properties['password-rule-name'] = None
    else:
        # Note: Accessing 'name' triggers a full pull, and the
        # Password Rule object does not support selective get.
        user_properties['password-rule-name'] = \
            password_rules_by_uri[password_rule_uri].name

    # Handle LDAP Server Definition reference
    ldap_srv_def_uri = user.properties['ldap-server-definition-uri']
    # This property always exists and is non-Null for auth.-type='ldap'.
    if ldap_srv_def_uri is None:
        user_properties['ldap-server-definition-name'] = None
    else:
        # Note: Accessing 'name' triggers a full pull, and the
        # LDAP Server Definition object does not support selective get.
        user_properties['ldap-server-definition-name'] = \
            ldap_server_definitions_by_uri[ldap_srv_def_uri].name

    # Handle primary MFA Server Definition reference
    pri_mfa_srv_def_uri = user.properties['primary-mfa-server-definition-uri']
    # This property always exists and may be None
    if pri_mfa_srv_def_uri is None:
        user_properties['primary-mfa-server-definition-name'] = None
    else:
        # Note: Accessing 'name' triggers a full pull, and the
        # MFA Server Definition object does not support selective get.
        user_properties['primary-mfa-server-definition-name'] = \
            mfa_server_definitions_by_uri[pri_mfa_srv_def_uri].name

    # Handle backup MFA Server Definition reference
    bac_mfa_srv_def_uri = user.properties['backup-mfa-server-definition-uri']
    # This property always exists and may be None
    if bac_mfa_srv_def_uri is None:
        user_properties['backup-mfa-server-definition-name'] = None
    else:
        # Note: Accessing 'name' triggers a full pull, and the
        # MFA Server Definition object does not support selective get.
        user_properties['backup-mfa-server-definition-name'] = \
            mfa_server_definitions_by_uri[bac_mfa_srv_def_uri].name

    # Handle default Group reference
    default_group_uri = user.properties['default-group-uri']
    # This property always exists, and may be None
    if default_group_uri is None:
        user_properties['default-group-name'] = None
    else:
        # Note: Accessing 'name' triggers a full pull, and the
        # default Group object does not support selective get.
        user_properties['default-group-name'] = \
            groups_by_uri[default_group_uri].name


def perform_list(params):
    """
    List the users, expand artificial properties and return a list of users.

    The set of properties in the returned users depends on module parameters
    'full_properties' and 'expand_names'.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    full_properties = params['full_properties']
    expand_names = params['expand_names']

    session, logoff = open_session(params)
    try:
        client = zhmcclient.Client(session)
        console = client.consoles.console

        user_list = []

        # List the users
        users = console.users.list(full_properties=full_properties)

        # Get the data for the name expansions only once
        if full_properties and expand_names:
            user_roles_by_uri = {x.uri: x for x in console.user_roles.list()}
            user_patterns_by_uri = {
                x.uri: x for x in console.user_patterns.list()}
            users_by_uri = {x.uri: x for x in users}
            password_rules_by_uri = {
                x.uri: x for x in console.password_rules.list()}
            ldap_server_definitions_by_uri = {
                x.uri: x for x in console.ldap_server_definitions.list()}
            mfa_server_definitions_by_uri = {
                x.uri: x for x in console.mfa_server_definitions.list()}
            groups_by_uri = {x.uri: x for x in console.groups.list()}

        # The default exception handling is sufficient for the above.

        for user in users:

            user_properties = dict(user.properties)
            if full_properties and expand_names:
                add_artificial_properties_expand(
                    user_properties, user, user_roles_by_uri,
                    user_patterns_by_uri, users_by_uri, password_rules_by_uri,
                    ldap_server_definitions_by_uri,
                    mfa_server_definitions_by_uri, groups_by_uri)

            user_properties_under = {
                n.replace('-', '_'): v for n, v in user_properties.items()}

            user_list.append(user_properties_under)

        return user_list

    finally:
        close_session(session, logoff)


def main():
    """Main function"""

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='raw'),
        hmc_auth=hmc_auth_parameter(),
        full_properties=dict(required=False, type='bool', default=False),
        expand_names=dict(required=False, type='bool', default=False),
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

    changed = False
    try:

        result_list = perform_list(module.params)

    except (Error, zhmcclient.Error) as exc:
        # These exceptions are considered errors in the environment or in user
        # input. They have a proper message that stands on its own, so we
        # simply pass that message on and will not need a traceback.
        msg = f"{exc.__class__.__name__}: {exc}"
        LOGGER.debug("Module exit (failure): msg: %r", msg)
        module.fail_json(msg=msg)
    # Other exceptions are considered module errors and are handled by Ansible
    # by showing the traceback.

    LOGGER.debug("Module exit (success): changed: %s, users: %r",
                 changed, result_list)
    module.exit_json(changed=changed, users=result_list)


if __name__ == '__main__':
    main()
