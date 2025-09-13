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
module: zhmc_partition_command
version_added: "2.15.0"
short_description: Execute OS console command in a partition (DPM mode)
description:
  - Execute a command in the console of the OS running in a partition and
    get back the command output.
  - "Note: The OS console interface provided by the HMC WS-API does not allow
     separating multiple concurrent interactions. For example, when OS console
     commands are executed via the HMC GUI at the same time when executing this
     Ansible module, the command output returned by the Ansible module may be
     mixed with output from the concurrently executed command."
  - "Note: The logic for determining which lines on the OS console belong to
     the executed command is as follows: The OS console messages are started to
     be captured just before the console command is sent. The captured console
     messages are then searched for the occurrence of the command. The command
     itself and all messages following the command are considered part of the
     command output, until there are no more new messages for 2 seconds. If
     there is a lot of traffic on the OS console, that may lead to other
     messages being included in the command output."
author:
  - Andreas Maier (@andy-maier)
requirements:
  - The targeted CPC must be in the DPM operational mode.
  - The targeted partition must be active (i.e. running an operating system).
  - "The HMC userid must have these task permissions:
    'Operating System Messages' (view-only is sufficient)"
  - "The HMC userid must have object-access permissions to these objects:
    Target CPC, target partition."
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
  cpc_name:
    description:
      - The name of the CPC with the target partition.
    type: str
    required: true
  name:
    description:
      - The name of the target partition.
    type: str
    required: true
  command:
    description:
      - "The OS console command to be executed."
    type: str
    required: true
  is_priority:
    description:
      - "Controls whether the command is executed as a priority command."
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

- name: Get z/VM CP level via OS console command
  zhmc_partition_command:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    name: "{{ my_partition_name }}"
    command: "Q CPLEVEL"
  register: zvm_cplevel_output
"""

RETURN = """
changed:
  description:
  - "Indicates if any change has been made by the module."
  - "This will always be true, because it is not clear whether the command
     has performed a change. Note that a playbook using this module with
     a command that does not perform a change can override that by specifying
     C(changed_when: false)."
  returned: always
  type: bool
msg:
  description: An error message that describes the failure.
  returned: failure
  type: str
output:
  description:
    - "The command and its output, as one item per line, without any trailing
       newlines."
    - "The format of each message text depends on the type of OS.
       Typical formats are, showing the message with the command:"
    - "z/VM: C(04:30:02 Q CPLEVEL)"
    - "Linux: C(uname -a)"
  returned: success
  type: list
  elements: str
  sample:
    [
      "04:30:02 Q CPLEVEL",
      "04:30:02 z/VM Version 7 Release 2.0, service level 2101 (64-bit)",
      "04:30:02 Generated at 05/19/21 10:00:00 CES",
      "04:30:02 IPL at 06/04/24 19:18:57 CES"
    ]
"""

import logging  # noqa: E402
import traceback  # noqa: E402
import threading  # noqa: E402
import queue  # noqa: E402
from ansible.module_utils.basic import AnsibleModule, \
    missing_required_lib  # noqa: E402

from ..module_utils.common import log_init, open_session, close_session, \
    hmc_auth_parameter, Error, NotificationThread, \
    common_fail_on_import_errors, parse_hmc_host, blanked_params  # noqa: E402

try:
    import zhmcclient
    IMP_ZHMCCLIENT_ERR = None
except ImportError:
    IMP_ZHMCCLIENT_ERR = traceback.format_exc()

# Python logger name for this module
LOGGER_NAME = 'zhmc_partition_command'

LOGGER = logging.getLogger(LOGGER_NAME)


class NoCommandFoundError(Error):
    """
    Indicates that the command was not found in the OS console messages.
    """
    pass


def find_partition(client, cpc_name, partition_name):
    """
    Find the specified partition in the specified CPC.

    The "List Permitted Logical Partitions" operation is used when available.

    Returns:
      zhmcclient.Partition

    Raises:
      zhmcclient.NotFound: partition does not exist.
    """
    # The "List Permitted Logical Partitions" operation was added in HMC
    # version 2.14.0. The operation depends only on the HMC version and not
    # on the SE/CPC version, so it is supported e.g. for a 2.14 HMC managing
    # a z13 CPC.
    hmc_version = client.query_api_version()['hmc-version']
    hmc_version_info = [int(x) for x in hmc_version.split('.')]
    if hmc_version_info < [2, 14, 0]:
        # Find the partition in the traditional way
        cpc = client.cpcs.find(name=cpc_name)
        partition = cpc.partitions.find(name=partition_name)
    else:
        # Find the partition using the new operation
        filter_args = {'cpc-name': cpc_name, 'name': partition_name}
        partitions = client.consoles.console.list_permitted_partitions(
            filter_args=filter_args)
        try:
            partition = partitions[0]
        except IndexError:
            raise zhmcclient.NotFound(
                message=f"Could not find partition {partition_name!r} in "
                f"permitted partitions of CPC {cpc_name!r}")
    return partition


def add_messages(receiver, msg_queue):
    """
    Receive the OS message notifications in the specified receiver and
    put them to the specified messsage queue. The function returns when the
    receiver is exhausted (which happens when it is closed).
    """
    this_thread = threading.current_thread()
    LOGGER.debug("Message thread: Receiving messages")
    # pylint: disable=unused-variable
    for header, message in receiver.notifications():

        # Indicate we are ready for command execution
        this_thread.ready()

        for msg_info in message['os-messages']:
            msg_txt = msg_info['message-text']
            msg_txt = msg_txt.rstrip('\n')
            LOGGER.debug("Message thread: Got message: %r", msg_txt)
            msg_queue.put(msg_txt)
            if this_thread.need_to_stop():
                LOGGER.debug("Message thread: Stop requested")
                return

    LOGGER.warning("Message thread: Unexpected end of notification loop")


def perform_command(params):
    """
    Send a command to the OS console, and return the command output as a module
    result.

    This is done by setting up a notification receiver for OS console messages,
    that receives OS messages in a separate thread, while the OS console
    command is executed.

    The resulting messages are then examined to find the command itself, which
    determines the starting point for returning the messages.

    The end point is reached when there are no more OS messages coming in
    for some seconds.

    Raises:
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    hmc_host = params['hmc_host']
    hmc_auth = params['hmc_auth']
    cpc_name = params['cpc_name']
    partition_name = params['name']
    command = params['command']
    is_priority = params['is_priority']

    session, logoff = open_session(params)
    try:
        client = zhmcclient.Client(session)

        partition = find_partition(client, cpc_name, partition_name)

        LOGGER.debug("Opening message channel to partition %r", partition.name)
        topic = partition.open_os_message_channel(
            include_refresh_messages=False)

        receiver = zhmcclient.NotificationReceiver(
            topic, hmc_host, hmc_auth['userid'], hmc_auth['password'])

        try:

            LOGGER.debug("Starting message thread")
            msg_queue = queue.Queue()
            msg_thread = NotificationThread(
                target=add_messages, args=(receiver, msg_queue))
            msg_thread.start()

            readiness_timeout = 2
            LOGGER.debug("Waiting for message thread readiness (timeout: %d)",
                         readiness_timeout)
            msg_thread.wait_ready(timeout=readiness_timeout)

            LOGGER.debug("Executing command: %r", command)
            partition.send_os_command(command, is_priority)

            # Process the messages being received
            LOGGER.debug("Processing received messages")
            result = []
            command_upper = command.upper()
            command_found = False
            no_more_messages_timeout = 2
            while True:
                try:
                    msg = msg_queue.get(timeout=no_more_messages_timeout)
                except queue.Empty:
                    LOGGER.debug("Found no more messages for %d s",
                                 no_more_messages_timeout)
                    break

                if not command_found:
                    if command_upper in msg.upper():
                        LOGGER.debug("Found command in message: %r", msg)
                        result.append(msg)
                        command_found = True
                    continue

                result.append(msg)

        finally:
            LOGGER.debug("Closing receiver")
            receiver.close()

        return result

    finally:
        close_session(session, logoff)


def main():
    """Main function"""

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='raw'),
        hmc_auth=hmc_auth_parameter(),
        cpc_name=dict(required=True, type='str'),
        name=dict(required=True, type='str'),
        command=dict(required=True, type='str'),
        is_priority=dict(required=False, type='bool', default=False),
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

    changed = True
    try:

        result = perform_command(module.params)

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
        "Module exit (success): changed: %r, output: %r", changed, result)
    module.exit_json(changed=changed, output=result)


if __name__ == '__main__':
    main()
