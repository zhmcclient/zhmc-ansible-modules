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
module: zhmc_storage_volume_list
version_added: "2.9.0"
short_description: List storage volumes of a storage group (DPM mode)
description:
  - List storage volumes of a specific storage group.
  - The returned storage volumes can be filtered by name, fulfillment state,
    minimum and maximum size, and usage (boot/data).
  - CPCs in classic mode are ignored (i.e. do not lead to a failure).
seealso:
  - module: ibm.ibm_zhmc.zhmc_storage_volume
author:
  - Andreas Maier (@andy-maier)
requirements:
  - Requires HMC version 2.14 or later (to have the
    "dpm-storage-management" firmware feature) and must be in the Dynamic
    Partition Manager (DPM) operational mode.
  - "The HMC userid must have object-access permissions to these objects:
    Target storage group."
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
  storage_group_name:
    description:
      - Name of the storage group whose storage volumes are to be listed.
    type: str
    required: true
  name:
    description:
      - Filter to limit returned storage volumes to those whose name matches the
        specified regular expression pattern.
      - If None/null, no such filtering happens.
    type: str
    required: false
    default: null
  fulfillment_state:
    description:
      - Filter to limit returned storage volumes to those that have the
        specified fulfillment state.
      - If None/null, no such filtering happens.
      - For possible values, see the description of property "fulfillment-state"
        in the data model of the Storage Volume object in the R(HMC API,HMC API)
        book.
    type: str
    required: false
    default: null
  maximum_size:
    description:
      - Filter to limit returned storage volumes to those with a size that is
        less than or equal to the specified maximum size (in GiB).
      - If None/null, no such filtering happens.
    type: int
    required: false
    default: null
  minimum_size:
    description:
      - Filter to limit returned storage volumes to those with a size that is
        greater than or equal to the specified minimum size (in GiB).
      - If None/null, no such filtering happens.
    type: int
    required: false
    default: null
  usage:
    description:
      - Filter to limit returned storage volumes to those with the specified
        usage (boot/data).
      - If None/null, no such filtering happens.
    type: str
    choices: ['boot', 'data']
    required: false
    default: null
  additional_properties:
    description:
      - List of additional properties to be returned for each storage volume,
        in addition to the default properties (see result description).
      - Mutually exclusive with O(full_properties).
      - The property names are specified with underscores instead of hyphens.
      - Not all properties defined in the data model are supported. For
        supported properties, see the description of query parameter
        "additional-properties" in the "List Storage Volumes of a Storage Group"
        operation in the R(HMC API,HMC API) book.
    type: list
    elements: str
    required: false
    default: []
  full_properties:
    description:
      - "If True, all properties of each storage volume will be returned.
        Default: False."
      - Mutually exclusive with O(additional_properties).
      - "Note: Setting this to True causes a loop of 'Get Storage Group
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

- name: List the volumes of storage group SG1
  zhmc_storage_volume_list:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    storage_group_name: SG1
  register: storage_volume_list

- name: List the data volumes of storage group SG1
  zhmc_storage_volume_list:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    storage_group_name: SG1
    usage: data
  register: storage_volume_list
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
storage_volumes:
  description: The list of storage volumes, with a subset of their properties.
  returned: success
  type: list
  elements: dict
  contains:
    name:
      description: Storage volume name
      type: str
    element_uri:
      description: Canonical URI of the storage volume object
      type: str
    fulfillment_state:
      description: The current fulfillment state of the storage volume.
        For possible values, see the description of property "fulfillment-state"
        in the data model of the Storage Group object in the R(HMC API,HMC API)
        book.
      type: str
    size:
      description: Size of the volume, in GiB.
      type: float
    usage:
      description: Usage of the volume (boot/data).
      type: str
      choices: ['boot', 'data']
    "{additional_property}":
      description: Additional properties requested via O(full_properties).
        The property names will have underscores instead of hyphens.
      type: raw
  sample:
    [
        {
            "name": "storage_volume1",
            "element_uri": "/api/storage-groups/..../storage-volumes/....",
            "fulfillment_state": "complete",
            "size": 500.0,
            "usage": "boot"
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
LOGGER_NAME = 'zhmc_storage_volume_list'

LOGGER = logging.getLogger(LOGGER_NAME)


def perform_list(params):
    """
    List the storage volumes and return a subset of properties.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    storage_group_name = params['storage_group_name']
    name = params['name']
    fulfillment_state = params['fulfillment_state']
    maximum_size = params['maximum_size']
    minimum_size = params['minimum_size']
    usage = params['usage']
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

        storage_group = console.storage_groups.find_by_name(storage_group_name)
        # The default exception handling is sufficient for the above.

        filter_args = {}
        if name:
            filter_args['name'] = name
        if fulfillment_state:
            filter_args['fulfillment-state'] = fulfillment_state
        if maximum_size:
            filter_args['maximum-size'] = maximum_size
        if minimum_size:
            filter_args['minimum-size'] = minimum_size
        if usage:
            filter_args['usage'] = usage

        # The additional-properties query parameter was added in HMC 2.17.0.
        storage_volumes = storage_group.storage_volumes.list(
            filter_args=filter_args,
            full_properties=full_properties,
            additional_properties=additional_properties)
        # The default exception handling is sufficient for the above.

        storage_volume_list = []
        for storage_volume in storage_volumes:
            storage_volume_properties = {}
            for pname_hmc, pvalue in storage_volume.properties.items():
                pname = pname_hmc.replace('-', '_')
                storage_volume_properties[pname] = pvalue

            storage_volume_list.append(storage_volume_properties)

        return storage_volume_list

    finally:
        close_session(session, logoff)


def main():
    """Main function"""

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='raw'),
        hmc_auth=hmc_auth_parameter(),
        storage_group_name=dict(required=True, type='str'),
        name=dict(required=False, type='str', default=None),
        fulfillment_state=dict(required=False, type='str', default=None),
        maximum_size=dict(required=False, type='int', default=None),
        minimum_size=dict(required=False, type='int', default=None),
        usage=dict(required=False, type='str', choices=['boot', 'data'],
                   default=None),
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

    LOGGER.debug("Module exit (success): changed: %s, storage_volumes: %r",
                 changed, result_list)
    module.exit_json(changed=changed, storage_volumes=result_list)


if __name__ == '__main__':
    main()
