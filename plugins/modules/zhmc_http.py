#!/usr/bin/python
# Copyright 2026 IBM Corp. All Rights Reserved.
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
module: zhmc_http
version_added: "2.9.0"
short_description: Perform direct HTTP requests
description:
  - Perform a direct GET/POST/DELETE HTTP request against the HMC WS-API.
  - This module can be used as a fallback for HMC WS-API operations that are
    not yet supported with other modules of this collection.
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
  method:
    description:
      - "The HTTP method to be executed, in lower case."
    type: str
    required: true
    choices: ['get', 'post', 'delete']
  uri:
    description:
      - "The canonical URI of the targeted resource starting with '/api/',
         including any query parameters."
    type: str
    required: true
  request_body:
    description:
      - "The request body for the HTTP request."
      - "Only permitted for C(method=post)."
    type: dict
    required: false
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
- name: List Dual-Control Requests
  zhmc_http:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth:
      userid: "{{ my_hmc_userid }}"
      password: "{{ my_hmc_password }}"
      verify: true
      ca_certs: "{{ my_certs_dir }}"
    method: get
    uri: /api/console/dual-control-requests
  register: dual_control_result
"""

RETURN = """
changed:
  description: Indicates if any change has been made by the module.
    This will always be false for HTTP GET operations, and will always be true
    for HTTP POST and DELETE operations.
  returned: always
  type: bool
msg:
  description: An error message that describes the failure. If an HTTP response
    was received, this will include HTTP status code, reason code and the
    message from the error response body.
  returned: failure
  type: str
response_body:
  description: The response body of the HTTP operation.
    If no HTTP response was received, this will be null.
  returned: always
  type: dict
"""

import logging  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule, \
    missing_required_lib  # noqa: E402

from ..module_utils.common import log_init, open_session, close_session, \
    hmc_auth_parameter, Error, ParameterError, common_fail_on_import_errors, \
    parse_hmc_host, blanked_params  # noqa: E402

try:
    import zhmcclient
    IMP_ZHMCCLIENT_ERR = None
except ImportError:
    IMP_ZHMCCLIENT_ERR = traceback.format_exc()

# Python logger name for this module
LOGGER_NAME = 'zhmc_http'

LOGGER = logging.getLogger(LOGGER_NAME)


def http_get(params, check_mode):
    # pylint: disable=unused-argument
    """
    Perform the HTTP GET method.

    This is performed regardless of check mode.

    Returns:
      tuple(changed, response_body)

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """
    uri = params['uri']
    request_body = params.get('request_body')
    if request_body is not None:
        raise ParameterError(
            "Module parameter 'request_body' is not permitted for HTTP GET")

    changed = False
    session, logoff = open_session(params)
    try:
        result = session.get(uri)
        return changed, result
    finally:
        close_session(session, logoff)


def http_post(params, check_mode):
    # pylint: disable=unused-argument
    """
    Perform the HTTP POST method.

    In check mode, this operation is not performed and the returned result
    body will be null.

    Returns:
      tuple(changed, response_body)

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """
    uri = params['uri']
    request_body = params.get('request_body')

    changed = True

    if check_mode:
        return changed, None

    session, logoff = open_session(params)
    try:
        result = session.post(uri, body=request_body, wait_for_completion=True)
        return changed, result
    finally:
        close_session(session, logoff)


def http_delete(params, check_mode):
    # pylint: disable=unused-argument
    """
    Perform the HTTP DELETE method.

    In check mode, this HTTP method is not performed and the returned
    response_body will be null.

    Returns:
      tuple(changed, response_body)

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """
    uri = params['uri']
    request_body = params.get('request_body')
    if request_body is not None:
        raise ParameterError(
            "Module parameter 'request_body' is not permitted for HTTP DELETE")

    changed = True

    if check_mode:
        return changed, None

    session, logoff = open_session(params)
    try:
        result = session.delete(uri)
        return changed, result
    finally:
        close_session(session, logoff)


def perform_task(params, check_mode):
    """
    Perform the task for this module, dependent on the 'method' module
    parameter.

    If check_mode is True, check whether changes would occur, but don't
    actually perform any changes.

    Raises:
      ParameterError: An issue with the module parameters.
      StatusError: An issue with the partition status.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """
    methods = {
        "get": http_get,
        "post": http_post,
        "delete": http_delete,
    }
    return methods[params['method']](params, check_mode)


def main():
    """Main function"""

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='raw'),
        hmc_auth=hmc_auth_parameter(),
        method=dict(required=True, type='str',
                    choices=['get', 'post', 'delete']),
        uri=dict(required=True, type='str'),
        request_body=dict(required=False, type='dict', default=None),
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

    changed = False
    try:

        changed, response_body = perform_task(module.params, module.check_mode)

    except zhmcclient.HTTPError as exc:
        msg = f"{exc.__class__.__name__}: {exc}"
        response_body = exc.body
        LOGGER.debug(
            "Module exit (failure): changed: %r, msg: %s", changed, msg)
        module.fail_json(changed=changed, msg=msg, response_body=response_body)
    except (Error, zhmcclient.Error) as exc:
        msg = f"{exc.__class__.__name__}: {exc}"
        LOGGER.debug(
            "Module exit (failure): changed: %r, msg: %s", changed, msg)
        module.fail_json(changed=changed, msg=msg)
    # The exceptions handled above are considered errors in the environment or
    # in user input. They have a proper message that stands on its own, so we
    # simply pass that message on and will not need a traceback.
    # Other exceptions are considered module errors and are handled by Ansible
    # by showing the traceback.

    LOGGER.debug(
        "Module exit (success): changed: %r", changed)
    module.exit_json(changed=changed, response_body=response_body)


if __name__ == '__main__':
    main()
