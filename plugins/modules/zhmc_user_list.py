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
  full_properties:
    description:
      - "If True, all properties of each user will be returned.
        Default: False."
      - "Note: Setting this to True causes a loop of 'Get User Properties'
        operations to be executed."
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
      description: "Type of the user ('standard', 'template', 'pattern-based',
        'system-defined')"
      type: str
    "{additional_property}":
      description: Additional properties requested via C(full_properties).
        The property names will have underscores instead of hyphens.
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
LOGGER_NAME = 'zhmc_user_list'

LOGGER = logging.getLogger(LOGGER_NAME)


def perform_list(params):
    """
    List the users and return a subset of properties.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    full_properties = params['full_properties']

    session, logoff = open_session(params)
    try:
        client = zhmcclient.Client(session)
        console = client.consoles.console

        user_list = []

        # List the users
        users = console.users.list(full_properties=full_properties)
        # The default exception handling is sufficient for the above.
        for user in users:

            user_properties = {}
            for pname_hmc, pvalue in user.properties.items():
                pname = pname_hmc.replace('-', '_')
                user_properties[pname] = pvalue

            user_list.append(user_properties)

        return user_list

    finally:
        close_session(session, logoff)


def main():

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='str'),
        hmc_auth=hmc_auth_parameter(),
        full_properties=dict(required=False, type='bool', default=False),
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

    changed = False
    try:

        result_list = perform_list(module.params)

    except (Error, zhmcclient.Error) as exc:
        # These exceptions are considered errors in the environment or in user
        # input. They have a proper message that stands on its own, so we
        # simply pass that message on and will not need a traceback.
        msg = "{0}: {1}".format(exc.__class__.__name__, exc)
        LOGGER.debug("Module exit (failure): msg: %r", msg)
        module.fail_json(msg=msg)
    # Other exceptions are considered module errors and are handled by Ansible
    # by showing the traceback.

    LOGGER.debug("Module exit (success): changed: %s, users: %r",
                 changed, result_list)
    module.exit_json(changed=changed, users=result_list)


if __name__ == '__main__':
    main()
