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
module: zhmc_session
version_added: "2.9.0"
short_description: Manage HMC sessions across tasks
description:
  - Create a session on the HMC for use by other ibm_zhmc modules, with
    O(action=create).
  - Delete a session on the HMC, with O(action=delete).
  - This module can be used in order to create an HMC session once and then use
    it for multiple tasks that use ibm_zhmc modules, reducing the number of HMC
    sessions that need to be created, to just one. When this module is not used,
    each ibm_zhmc module invocation will create and delete a separate HMC
    session.
author:
  - Andreas Maier (@andy-maier)
requirements: []
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
          - The userid (username) for creating the HMC session.
          - Required for O(action=create), not permitted for O(action=delete).
        type: str
        required: false
        default: null
      password:
        description:
          - The password for creating the HMC session.
          - Required for O(action=create), not permitted for O(action=delete).
        type: str
        required: false
        default: null
      session_id:
        description:
          - Session ID of the HMC session to be deleted.
          - Required for O(action=delete), not permitted for O(action=create).
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
          - Optional for O(action=create), not permitted for O(action=delete).
        type: str
        required: false
        default: null
      verify:
        description:
          - If True (default), verify the HMC certificate as specified in the
            O(hmc_auth.ca_certs) parameter. If False, ignore what is specified in the
            O(hmc_auth.ca_certs) parameter and do not verify the HMC certificate.
          - Optional for O(action=create), not permitted for O(action=delete).
        type: bool
        required: false
        default: true
  action:
    description:
      - "The action to perform for the HMC session. Since an HMC session does
         not have a name, it is not possible to specify the desired end state
         in an idempotent manner, so this module uses actions:"
      - "* V(create): Create a new session on the HMC and verify that the
         credentials are valid.
         Requires C(hmc_auth.userid) and C(hmc_auth.password) and uses
         C(hmc_auth.ca_certs) and C(hmc_auth.verify) if provided."
      - "* V(delete): Delete the specified session on the HMC. No longer
         existing sessions are tolerated. Requires C(hmc_auth.session_id)."
    type: str
    required: true
    choices: ['create', 'delete']
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
# Note: The following is a sequence of tasks that demonstrates the use
#       of the zhmc_session module for one other ibm_zhmc task. The example
#       assumes that some variables named 'my_*' are set.

- name: Create an HMC session
  zhmc_session:
    hmc_host: "{{ my_hmc_host }}"  # Single HMC or list of redundant HMCs
    hmc_auth:
      userid: "{{ my_hmc_userid }}"
      password: "{{ my_hmc_password }}"
      verify: true                      # optional
      ca_certs: "{{ my_certs_dir }}"    # optional
    action: create
  register: session
  no_log: true    # Protect result containing HMC session ID from being logged

- name: Example task using the previously created HMC session
  zhmc_cpc_list:
    hmc_host: "{{ session.hmc_host }}"  # The actually used HMC
    hmc_auth: "{{ session.hmc_auth }}"
  register: cpc_list

- name: Delete the HMC session
  zhmc_session:
    hmc_host: "{{ session.hmc_host }}"  # The actually used HMC
    hmc_auth: "{{ session.hmc_auth }}"
    action: delete
  register: session    # Just for safety in case it is used after that
"""

RETURN = """
changed:
  description: Indicates if any change has been made by the module.
    This will always be false, since a session creation on the HMC does
    not count as a change.
  returned: always
  type: bool
msg:
  description: An error message that describes the failure.
  returned: failure
  type: str
hmc_host:
  description:
    - The hostname or IP address of the HMC that was actually used for the
      session creation, for O(action=create). This value must be specified as
      O(hmc_host) for O(action=delete).
    - For O(action=delete), returns the null value.
  returned: success
  type: str
hmc_auth:
  description: Credentials for the HMC session, for use by other tasks. This
    return value should be protected with C(no_log=true) for O(action=create),
    since it contains the HMC session ID. For O(action=delete), the same
    structure is returned, just with null values. This can be used to reset
    the variable that was set for O(action=create).
  returned: success
  type: dict
  contains:
    session_id:
      description: "New HMC session ID for O(action=create), or null for
        O(action=delete)."
      type: str
    ca_certs:
      description: "Value of O(hmc_auth.ca_certs) input parameter for O(action=create),
        or null for O(action=delete)."
      type: str
    verify:
      description: "Value of O(hmc_auth.verify) input parameter for O(action=create),
        or null for O(action=delete)."
      type: bool
  sample:
    {
      "session_id": "xyz.........",
      "verify": true,
      "ca_certs": null
    }
"""

import logging  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402

from ..module_utils.common import log_init, open_session, close_session, \
    hmc_auth_parameter, Error, ParameterError, \
    missing_required_lib, parse_hmc_host, blanked_params  # noqa: E402

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
LOGGER_NAME = 'zhmc_session'

LOGGER = logging.getLogger(LOGGER_NAME)


def perform_action(params):
    """
    Create a logged-on HMC session and return its session-ID based auth data,
    or delete an HMC session identified by its session ID.

    Returns:
      dict: A dictionary useable for the 'hmc_auth' input parameter of
        ibm_zhmc modules.

    Raises:
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    faked_session = params.get('_faked_session', None)
    if faked_session is not None:
        raise ParameterError(
            "The zhmc_session module does not support the '_faked_session' "
            "module parameter.")

    hmc_auth = params['hmc_auth']
    session_id = hmc_auth.get('session_id', None)

    if params['action'] == 'create':

        if session_id is not None:
            raise ParameterError(
                "Requested action is to create an HMC session, but module "
                "parameter 'hmc_auth' has a 'session_id' item specified.")

        # With session_id None, this creates a client-side Session object
        # that is ready to log on, but it does not immediately create a new
        # session on the HMC.
        # pylint: disable=unused-variable
        session, logoff = open_session(params)

        # The logon creates the new session on the HMC and only after that,
        # the session_id attribute is set.
        session.logon(verify=True)

        if session.verify_cert is False:
            verify = False
            ca_certs = None
        elif session.verify_cert is True:
            verify = True
            ca_certs = None
        else:
            verify = True
            ca_certs = session.verify_cert

        hmc_auth = {
            'session_id': session.session_id,
            'verify': verify,
            'ca_certs': ca_certs,
        }
        hmc_host = session.actual_host
        return hmc_auth, hmc_host

    # action: delete (already verified)

    if session_id is None:
        raise ParameterError(
            "Requested action is to delete an HMC session, but module "
            "parameter 'hmc_auth' has no 'session_id' item specified.")

    # With session_id specified, this creates a client-side Session object
    # that knows the HMC session, but this does not interact with the HMC.
    session, logoff = open_session(params)

    # The logoff deletes the session on the HMC and resets the session_id
    # attribute to None.
    close_session(session, logoff=True)

    hmc_auth = {
        'session_id': None,
        'verify': None,
        'ca_certs': None,
    }
    return hmc_auth, None


def main():
    """Main function"""

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='raw'),
        hmc_auth=hmc_auth_parameter(),  # same definition as for other modules
        action=dict(required=True, type='str', choices=['create', 'delete']),
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

    log_file = module.params['log_file']
    log_init(LOGGER_NAME, log_file)

    module.params['hmc_host'] = parse_hmc_host(module.params['hmc_host'])

    if LOGGER.isEnabledFor(logging.DEBUG):
        LOGGER.debug("Module entry: params: %r",
                     blanked_params(module.params))

    # We do not count session creation or deletion as a change
    changed = False

    try:

        hmc_auth, hmc_host = perform_action(module.params)

    except (Error, zhmcclient.Error) as exc:
        # These exceptions are considered errors in the environment or in user
        # input. They have a proper message that stands on its own, so we
        # simply pass that message on and will not need a traceback.
        msg = f"{exc.__class__.__name__}: {exc}"
        LOGGER.debug("Module exit (failure): msg: %r", msg)
        module.fail_json(msg=msg)
    # Other exceptions are considered module errors and are handled by Ansible
    # by showing the traceback.

    LOGGER.debug("Module exit (success): changed: %s, hmc_auth: (not shown), "
                 "hmc_host: %r", changed, hmc_host)
    module.exit_json(changed=changed, hmc_auth=hmc_auth, hmc_host=hmc_host)


if __name__ == '__main__':
    main()
