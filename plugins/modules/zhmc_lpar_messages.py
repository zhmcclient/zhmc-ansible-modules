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
module: zhmc_lpar_messages
version_added: "2.9.0"
short_description: Get console messages for OS in an LPAR
description:
  - Get the OS console messages for the OS running in a loaded LPAR.
author:
  - Andreas Maier (@andy-maier)
requirements:
  - The targeted CPC must be in the classic operational mode.
  - The targeted LPAR must be loaded (i.e. running an operating system).
  - "The HMC userid must have these task permissions:
    'Operating System Messages' (view-only is sufficient)"
  - "The HMC userid must have object-access permissions to these objects:
    Target CPC, target LPAR."
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
      - The name of the CPC with the target LPAR.
    type: str
    required: true
  name:
    description:
      - The name of the target LPAR.
    type: str
    required: true
  begin:
    description:
      - "A message sequence number to limit returned messages. Messages with
         a sequence number less than this are omitted from the results."
      - "If null, no such filtering is performed."
    type: int
    required: false
    default: null
  end:
    description:
      - "A message sequence number to limit returned messages. Messages with
         a sequence number greater than this are omitted from the results."
      - "If null, no such filtering is performed."
    type: int
    required: false
    default: null
  max_messages:
    description:
      - "Limits the returned messages to the specified maximum number, starting
         from the begin of the sequence numbers in the result that would
         otherwise be returned."
      - "If null or 0, no such filtering is performed."
    type: int
    required: false
    default: null
  is_held:
    description:
      - "Limit the returned messages to only held (if true) or only non-held
         (if false) messages."
      - "If null, no such filtering is performed."
    type: bool
    required: false
    default: null
  is_priority:
    description:
      - "Limit the returned messages to only priority (if true) or only
         non-priority (if false) messages."
      - "If null, no such filtering is performed."
    type: bool
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

- name: Get OS console messages for the OS in the LPAR
  zhmc_lpar_messages:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    name: "{{ my_lpar_name }}"
  register: lpar_messages

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
messages:
  description:
    - "The list of operating system console messages."
  returned: success
  type: list
  elements: dict
  contains:
    sequence_number:
      description:
      - "The sequence number assigned to this message by the HMC."
      - "Although sequence numbers may wrap over time, this number can be
         considered a unique identifier for the message."
      type: int
    message_text:
      description: "The text of the message"
      type: str
    message_id:
      description:
        - "The message identifier assigned to this message by the operating
           system."
      type: str
    timestamp:
      description:
        - "The point in time (as an ISO 8601 date and time value) when the
           message was created, or null if this information is not available
           from the operating system."
      type: str
    sound_alarm:
      description:
        - "Indicates whether the message should cause the alarm to be sounded."
      type: bool
    is_priority:
      description:
        - "Indicates whether the message is a priority message."
        - "A priority message indicates a critical condition that requires
           immediate attention."
      type: bool
    is_held:
      description:
        - "Indicates whether the message is a held message."
        - "A held message is one that requires a response."
      type: bool
    prompt_text:
      description:
        - "The prompt text that is associated with this message, or null
           indicating that there is no prompt text for this message."
        - "The prompt text is used when responding to a message. The response
           is to be sent as an operating system command where the command is
           prefixed with the prompt text and followed by the response to the
           message."
      type: str
    os_name:
      description:
        - "The name of the operating system that generated this omessage, or
           null indicating there is no operating system name  associated with
           this message."
        - "This name is determined by the operating system and may be unrelated
           to the name of the LPAR in which the operating system is running."
      type: str
  sample:
    [
        {
            "is_held": false,
            "is_priority": false,
            "message_id": 2328551,
            "message_text": "Uncompressing Linux... \n",
            "os_name": null,
            "prompt_text": "",
            "sequence_number": 0,
            "sound_alarm": false,
            "timestamp": null
        },
        {
            "is_held": false,
            "is_priority": false,
            "message_id": 2328552,
            "message_text": "Ok, booting the kernel.\n",
            "os_name": null,
            "prompt_text": "",
            "sequence_number": 1,
            "sound_alarm": false,
            "timestamp": null
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

try:
    import pytz
    IMP_PYTZ_ERR = None
except ImportError:
    IMP_PYTZ_ERR = traceback.format_exc()

# Python logger name for this module
LOGGER_NAME = 'zhmc_lpar'

LOGGER = logging.getLogger(LOGGER_NAME)


def find_lpar(client, cpc_name, lpar_name):
    """
    Find the specified LPAR in the specified CPC.

    The "List Permitted Logical Partitions" operation is used when available.

    Returns:
      zhmcclient.Lpar

    Raises:
      zhmcclient.NotFound: LPAR does not exist.
    """
    # The "List Permitted Logical Partitions" operation was added in HMC
    # version 2.14.0. The operation depends only on the HMC version and not
    # on the SE/CPC version, so it is supported e.g. for a 2.14 HMC managing
    # a z13 CPC.
    hmc_version = client.query_api_version()['hmc-version']
    hmc_version_info = [int(x) for x in hmc_version.split('.')]
    if hmc_version_info < [2, 14, 0]:
        # Find the LPAR in the traditional way
        cpc = client.cpcs.find(name=cpc_name)
        lpar = cpc.lpars.find(name=lpar_name)
    else:
        # Find the LPAR using the new operation
        filter_args = {'cpc-name': cpc_name, 'name': lpar_name}
        lpars = client.consoles.console.list_permitted_lpars(
            filter_args=filter_args)
        try:
            lpar = lpars[0]
        except IndexError:
            raise zhmcclient.NotFound(
                message="Could not find LPAR {ln!r} in permitted LPARs of "
                "CPC {c!r}".format(ln=lpar_name, c=cpc_name))
    return lpar


def perform_os_messages(params):
    """
    Get the OS console messages and return a list of them.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    cpc_name = params['cpc_name']
    lpar_name = params['name']
    begin = params['begin']
    end = params['end']
    is_held = params['is_held']
    is_priority = params['is_priority']
    max_messages = params['max_messages']
    if max_messages is None:
        max_messages = 0

    session, logoff = open_session(params)
    try:
        client = zhmcclient.Client(session)

        lpar = find_lpar(client, cpc_name, lpar_name)

        result_dict = lpar.list_os_messages(
            begin=begin, end=end, is_held=is_held, is_priority=is_priority,
            max_messages=max_messages)

        result = []
        for os_message in result_dict['os-messages']:
            hmc_ts = os_message.get('timestamp')
            if hmc_ts == -1:
                timestamp = None
            else:
                dt = zhmcclient.datetime_from_timestamp(hmc_ts, tzinfo=pytz.utc)
                timestamp = dt.isoformat()
            result_message = {
                "sequence_number": os_message.get('sequence-number'),
                "message_text": os_message.get('message-text'),
                "message_id": os_message.get('message-id'),
                "timestamp": timestamp,
                "sound_alarm": os_message.get('sound-alarm'),
                "is_priority": os_message.get('is-priority'),
                "is_held": os_message.get('is-held'),
                "prompt_text": os_message.get('prompt-text'),
                "os_name": os_message.get('os-name'),
            }
            result.append(result_message)

        return result

    finally:
        close_session(session, logoff)


def main():

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='str'),
        hmc_auth=hmc_auth_parameter(),
        cpc_name=dict(required=True, type='str'),
        name=dict(required=True, type='str'),
        begin=dict(required=False, type='int', default=None),
        end=dict(required=False, type='int', default=None),
        max_messages=dict(required=False, type='int', default=None),
        is_held=dict(required=False, type='bool', default=None),
        is_priority=dict(required=False, type='bool', default=None),
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

    if IMP_PYTZ_ERR is not None:
        module.fail_json(msg=missing_required_lib("pytz"),
                         exception=IMP_PYTZ_ERR)

    common_fail_on_import_errors(module)

    log_file = module.params['log_file']
    log_init(LOGGER_NAME, log_file)

    _params = dict(module.params)
    del _params['hmc_auth']
    LOGGER.debug("Module entry: params: %r", _params)

    changed = False
    try:

        result = perform_os_messages(module.params)

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
        "Module exit (success): changed: %r, messages: %r", changed, result)
    module.exit_json(changed=changed, messages=result)


if __name__ == '__main__':
    main()
