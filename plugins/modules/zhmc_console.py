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
module: zhmc_console
version_added: "2.9.0"
short_description: Manage the HMC
description:
  - Get facts about the targeted HMC.
  - Upgrade the firmware of the targeted HMC.
author:
  - Andreas Maier (@andy-maier)
requirements:
  - "For C(state=facts), no specific task or object-access permissions are
     required."
  - "For C(state=upgrade), task permission to the 'Single Step Console
     Internal Code' task is required."
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
  state:
    description:
      - "The action to be performed on the HMC:"
      - "* C(facts): Returns facts about the HMC."
      - "* C(upgrade): Upgrades the firmware of the HMC and returns the new
         facts after the upgrade. If the HMC firmware is already at the
         requested bundle level, nothing is changed and the module succeeds."
    type: str
    choices: ['facts', 'upgrade']
    required: true
  bundle_level:
    description:
      - "Name of the bundle to be installed on the HMC (e.g. 'H71')"
      - "Required for C(state=upgrade)"
    type: str
    required: false
    default: null
  upgrade_timeout:
    description:
      - "Timeout in seconds for waiting for completion of upgrade (e.g. 3600)"
    type: int
    required: false
    default: 3600
  backup_location_type:
    description:
      - "Type of backup location for the HMC backup that is performed:"
      - "* 'ftp': The FTP server that was used for the last console backup as
         defined on the 'Configure Backup Settings' user interface task in the
         HMC GUI."
      - "* 'usb': The USB storage device mounted to the HMC."
      - "Optional for C(state=upgrade), default: 'usb'"
    type: str
    choices: ['ftp', 'usb']
    required: false
    default: 'usb'
  accept_firmware:
    description:
      - "Accept the previous bundle level before installing the new level."
      - "Optional for C(state=upgrade), default: True"
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

- name: Gather facts about the HMC
  zhmc_console:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    state: facts
  register: hmc1

- name: Upgrade the HMC firmware and return facts
  zhmc_console:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    state: upgrade
    bundle_level: "H71"
    upgrade_timeout: 3600
  register: hmc1
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
hmc:
  description: "The facts about the HMC."
  returned: success
  type: dict
  contains:
    name:
      description: "HMC name"
      type: str
    "{property}":
      description: "Additional properties of the Console object representing
        the targeted HMC, as described in the data model of the 'Console'
        object in the :term:`HMC API` book.
        Note that the set of properties has been extended over the past
        HMC versions, so you will get less properties on older HMC versions.
        The property names have hyphens (-) as described in that book."
      type: raw
    "api_version":
      description: "Additional facts from the 'Query API Version' operation."
      type: dict
      contains:
        "{property}":
          description: "The properties returned from the
            'Query API Version' operation, as described in the
            :term:`HMC API` book.
            Note that the set of properties has been extended over the past
            HMC versions, so you will get less properties on older HMC
            versions.
            The property names have hyphens (-) as described in that book."
          type: raw
  sample:
    {
        "name": "HMC1",
        "{property}": "... more Console properties ... ",
        "api_version": {
            "{property}": "... from Query API Version operation ... ",
        }
    }
"""

import logging  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402

from ..module_utils.common import log_init, open_session, close_session, \
    hmc_auth_parameter, Error, ParameterError, missing_required_lib, \
    common_fail_on_import_errors, parse_hmc_host  # noqa: E402

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
LOGGER_NAME = 'zhmc_console'

LOGGER = logging.getLogger(LOGGER_NAME)


def add_artificial_properties(console_properties, console):
    """
    Add artificial properties to the Console object properties.

    Upon return, the console_properties dict has been extended by
    these artificial properties:

    * 'api_version': Result of the "Query API Version" operation.
    """
    version_props = console.manager.client.query_api_version()
    console_properties['api_version'] = dict(version_props)


def facts(module):
    """
    Identify the target HMC and return facts about the target HMC and its
    child resources.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    session, logoff = open_session(module.params)
    try:
        client = zhmcclient.Client(session)
        console = client.consoles.console
        # The default exception handling is sufficient for the above.

        console.pull_full_properties()
        result = dict(console.properties)
        add_artificial_properties(result, console)

        return False, result

    finally:
        close_session(session, logoff)


def upgrade(module):
    """
    Upgrades the firmware on this HMC to a new bundle level.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    module.fail_on_missing_params(['bundle_level'])
    bundle_level = module.params['bundle_level']
    upgrade_timeout = module.params['upgrade_timeout']
    accept_firmware = module.params['accept_firmware']
    backup_location_type = module.params['backup_location_type']

    session, logoff = open_session(module.params)
    try:
        client = zhmcclient.Client(session)
        console = client.consoles.console
        # The default exception handling is sufficient for the above.

        ec_mcl = console.prop('ec-mcl-description')
        hmc_bundle_level = ec_mcl.get('bundle-level', None)
        if hmc_bundle_level is None:
            hmc_version = console.prop('version')
            raise ParameterError(
                "HMC version {v} does not support firmware upgrade through "
                "the Web Services API".format(v=hmc_version))

        changed = False

        if not module.check_mode:
            # This may restart the HMC, but zhmcclient will re-establish the
            # session.
            try:
                console.single_step_install(
                    bundle_level=bundle_level,
                    accept_firmware=accept_firmware,
                    backup_location_type=backup_location_type,
                    wait_for_completion=True,
                    operation_timeout=upgrade_timeout)
                changed = True
            except zhmcclient.HTTPError as exc:
                if exc.http_status == 400 and exc.reason == 356:
                    # HMC was already at that bundle level
                    pass
                else:
                    raise

        console.pull_full_properties()
        result = dict(console.properties)
        add_artificial_properties(result, console)

        return changed, result

    finally:
        close_session(session, logoff)


def perform_task(module):
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
        "facts": facts,
        "upgrade": upgrade,
    }
    return actions[module.params['state']](module)


def main():

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='raw'),
        hmc_auth=hmc_auth_parameter(),
        state=dict(required=True, type='str', choices=['facts', 'upgrade']),
        bundle_level=dict(required=False, type='str', default=None),
        upgrade_timeout=dict(required=False, type='int', default=3600),
        backup_location_type=dict(
            required=False, type='str', choices=['ftp', 'usb'], default='usb'),
        accept_firmware=dict(required=False, type='bool', default=True),
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

    module.params['hmc_host'] = parse_hmc_host(module.params['hmc_host'])

    _params = dict(module.params)
    del _params['hmc_auth']
    LOGGER.debug("Module entry: params: %r", _params)

    try:

        changed, result = perform_task(module)

    except (Error, zhmcclient.Error) as exc:
        # These exceptions are considered errors in the environment or in user
        # input. They have a proper message that stands on its own, so we
        # simply pass that message on and will not need a traceback.
        msg = "{0}: {1}".format(exc.__class__.__name__, exc)
        LOGGER.debug("Module exit (failure): msg: %r", msg)
        module.fail_json(msg=msg)
    # Other exceptions are considered module errors and are handled by Ansible
    # by showing the traceback.

    LOGGER.debug("Module exit (success): changed: %s, hmc: %r",
                 changed, result)
    module.exit_json(
        changed=changed, hmc=result)


if __name__ == '__main__':
    main()
