#!/usr/bin/python
# Copyright 2022 IBM Corp. All Rights Reserved.
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
module: zhmc_lpar_list
version_added: "2.9.0"
short_description: List LPARs
description:
  - List permitted LPARs on a CPC (Z system) or on all managed CPCs.
  - CPCs in DPM mode are ignored (i.e. do not lead to a failure).
  - LPARs for which the user has no object access permission are ignored (i.e.
    do not lead to a failure).
author:
  - Andreas Maier (@andy-maier)
requirements:
  - Access to the WS API of the HMC (see :term:`HMC API`).
  - The HMC version must be 2.14.0 or higher.
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
        type: str
        required: true
      password:
        description:
          - The password for authenticating with the HMC.
        type: str
        required: true
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
      - "Name of the CPC for which the LPARs are to be listed."
      - "Default: All managed CPCs."
    type: str
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
    required: false
    type: raw
    default: null
"""

EXAMPLES = """
---
# Note: The following examples assume that some variables named 'my_*' are set.

- name: List the permitted LPARs on all managed CPCs
  zhmc_lpar_list:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
  register: lpar_list

- name: List the permitted LPARs on a CPC
  zhmc_lpar_list:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: CPCA
  register: lpar_list

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
lpars:
  description: The list of permitted LPARs, with a subset of their properties.
  returned: success
  type: list
  elements: dict
  contains:
    name:
      description: "LPAR name"
      type: str
    cpc_name:
      description: "Name of the parent CPC of the LPAR"
      type: str
    se_version:
      description: "SE version of the parent CPC of the LPAR (since HMC/SE
        2.14.1, otherwise None)"
      type: str
    status:
      description: The current status of the LPAR. For details, see the
        description of the 'status' property in the data model of the
        'Logical Partition' resource (see :term:`HMC API`).
      type: str
    has_unacceptable_status:
      description: Indicates whether the current status of the LPAR is
        unacceptable, based on its 'acceptable-status' property.
      type: bool
    activation_mode:
      description: The activation mode of the LPAR. For details, see the
        description of the 'activation-mode' property in the data model of the
        'Logical Partition' resource (see :term:`HMC API`).
      type: str
  sample:
    [
        {
            "name": "LPAR1",
            "cpc_name": "CPC1",
            "se_version": "2.15.0",
            "status": "active",
            "has_unacceptable_status": False,
            "activation_mode": 'linux'
        }
    ]
"""

import logging  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402

from ..module_utils.common import log_init, Error, VersionError, \
    get_hmc_auth, get_session, missing_required_lib  # noqa: E402

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
LOGGER_NAME = 'zhmc_lpar_list'

LOGGER = logging.getLogger(LOGGER_NAME)


def perform_list(params):
    """
    List the LPARs and return a subset of properties.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    host = params['hmc_host']
    userid, password, ca_certs, verify = get_hmc_auth(params['hmc_auth'])
    cpc_name = params.get('cpc_name', None)
    _faked_session = params.get('_faked_session', None)  # No default specified

    session = get_session(
        _faked_session, host, userid, password, ca_certs, verify)
    try:
        client = zhmcclient.Client(session)

        # Check minimum required HMC version. The "List Permitted Logical
        # Partitions" operation used by this module was added in HMC 2.14.0.
        hmc_version = client.query_api_version()['hmc-version']
        hmc_version_info = [int(x) for x in hmc_version.split('.')]
        if hmc_version_info < [2, 14, 0]:
            raise VersionError(
                "The HMC version is {0}, but the minimum required version "
                "for the zhmc_lpar_list module is 2.14.0".
                format(hmc_version))

        lpar_list = []

        if cpc_name:
            LOGGER.debug("Listing permitted LPARs of CPC %s", cpc_name)
            filter_args = {'cpc-name': cpc_name}
        else:
            LOGGER.debug("Listing permitted LPARs of all managed CPCs")
            filter_args = None
        lpars = client.consoles.console.list_permitted_lpars(
            filter_args=filter_args)
        # The default exception handling is sufficient for the above.

        for lpar in lpars:
            # se-version has been added to the result of List Permitted
            # LPARs in HMC/SE 2.14.1. We want to get it if present, without
            # triggering a full pull of LPAR properties.
            parent_cpc = lpar.manager.cpc
            if 'se-version' in parent_cpc.properties:
                se_version = parent_cpc.get_property('se-version')
            else:
                se_version = None
            lpar_properties = {
                "name": lpar.name,
                "cpc_name": parent_cpc.name,
                "se_version": se_version,
                "status": lpar.get_property('status'),
                "has_unacceptable_status": lpar.get_property(
                    'has-unacceptable-status'),
                "activation_mode": lpar.get_property('activation-mode'),
            }
            lpar_list.append(lpar_properties)

        return lpar_list

    finally:
        session.logoff()


def main():

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='str'),
        hmc_auth=dict(
            required=True,
            type='dict',
            options=dict(
                userid=dict(required=True, type='str'),
                password=dict(required=True, type='str', no_log=True),
                ca_certs=dict(required=False, type='str', default=None),
                verify=dict(required=False, type='bool', default=True),
            ),
        ),
        cpc_name=dict(required=False, type='str', default=None),
        log_file=dict(required=False, type='str', default=None),
        _faked_session=dict(required=False, type='raw'),
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

    LOGGER.debug("Module exit (success): changed: %s, result: %r",
                 changed, result_list)
    module.exit_json(changed=changed, lpars=result_list)


if __name__ == '__main__':
    main()