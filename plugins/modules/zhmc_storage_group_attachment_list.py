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
module: zhmc_storage_group_attachment_list
version_added: "2.9.0"
short_description: List the partitions attached to a storage group (DPM mode)
description:
  - List the partitions attached to a storage group.
  - The returned partitions can be filtered by name and status.
seealso:
  - module: ibm.ibm_zhmc.zhmc_storage_group_attachment
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
  cpc_name:
    description:
      - The name of the CPC associated with the target storage group.
    type: str
    required: true
  name:
    description:
      - The name of the target storage group.
    type: str
    required: true
  partition_name:
    description:
      - Filter to limit returned partitions to those whose name matches the
        specified regular expression pattern.
      - If None/null, no such filtering happens.
    type: str
    required: false
    default: null
  partition_status:
    description:
      - Filter to limit returned partitions to those that have the
        specified status.
      - If None/null, no such filtering happens.
      - For possible values, see the description of property "status"
        in the data model of the Partition object in the R(HMC API,HMC API)
        book.
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
    type: raw
    required: false
    default: null
"""

EXAMPLES = """
---
# Note: The following examples assume that some variables named 'my_*' are set.

- name: List the partitions attached to a storage group
  zhmc_storage_group_attachment_list:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc }}"
    name: "{{ my_name }}"
  register: storage_group_attachment_list
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
partitions:
  description: The list of attached partitions, with a subset of their properties.
  returned: success
  type: list
  elements: dict
  contains:
    name:
      description: Partition name
      type: str
    object_uri:
      description: Canonical URI of the Partition
      type: str
    cpc_uri:
      description: Canonical URI of the CPC of the partition
      type: str
    cpc_name:
      description: Name of the CPC of the partition
      type: str
    status:
      description: The status of the partition.
        For possible values, see the description of property "status"
        in the data model of the Partition object in the R(HMC API,HMC API)
        book.
      type: str
  sample:
    [
        {
            "name": "partition1",
            "object_uri": "/api/partitions/....",
            "cpc_uri": "/api/cpcs/....",
            "cpc_name": "CPC1",
            "status": "active"
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
LOGGER_NAME = 'zhmc_storage_group_attachment_list'

LOGGER = logging.getLogger(LOGGER_NAME)


def perform_list(params):
    """
    List the attached partitions and return a subset of properties.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    name = params['name']
    cpc_name = params['cpc_name']
    partition_name = params['partition_name']
    partition_status = params['partition_status']

    session, logoff = open_session(params)
    try:
        # The default exception handling is sufficient for this code
        client = zhmcclient.Client(session)
        console = client.consoles.console
        cpc = client.cpcs.find(name=cpc_name)

        filter = {'name': name, 'cpc-uri': cpc.uri}
        storage_groups = console.storage_groups.list(filter_args=filter)

        if not storage_groups:
            raise ParameterError(
                f"Storage group {name!r} associated with CPC {cpc.name!r} "
                f"not found.")

        # Since SG names are unique on each CPC, we should now have one SG
        storage_group = storage_groups[0]

        attached_partitions = storage_group.list_attached_partitions(
            name=partition_name, status=partition_status)

        partition_list = []
        for part in attached_partitions:
            part_properties = {
                "cpc_name": cpc_name,
            }
            for pname_hmc, pvalue in part.properties.items():
                pname = pname_hmc.replace('-', '_')
                part_properties[pname] = pvalue

            partition_list.append(part_properties)

        return partition_list

    finally:
        close_session(session, logoff)


def main():
    """Main function"""

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='raw'),
        hmc_auth=hmc_auth_parameter(),
        name=dict(required=True, type='str'),
        cpc_name=dict(required=True, type='str'),
        partition_name=dict(required=False, type='str', default=None),
        partition_status=dict(required=False, type='str', default=None),
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

    LOGGER.debug("Module exit (success): changed: %s, partitions: %r",
                 changed, result_list)
    module.exit_json(changed=changed, partitions=result_list)


if __name__ == '__main__':
    main()
