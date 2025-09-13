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
short_description: List LPARs (classic mode)
description:
  - List LPARs on a specific CPC (Z system) or on all managed CPCs.
  - CPCs in DPM mode are ignored (i.e. do not lead to a failure).
  - LPARs for which the user has no object access permission are ignored (i.e.
    do not lead to a failure).
  - On HMCs with version 2.14.0 or higher, the "List Permitted Logical
    Partitions" operation is used by this module. Otherwise, the managed CPCs
    are listed and then the LPARs on each desired CPC or CPCs are listed. This
    improves the execution time of the module on newer HMCs but does not affect
    the module result data.
author:
  - Andreas Maier (@andy-maier)
requirements:
  - "The HMC userid must have object-access permissions to these objects:
    Target LPArs, CPCs of target LPARs (only for z13 and older)."
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
      - "Name of the CPC for which the LPARs are to be listed."
      - "Default: All managed CPCs."
    type: str
    required: false
    default: null
  additional_properties:
    description:
      - List of additional properties to be returned for each LPAR, in
        addition to the default properties (see result description).
      - Mutually exclusive with O(full_properties).
      - The property names are specified with underscores instead of hyphens.
      - On HMCs with an API version below 4.10 (= HMC version 2.16.0 plus some
        post-GA updates), all properties of each LPAR will be returned if this
        parameter is specified, but you should not rely on that.
    type: list
    elements: str
    required: false
    default: []
  full_properties:
    description:
      - "If True, all properties of each LPAR will be returned.
        Default: False."
      - Mutually exclusive with O(additional_properties).
      - "Note: Setting this to True causes a loop of 'Get Logical Partition
        Properties' operations to be executed. It is preferable from a
        performance perspective to use the O(additional_properties) parameter
        instead."
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
      description: "SE version of the parent CPC of the LPAR"
      type: str
    status:
      description: The current status of the LPAR. For details, see the
        description of the 'status' property in the data model of the
        'Logical Partition' resource (see R(HMC API,HMC API)).
      type: str
    has_unacceptable_status:
      description: Indicates whether the current status of the LPAR is
        unacceptable, based on its 'acceptable-status' property.
      type: bool
    activation_mode:
      description: The activation mode of the LPAR. For details, see the
        description of the 'activation-mode' property in the data model of the
        'Logical Partition' resource (see R(HMC API,HMC API)).
      type: str
    "{additional_property}":
      description: Additional properties requested via O(full_properties) or
        O(additional_properties).
        The property names will have underscores instead of hyphens.
      type: raw
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
from ansible.module_utils.basic import AnsibleModule, \
    missing_required_lib  # noqa: E402

from ..module_utils.common import log_init, open_session, close_session, \
    hmc_auth_parameter, Error, ParameterError, \
    common_fail_on_import_errors, parse_hmc_host, blanked_params  # noqa: E402

try:
    import zhmcclient
    IMP_ZHMCCLIENT_ERR = None
except ImportError:
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

    cpc_name = params['cpc_name']
    additional_properties = \
        [p.replace('_', '-') for p in params['additional_properties']]
    full_properties = params['full_properties']

    if additional_properties and full_properties:
        raise ParameterError(
            "The 'additional_properties' and 'full_properties' module "
            "parameters are mutually exclusive but both are specified.")

    session, logoff = open_session(params)
    try:
        client = zhmcclient.Client(session)

        # The "List Permitted Logical Partitions" operation was added in HMC
        # version 2.14.0. The operation depends only on the HMC version and not
        # on the SE/CPC version, so it is supported e.g. for a 2.14 HMC managing
        # a z13 CPC.
        #
        # The "List Permitted Logical Partitions" operation supports the
        # 'additional-properties' query parameter starting with feature
        # 'secure-boot-with-certificates' (API version 4.10, HMC version 2.16
        # after initial GA).
        #
        # The "List Logical Partitions of a CPC" operation does not support an
        # 'additional-properties' query parameter as of HMC API version 4.10,
        # HMC version 2.16 after initial GA).
        av = client.query_api_version()
        hmc_version_info = [int(x) for x in av['hmc-version'].split('.')]
        api_version_info = [av['api-major-version'], av['api-minor-version']]
        if hmc_version_info < [2, 14, 0]:
            # Use the "List Logical Partitions of a CPC" operation.
            if additional_properties:
                # Get full properties instead of specific additional properties
                # since "List Logical Partitions of a CPC" does not support
                # additional-properties.
                additional_properties = None
                full_properties = True
            if full_properties:
                prop_str = "full properties"
            else:
                prop_str = "default properties"
            if cpc_name:
                LOGGER.debug("Listing LPARs of CPC %s (Find CPC, "
                             "then list LPARs with %s)",
                             cpc_name, prop_str)
                cpc = client.cpcs.find(name=cpc_name)
                lpars = cpc.lpars.list(full_properties=full_properties)
            else:
                LOGGER.debug("Listing LPARs of all managed CPCs (List "
                             "CPCs, then on each CPC list LPARs with %s)",
                             prop_str)
                cpcs = client.cpcs.list()
                lpars = []
                for cpc in cpcs:
                    _lpars = cpc.lpars.list(full_properties=full_properties)
                    lpars.extend(_lpars)
        else:
            # Use the "List Permitted Logical Partitions" operation.
            if additional_properties and api_version_info < [4, 10]:
                # Get full properties instead of specific additional properties
                # since "List Permitted Logical Partitions" does not support
                # additional-properties on these early 2.16 HMC versions.
                additional_properties = None
                full_properties = True
            if full_properties:
                prop_str = "full properties"
            elif additional_properties:
                prop_str = "additional properties"
            else:
                prop_str = "default properties"
            if cpc_name:
                LOGGER.debug("Listing LPARs of CPC %s "
                             "(List permitted LPARs with %s)",
                             cpc_name, prop_str)
                filter_args = {'cpc-name': cpc_name}
            else:
                LOGGER.debug("Listing LPARs of all managed CPCs "
                             "(List permitted LPARs with %s)",
                             prop_str)
                filter_args = None
            lpars = client.consoles.console.list_permitted_lpars(
                filter_args=filter_args,
                additional_properties=additional_properties,
                full_properties=full_properties)
        # The default exception handling is sufficient for the above.

        se_versions = {}
        lpar_list = []
        for lpar in lpars:
            # se-version has been added to the result of List Permitted
            # LPARs in HMC/SE 2.14.1. Before that, it triggers the
            # retrieval of CPC properties.
            parent_cpc = lpar.manager.cpc
            try:
                se_version = se_versions[parent_cpc.name]
            except KeyError:
                try:
                    se_version = lpar.properties['se-version']
                except KeyError:
                    se_version = parent_cpc.get_property('se-version')
                se_versions[parent_cpc.name] = se_version

            lpar_properties = {
                "cpc_name": parent_cpc.name,
                "se_version": se_version,
            }
            for pname_hmc, pvalue in lpar.properties.items():
                pname = pname_hmc.replace('-', '_')
                lpar_properties[pname] = pvalue

            lpar_list.append(lpar_properties)

        return lpar_list

    finally:
        close_session(session, logoff)


def main():
    """Main function"""

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='raw'),
        hmc_auth=hmc_auth_parameter(),
        cpc_name=dict(required=False, type='str', default=None),
        additional_properties=dict(
            required=False, type='list', elements='str', default=[]),
        full_properties=dict(required=False, type='bool', default=False),
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

    LOGGER.debug("Module exit (success): changed: %s, lpars: %r",
                 changed, result_list)
    module.exit_json(changed=changed, lpars=result_list)


if __name__ == '__main__':
    main()
