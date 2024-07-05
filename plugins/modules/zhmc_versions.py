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
module: zhmc_versions
version_added: "2.15.0"
short_description: Retrieve HMC/CPC version and feature facts
description:
  - Retrieve version and feature facts for the targeted HMC and its managed
    CPCs.
author:
  - Andreas Maier (@andy-maier)
requirements:
  - "No specific task or object-access permissions are required."
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
  cpc_names:
    description:
      - "List of CPC names for which facts are to be included in the result."
      - "Default: All managed CPCs."
    type: list
    elements: str
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

- name: Retrieve version and feature information for HMC and all managed CPCs
  zhmc_versions:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
  register: hmc1

- name: Retrieve version and feature information for HMC only
  zhmc_versions:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_names: []
  register: hmc1
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
versions:
  description: "The version information."
  returned: success
  type: dict
  contains:
    hmc_name:
      description: "HMC name"
      type: str
    hmc_version:
      description: "HMC version, as a string."
      type: str
    hmc_version_info:
      description: "HMC version, as a list of integers."
      type: list
      elements: int
    hmc_api_version:
      description: "HMC API version, as a string."
      type: str
    hmc_api_version_info:
      description: "HMC API version, as a list of integers."
      type: list
      elements: int
    hmc_api_features:
      description: "The available HMC API features."
      type: list
      elements: str
    cpcs:
      description: "Version data for the requested CPCs of the HMC."
      type: list
      elements: dict
      contains:
        name:
          description: "CPC name."
          type: str
        status:
          description: "The current status of the CPC. For details, see the
            description of the 'status' property in the data model of the 'CPC'
            resource (see R(HMC API,HMC API))."
          type: str
        has_unacceptable_status:
          description: "Indicates whether the current status of the CPC is
            unacceptable, based on its 'acceptable-status' property."
          type: bool
        dpm_enabled:
          description: "Indicates wehether the CPC is in DPM mode (true) or in
            classic mode (false)."
          type: bool
        se_version:
          description: "SE version of the CPC, as a string."
          type: str
        se_version_info:
          description: "SE version of the CPC, as a list of integers."
          type: list
          elements: int
        cpc_api_features:
          description: "The available CPC API features."
          type: list
          elements: str

  sample:
    {
        "hmc_name": "HMC1",
        "hmc_version": "2.16.0",
        "hmc_version_info": [2, 16, 0],
        "hmc_api_version": "4.10",
        "hmc_api_version_info": [4, 10],
        "hmc_api_features": [
            "adapter-network-information",
            "..."
        ],
        "cpcs": [
            {
                "name": "CPC1",
                "status": "active",
                "has_unacceptable_status": false,
                "dpm_enabled": true,
                "se_version": "2.16.0",
                "se_version_info": [2, 16, 0],
                "cpc_api_features": [
                    "adapter-network-information",
                    "..."
                ]
            }
        ]
    }
"""

import logging  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402

from ..module_utils.common import log_init, open_session, close_session, \
    hmc_auth_parameter, Error, missing_required_lib, \
    common_fail_on_import_errors, parse_hmc_host  # noqa: E402

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
LOGGER_NAME = 'zhmc_versions'

LOGGER = logging.getLogger(LOGGER_NAME)


def get_versions(module):
    """
    Retrieve the data and return a dict with the results of this module.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    cpc_names = module.params['cpc_names']

    versions = {}
    session, logoff = open_session(module.params)
    try:

        client = zhmcclient.Client(session)
        console = client.consoles.console

        # Get HMC version info
        vers = client.query_api_version()
        versions['hmc_name'] = vers['hmc-name']
        hmc_version_str = vers['hmc-version']
        hmc_version_info = list(map(int, hmc_version_str.split('.')))
        versions['hmc_version'] = hmc_version_str
        versions['hmc_version_info'] = hmc_version_info
        api_version_info = [
            vers['api-major-version'],
            vers['api-minor-version']]
        api_version_str = '{}.{}'.format(*api_version_info)
        versions['hmc_api_version'] = api_version_str
        versions['hmc_api_version_info'] = api_version_info

        # Get HMC API features
        versions['hmc_api_features'] = console.list_api_features()

        # List managed CPCs
        cpcs = client.cpcs.list()
        versions['cpcs'] = []
        for cpc in cpcs:

            # Filter on the requested CPCs
            if cpc_names is not None and cpc.name not in cpc_names:
                continue

            cpc_vers = {}

            # Get CPC data from list result
            cpc_vers['name'] = cpc.prop('name')
            cpc_vers['status'] = cpc.prop('status')
            cpc_vers['has_unacceptable_status'] = \
                cpc.prop('has-unacceptable-status')
            cpc_vers['dpm_enabled'] = cpc.prop('dpm-enabled')
            se_version_str = cpc.prop('se-version')
            se_version_info = list(map(int, se_version_str.split('.')))
            cpc_vers['se_version'] = se_version_str
            cpc_vers['se_version_info'] = se_version_info

            # Get CPC API features
            cpc_vers['cpc_api_features'] = cpc.list_api_features()

            versions['cpcs'].append(cpc_vers)

        return False, versions

    finally:
        close_session(session, logoff)


def main():
    """Main function"""

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='raw'),
        hmc_auth=hmc_auth_parameter(),
        cpc_names=dict(required=False, type='list', elements='str',
                       default=None),
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

    _params = dict(module.params)
    del _params['hmc_auth']
    LOGGER.debug("Module entry: params: %r", _params)

    try:

        changed, versions = get_versions(module)

    except (Error, zhmcclient.Error) as exc:
        # These exceptions are considered errors in the environment or in user
        # input. They have a proper message that stands on its own, so we
        # simply pass that message on and will not need a traceback.
        msg = f"{exc.__class__.__name__}: {exc}"
        LOGGER.debug("Module exit (failure): msg: %r", msg)
        module.fail_json(msg=msg)
    # Other exceptions are considered module errors and are handled by Ansible
    # by showing the traceback.

    LOGGER.debug("Module exit (success): changed: %s, versions: %r",
                 changed, versions)
    module.exit_json(
        changed=changed, versions=versions)


if __name__ == '__main__':
    main()
