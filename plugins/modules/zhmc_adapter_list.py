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
module: zhmc_adapter_list
version_added: "2.9.0"
short_description: List adapters
description:
  - List adapters on a specific CPC (Z system) or on all managed CPCs.
  - CPCs in classic mode are ignored (i.e. do not lead to a failure).
  - Adapters for which the user has no object access permission are ignored
    (i.e. do not lead to a failure).
  - On HMCs with version 2.16.0 or higher, the "List Permitted Adapters"
    operation is used by this module. Otherwise, the managed CPCs are listed
    and then the adapters on each desired CPC or CPCs are listed. This improves
    the execution time of the module on newer HMCs but does not affect the
    module result data.
seealso:
  - module: zhmc_adapter
author:
  - Andreas Maier (@andy-maier)
requirements:
  - "The HMC userid must have object-access permissions to these objects:
    Target adapters, CPCs of target adapters (CPC access is only needed for
    HMC version 2.15 and older)."
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
  cpc_name:
    description:
      - "Name of the CPC for which the adapters are to be listed."
      - "Default: All managed CPCs."
    type: str
    required: false
    default: null
  name:
    description:
      - Regular expression pattern for the adapter name to filter the result
        list to matching adapters.
    type: str
    required: false
    default: null
  adapter_id:
    description:
      - Regular expression pattern for the adapter ID (PCHID) ('adapter-id'
        property) to filter the result list to matching adapters.
    type: str
    required: false
    default: null
  adapter_family:
    description:
      - Adapter family ('adapter-family' property) to filter the result list
        to adapters with that family.
    type: str
    required: false
    default: null
  type:
    description:
      - Adapter type ('type' property) to filter the result list
        to adapters with that type.
    type: str
    required: false
    default: null
  status:
    description:
      - Adapter status ('status' property) to filter the result list
        to adapters with that status.
    type: str
    required: false
    default: null
  additional_properties:
    description:
      - List of additional properties to be returned for each adapter, in
        addition to the default properties (see result description).
      - Mutually exclusive with C(full_properties).
      - The property names are specified with underscores instead of hyphens.
      - On HMCs with an API version below 4.10 (= HMC version 2.16.0 with some
        post-GA updates), all properties of each adapter will be returned if
        this parameter is specified, but you should not rely on that.
    type: list
    elements: str
    required: false
    default: []
  full_properties:
    description:
      - "If True, all properties of each adapter will be returned.
        Default: False."
      - Mutually exclusive with C(additional_properties).
      - "Note: Setting this to True causes a loop of 'Get Adapter Properties'
        operations to be executed. It is preferable from a performance
        perspective to use the C(additional_properties) parameter instead."
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

- name: List all permitted adapters on all managed CPCs
  zhmc_adapter_list:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
  register: adapter_list

- name: List all permitted adapters on a CPC
  zhmc_adapter_list:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: CPCA
  register: adapter_list

- name: List the permitted FICON adapters on a CPC
  zhmc_adapter_list:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: CPCA
    adapter_family: "ficon"
  register: adapter_list
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
adapters:
  description: The list of adapters, with a subset of their properties.
    For details on the properties, see the data model of the 'Adapter' resource
    (see :term:`HMC API`)
  returned: success
  type: list
  elements: dict
  contains:
    name:
      description: "Adapter name"
      type: str
    cpc_name:
      description: "Name of the parent CPC of the adapter"
      type: str
    adapter_id:
      description: "Adapter ID (PCHID) of the adapter ('adapter-id' property)"
      type: str
    adapter_family:
      description: "Family of the adapter ('adapter-family' property)"
      type: str
    type:
      description: "Type of the adapter ('type' property)"
      type: str
    status:
      description: "The current status of the adapter ('status' property)"
      type: str
    "{additional_property}":
      description: Additional properties requested via C(full_properties) or
        C(additional_properties).
        The property names will have underscores instead of hyphens.
      type: raw
  sample:
    [
        {
            "name": "adapter1",
            "cpc_name": "CPC1",
            "adapter_id": "10c",
            "adapter_family": "osa",
            "type": "osd",
            "status": "active",
        }
    ]
"""

import logging  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402

from ..module_utils.common import log_init, open_session, close_session, \
    hmc_auth_parameter, Error, ParameterError, \
    missing_required_lib, parse_hmc_host  # noqa: E402

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
LOGGER_NAME = 'zhmc_adapter_list'

LOGGER = logging.getLogger(LOGGER_NAME)


def perform_list(params):
    """
    List the adapters and return a subset of properties.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    cpc_name = params['cpc_name']
    name = params['name']
    adapter_id = params['adapter_id']
    adapter_family = params['adapter_family']
    type = params['type']
    status = params['status']
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
        console = client.consoles.console

        filter_args = {}
        if name is not None:
            filter_args['name'] = name
        if adapter_id is not None:
            filter_args['adapter-id'] = adapter_id
        if adapter_family is not None:
            filter_args['adapter-family'] = adapter_family
        if type is not None:
            filter_args['type'] = type
        if status is not None:
            filter_args['status'] = status

        # The "List Permitted Adapters" operation was added in HMC API version
        # 4.1 (HMC version 2.16.0 initial GA). The operation depends only on
        # the HMC version and not on the SE/CPC version, so it is supported
        # e.g. for a 2.16 HMC managing a z15 CPC.
        #
        # The "List Permitted Adapters" operation supports the
        # 'additional-properties' query parameter starting with feature
        # 'adapter-network-information' (HMC API version 4.10, HMC version
        # 2.16.0 after initial GA).
        #
        # The "List Adapters of a CPC" operation supports the
        # 'additional-properties' query parameter starting with HMC API version
        # 4.1 (HMC version 2.16 at initial GA).
        av = client.query_api_version()
        hmc_version_info = [int(x) for x in av['hmc-version'].split('.')]
        api_version_info = [av['api-major-version'], av['api-minor-version']]
        if hmc_version_info < [2, 16, 0]:
            # Use the "List Adapters of a CPC" operation.
            if additional_properties:
                # Get full properties instead of specific additional properties
                # since "List Adapters of a CPC" does not support
                # additional-properties on these HMC versions.
                full_properties = True
            if full_properties:
                prop_str = "full properties"
            else:
                prop_str = "default properties"
            if cpc_name:
                LOGGER.debug("Listing adapters of CPC %s (Find CPC, "
                             "then list adapters with %s)",
                             cpc_name, prop_str)
                cpc = client.cpcs.find(name=cpc_name)
                adapters = cpc.adapters.list(
                    filter_args=filter_args,
                    full_properties=full_properties)
            else:
                LOGGER.debug("Listing adapters of all managed CPCs (List CPCs, "
                             "then on each CPC list adapters with %s)",
                             prop_str)
                cpcs = client.cpcs.list()
                adapters = []
                for cpc in cpcs:
                    _adapters = cpc.adapters.list(
                        filter_args=filter_args,
                        full_properties=full_properties)
                    adapters.extend(_adapters)
        else:
            # Use the "List Permitted Adapters" operation.
            if additional_properties and api_version_info < [4, 10]:
                # Get full properties instead of specific additional properties
                # since "List Adapters of a CPC" does not support
                # additional-properties on these early 2.16 API versions.
                additional_properties = None
                full_properties = True
            if full_properties:
                prop_str = "full properties"
            elif additional_properties:
                prop_str = "additional properties"
            else:
                prop_str = "default properties"
            if cpc_name:
                LOGGER.debug("Listing adapters of CPC %s "
                             "(List permitted adapters with %s)",
                             cpc_name, prop_str)
                filter_args['cpc-name'] = cpc_name
            else:
                LOGGER.debug("Listing adapters of all managed CPCs "
                             "(List permitted adapters with %s)",
                             prop_str)
            adapters = console.list_permitted_adapters(
                filter_args=filter_args,
                additional_properties=additional_properties,
                full_properties=full_properties)
        # The default exception handling is sufficient for the above.

        adapter_list = []
        for adapter in adapters:
            parent_cpc = adapter.manager.cpc

            adapter_properties = {
                "cpc_name": parent_cpc.name,
            }
            for pname_hmc, pvalue in adapter.properties.items():
                pname = pname_hmc.replace('-', '_')
                adapter_properties[pname] = pvalue

            adapter_list.append(adapter_properties)

        return adapter_list

    finally:
        close_session(session, logoff)


def main():

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='raw'),
        hmc_auth=hmc_auth_parameter(),
        cpc_name=dict(required=False, type='str', default=None),
        name=dict(required=False, type='str', default=None),
        adapter_id=dict(required=False, type='str', default=None),
        adapter_family=dict(required=False, type='str', default=None),
        type=dict(required=False, type='str', default=None),
        status=dict(required=False, type='str', default=None),
        additional_properties=dict(
            required=False, type='list', elements='str', default=[]),
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

    log_file = module.params['log_file']
    log_init(LOGGER_NAME, log_file)

    module.params['hmc_host'] = parse_hmc_host(module.params['hmc_host'])

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
        msg = f"{exc.__class__.__name__}: {exc}"
        LOGGER.debug("Module exit (failure): msg: %r", msg)
        module.fail_json(msg=msg)
    # Other exceptions are considered module errors and are handled by Ansible
    # by showing the traceback.

    LOGGER.debug("Module exit (success): changed: %s, adapters: %r",
                 changed, result_list)
    module.exit_json(changed=changed, adapters=result_list)


if __name__ == '__main__':
    main()
