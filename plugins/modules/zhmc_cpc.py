#!/usr/bin/python
# Copyright 2018,2020 IBM Corp. All Rights Reserved.
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
module: zhmc_cpc
version_added: "2.9.0"
short_description: Manage a CPC
description:
  - Deactivate/Stop a CPC (Z system).
  - Activate/Start a CPC and update its properties.
  - Gather facts about a CPC, and for DPM operational mode, including its
    adapters, partitions and storage groups.
  - Update the properties of a CPC.
  - Upgrade the SE firmware of a CPC.
author:
  - Andreas Maier (@andy-maier)
  - Andreas Scheuring (@scheuran)
requirements:
  - "The HMC userid must have these task permissions:
    'CPC Details'. For CPCs in DMP mode: 'Start', 'Stop'. For CPCs in classic
    mode: 'Activate', 'Deactivate'."
  - "The HMC userid must have object-access permissions to these objects:
    Target CPCs. For CPCs in DMP mode: Adapters, partitions, storage groups of
    target CPCs. For CPCs in classic mode: LPARs, activation profiles of
    target CPCs."
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
  name:
    description:
      - The name of the target CPC.
    type: str
    required: true
  state:
    description:
      - "The desired state for the CPC. All states are fully idempotent
         within the limits of the properties that can be changed:"
      - "* V(inactive): Ensures the CPC is inactive."
      - "* V(active): Ensures the CPC is active and then ensures that the CPC
         has the specified properties. The operational mode of the CPC cannot
         be changed."
      - "* V(set): Ensures that the CPC has the specified properties."
      - "* V(facts): Returns the CPC properties including its child resources."
      - "* V(upgrade): Upgrades the firmware of the SE of the CPC and returns
         the new facts after the upgrade. If the SE firmware is already at the
         requested bundle level, nothing is changed and the module succeeds."
    type: str
    choices: ['inactive', 'active', 'set', 'facts', 'upgrade']
    required: true
  select_properties:
    description:
      - "Limits the returned properties of the CPC to those specified in this
         parameter plus those specified in the O(properties) parameter."
      - "The properties can be specified with underscores or hyphens in their
         names."
      - "Null indicates not to limit the returned properties in this way."
      - "This parameter is ignored for O(state) values that cause no properties
         to be returned."
      - "The returned child resources (adapters, partitions, storage groups)
         cannot be excluded using this parameter."
      - "The specified properties are passed to the 'Get CPC Properties' HMC
         operation using the 'properties' query parameter and save time for
         the HMC to pull together all properties."
    type: list
    elements: str
    required: false
    default: null
  activation_profile_name:
    description:
      - "The name of the reset activation profile to be used when activating the
         CPC in the classic operational mode, for O(state=active).
         This parameter is ignored when the CPC is in classic mode and was
         already active, and when the CPC is in DPM mode."
      - "Default: The reset activation profile specified in the
         'next-activation-profile-name' property of the CPC."
      - "This parameter is not allowed for the other O(state) values."
    type: str
    required: false
    default: null
  properties:
    description:
      - "Only for O(state=set) and O(state=active): New values for the
         properties of the CPC.
         Properties omitted in this dictionary will remain unchanged.
         This parameter will be ignored for other O(state) values."
      - "The parameter is a dictionary. The key of each dictionary item is the
         property name as specified in the data model for CPC resources, with
         underscores instead of hyphens. The value of each dictionary item is
         the property value (in YAML syntax). Integer properties may also be
         provided as decimal strings."
      - "The possible properties in this dictionary are the properties
         defined as writeable in the data model for CPC resources."
    type: dict
    required: false
    default: null
  bundle_level:
    description:
      - "Name of the bundle to be installed on the SE of the CPC (e.g. V(S71))"
      - "Required for O(state=upgrade)"
    type: str
    required: false
    default: null
  upgrade_timeout:
    description:
      - "Timeout in seconds for waiting for completion of upgrade (e.g. 10800)"
    type: int
    required: false
    default: 10800
  accept_firmware:
    description:
      - "Accept the previous bundle level before installing the new level."
      - "Optional for O(state=upgrade), default: True"
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

- name: Gather facts about the CPC
  zhmc_cpc:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_cpc_name }}"
    state: facts
  register: cpc1

- name: Ensure the CPC is inactive
  zhmc_cpc:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_cpc_name }}"
    state: inactive

- name: Ensure the CPC is active
  zhmc_cpc:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_cpc_name }}"
    state: active
  register: cpc1

- name: Ensure the CPC has the desired property values
  zhmc_cpc:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_cpc_name }}"
    state: set
    properties:
      acceptable_status:
        - active
      description: "This is CPC {{ my_cpc_name }}"
  register: cpc1

- name: Upgrade the SE firmware and return CPC facts
  zhmc_cpc:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    name: "{{ my_cpc_name }}"
    state: upgrade
    bundle_level: "S71"
    upgrade_timeout: 10800
  register: cpc1
"""

RETURN = """
changed:
  description: Indicates if any change has been made by the module.
    For O(state=facts), always will be false.
  returned: always
  type: bool
msg:
  description: An error message that describes the failure.
  returned: failure
  type: str
cpc:
  description:
    - "For O(state=inactive), an empty dictionary."
    - "For O(state=active|set|facts|upgrade), the resource properties of the
       CPC after after any specified updates have been applied, and its
       adapters, partitions, and storage groups."
  returned: success
  type: dict
  contains:
    name:
      description: "CPC name"
      type: str
    "{property}":
      description: "Additional properties of the CPC, as described in the data
        model of the 'CPC' object in the R(HMC API,HMC API) book.
        The property names have hyphens (-) as described in that book."
      type: raw
    adapters:
      description: "The adapters of the CPC, with a subset of their
        properties. For details, see the R(HMC API,HMC API) book."
      type: list
      elements: dict
      contains:
        name:
          description: "Adapter name"
          type: str
        object-uri:
          description: "Canonical URI of the adapter"
          type: str
        adapter-id:
          description: "Adapter ID (PCHID)"
          type: str
        type:
          description: "Adapter type"
          type: str
        adapter-family:
          description: "Adapter family"
          type: str
        status:
          description: "Status of the adapter"
          type: str
    partitions:
      description: "The defined partitions of the CPC, with a subset of their
        properties. For details, see the R(HMC API,HMC API) book."
      type: list
      elements: dict
      contains:
        name:
          description: "Partition name"
          type: str
        object-uri:
          description: "Canonical URI of the partition"
          type: str
        type:
          description: "Type of the partition"
          type: str
        status:
          description: "Status of the partition"
          type: str
    storage-groups:
      description: "The storage groups associated with the CPC, with a subset
        of their properties. For details, see the R(HMC API,HMC API) book."
      type: list
      elements: dict
      contains:
        name:
          description: "Storage group name"
          type: str
        object-uri:
          description: "Canonical URI of the storage group"
          type: str
        type:
          description: "Storage group type"
          type: str
        fulfillment-status:
          description: "Fulfillment status of the storage group"
          type: str
        cpc-uri:
          description: "Canonical URI of the associated CPC"
          type: str
  sample:
    {
        "name": "CPCA",
        "{property}": "... more properties ... ",
        "adapters": [
            {
                "adapter-family": "ficon",
                "adapter-id": "120",
                "name": "FCP_120_SAN1_02",
                "object-uri": "/api/adapters/dfb2147a-e578-11e8-a87c-00106f239c31",
                "status": "active",
                "type": "fcp"
            },
            {
                "adapter-family": "osa",
                "adapter-id": "10c",
                "name": "OSM1",
                "object-uri": "/api/adapters/ddde026c-e578-11e8-a87c-00106f239c31",
                "status": "active",
                "type": "osm"
            },
        ],
        "partitions": [
            {
                "name": "PART1",
                "object-uri": "/api/partitions/c44338de-351b-11e9-9fbb-00106f239d19",
                "status": "stopped",
                "type": "linux"
            },
            {
                "name": "PART2",
                "object-uri": "/api/partitions/6a46d18a-cf79-11e9-b447-00106f239d19",
                "status": "active",
                "type": "ssc"
            },
        ],
        "storage-groups": [
            {
                "cpc-uri": "/api/cpcs/66942455-4a14-3f99-8904-3e7ed5ca28d7",
                "fulfillment-state": "complete",
                "name": "CPCA_SG_PART1",
                "object-uri": "/api/storage-groups/58e41a42-20a6-11e9-8dfc-00106f239c31",
                "type": "fcp"
            },
            {
                "cpc-uri": "/api/cpcs/66942455-4a14-3f99-8904-3e7ed5ca28d7",
                "fulfillment-state": "complete",
                "name": "CPCA_SG_PART2",
                "object-uri": "/api/storage-groups/4947c6d0-f433-11ea-8f73-00106f239d19",
                "type": "fcp"
            },
        ],
    }
"""

import logging  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule, \
    missing_required_lib  # noqa: E402

from ..module_utils.common import log_init, open_session, close_session, \
    hmc_auth_parameter, Error, StatusError, ParameterError, to_unicode, \
    process_normal_property, common_fail_on_import_errors, pull_properties, \
    parse_hmc_host, blanked_params  # noqa: E402

try:
    import zhmcclient
    IMP_ZHMCCLIENT_ERR = None
except ImportError:
    IMP_ZHMCCLIENT_ERR = traceback.format_exc()

# Python logger name for this module
LOGGER_NAME = 'zhmc_cpc'

LOGGER = logging.getLogger(LOGGER_NAME)

# Dictionary of properties of CPC resources, in this format:
#   name: (allowed, create, update, eq_func, type_cast)
# where:
#   name: Name of the property according to the data model, with hyphens
#     replaced by underscores (this is how it is or would be specified in
#     the 'properties' module parameter).
#   allowed: Indicates whether it is allowed in the 'properties' module
#     parameter.
#   create: Not applicable for CPCs.
#   update: Indicates whether it can be specified for the "Modify CPC
#     Properties" operation (at all).
#   update_while_active: Indicates whether it can be specified for the "Modify
#     CPC Properties" operation while the CPC is active. None means
#     "not applicable" (used for update=False).
#   eq_func: Equality test function for two values of the property; None means
#     to use Python equality.
#   type_cast: Type cast function for an input value of the property; None
#     means to use it directly. This can be used for example to convert
#     integers provided as strings by Ansible back into integers (that is a
#     current deficiency of Ansible).
ZHMC_CPC_PROPERTIES = {

    # update properties for any mode:
    'acceptable_status': (True, None, True, True, None, None),

    # update properties for DPM mode:
    'description': (True, None, True, True, None, to_unicode),

    # update properties for classic mode:
    'next_activation_profile_name': (True, None, True, True, None, to_unicode),
    'processor_running_time_type': (True, None, True, True, None, to_unicode),
    'processor_running_time': (True, None, True, True, None, int),
    # Following property is read-only on z14 and higher:
    'does_wait_state_end_time_slice': (True, None, True, True, None, None),

    # read-only properties (subset):
    'name': (False, None, False, None, None, None),  # provided in 'name' parm
    'object_uri': (False, None, False, None, None, None),
    'object_id': (False, None, False, None, None, None),
    'parent': (False, None, False, None, None, None),
    'class': (False, None, False, None, None, None),

    # The properties not specified here default to allow=False.
}


def process_properties(cpc, params):
    """
    Process the properties specified in the 'properties' module parameter,
    and return a dictionary (update_props) that contains the properties that
    can be updated. The input property values are compared with the existing
    resource property values and the returned set of properties is the minimal
    set of properties that need to be changed.

    - Underscores in the property names are translated into hyphens.
    - The presence of properties that cannot be updated is surfaced by raising
      ParameterError.

    Parameters:

      cpc (zhmcclient.Cpc): CPC to be updated.

      params (dict): Module input parameters.

    Returns:
      update_props: dict of properties for zhmcclient.Cpc.update_properties()

    Raises:
      ParameterError: An issue with the module parameters.
    """

    input_props = params['properties']
    if input_props is None:
        input_props = {}

    update_props = {}
    for prop_name in input_props:

        try:
            # pylint: disable=unused-variable
            allowed, create, update, update_active, eq_func, type_cast = \
                ZHMC_CPC_PROPERTIES[prop_name]
        except KeyError:
            allowed = False

        if not allowed:
            raise ParameterError(
                f"CPC property {prop_name!r} specified in the 'properties' "
                "module parameter cannot be updated.")

        # Process a normal (= non-artificial) property
        _create_props, _update_props, _stop = process_normal_property(
            prop_name, ZHMC_CPC_PROPERTIES, input_props, cpc)
        update_props.update(_update_props)
        if _create_props:
            raise AssertionError()
        if _stop:
            raise AssertionError()

    return update_props


def add_artificial_properties(cpc_properties, cpc):
    """
    Add artificial properties to the CPC properties.

    Upon return, the cpc_properties dict has been extended by these artificial
    properties:

    * 'partitions': List of partitions of the CPC, with the list subset of
      their properties.

    * 'adapters': List of adapters of the CPC, with the list subset of their
      properties.

    * 'storage-groups': List of storage groups attached to the partition, with
      the list subset of their properties.
    """
    partitions = cpc.partitions.list()
    cpc_properties['partitions'] = [dict(p.properties) for p in partitions]

    adapters = cpc.adapters.list()
    cpc_properties['adapters'] = [dict(a.properties) for a in adapters]

    storage_groups = cpc.manager.console.storage_groups.list(
        filter_args={'cpc-uri': cpc.uri})
    cpc_properties['storage-groups'] = [dict(sg.properties)
                                        for sg in storage_groups]


def update_cpc_properties(cpc, params, check_mode):
    """
    Update the properties of the CPC on the HMC.

    Returns the properties to be returned from the module.
    """

    input_props = params['properties']  # with underscores
    if input_props is None:
        input_props = {}
    input_prop_names = list(input_props.keys())
    select_prop_names = params['select_properties']  # with underscores

    changed = False

    pull_properties(cpc, select_prop_names, input_prop_names)
    cpc_properties = dict(cpc.properties)
    update_props = process_properties(cpc, params)

    if update_props:
        if not check_mode:
            cpc.update_properties(update_props)
        # Some updates of CPC properties are not reflected in a new
        # retrieval of properties until after a few seconds (usually the
        # second retrieval).
        # Therefore, we construct the modified result based upon the input
        # changes, and not based upon newly retrieved properties.
        cpc_properties.update(update_props)

        changed = True

    return changed, cpc_properties


def ensure_active(module):
    """
    Ensure the CPC is active, and then set the properties.

    Raises:
      ParameterError: An issue with the module parameters.
      Error: Other errors during processing.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    cpc_name = module.params['name']
    activation_profile_name = module.params['activation_profile_name']

    changed = False

    session, logoff = open_session(module.params)
    try:
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        # Activate the CPC
        cpc_status = cpc.get_property('status')
        if cpc_status in ('not-operating', 'no-power'):
            # CPC is inactive
            if not module.check_mode:
                cpc_dpm_enabled = cpc.get_property('dpm-enabled')
                if cpc_dpm_enabled:
                    cpc.start()
                else:
                    if not activation_profile_name:
                        raise ParameterError(
                            f"CPC {cpc_name!r} is in classic mode and "
                            "activation requires the 'activation_profile_name' "
                            "parameter to be specified")
                    cpc.activate(
                        activation_profile_name=activation_profile_name,
                        force=True)
            changed = True
        elif cpc_status in ('active', 'operating', 'exceptions',
                            'service-required', 'degraded', 'acceptable',
                            'service'):
            # CPC is already active
            pass
        else:
            # cpc_status in ('not-communicating', 'status-check')
            # or any new future status values.
            raise StatusError(
                f"CPC {cpc_name!r} cannot be activated because it is in "
                f"status {cpc_status!r}")

        # Update the properties of the CPC.
        _changed, cpc_properties = update_cpc_properties(
            cpc, module.params, module.check_mode)
        changed |= _changed

        add_artificial_properties(cpc_properties, cpc)

        return changed, cpc_properties

    finally:
        close_session(session, logoff)


def ensure_inactive(module):
    """
    Ensure the CPC is inactive. The operational mode is not changed.

    Raises:
      ParameterError: An issue with the module parameters.
      Error: Other errors during processing.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    cpc_name = module.params['name']

    changed = False

    session, logoff = open_session(module.params)
    try:
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        # Inactivate the CPC
        cpc_status = cpc.get_property('status')
        if cpc_status in ('not-operating', 'no-power'):
            # Already inactive
            pass
        elif cpc_status in ('active', 'operating', 'exceptions',
                            'service-required', 'degraded', 'acceptable',
                            'service'):
            if not module.check_mode:
                cpc_dpm_enabled = cpc.get_property('dpm-enabled')
                if cpc_dpm_enabled:
                    cpc.stop()
                else:
                    cpc.deactivate(force=True)
            changed = True
        else:
            # cpc_status in ('not-communicating', 'status-check')
            # or any new future status values.
            raise StatusError(
                f"CPC {cpc_name!r} cannot be deactivated because it is in "
                f"status {cpc_status!r}")

        return changed, None

    finally:
        close_session(session, logoff)


def ensure_set(module):
    """
    Identify the target CPC and ensure that the specified properties are set on
    the target CPC.

    Raises:
      ParameterError: An issue with the module parameters.
      Error: Other errors during processing.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    cpc_name = module.params['name']

    changed = False

    session, logoff = open_session(module.params)
    try:
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        # Update the properties of the CPC.
        _changed, cpc_properties = update_cpc_properties(
            cpc, module.params, module.check_mode)
        changed |= _changed

        add_artificial_properties(cpc_properties, cpc)

        return changed, cpc_properties

    finally:
        close_session(session, logoff)


def facts(module):
    """
    Identify the target CPC and return facts about the target CPC and its
    child resources.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    cpc_name = module.params['name']
    select_prop_names = module.params['select_properties']  # with underscores

    session, logoff = open_session(module.params)
    try:
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        pull_properties(cpc, select_prop_names)
        cpc_properties = dict(cpc.properties)

        add_artificial_properties(cpc_properties, cpc)

        return False, cpc_properties

    finally:
        close_session(session, logoff)


def upgrade(module):
    """
    Upgrades the firmware of the SE of this CPC to a new bundle level.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    module.fail_on_missing_params(['bundle_level'])
    bundle_level = module.params['bundle_level']
    upgrade_timeout = module.params['upgrade_timeout']
    accept_firmware = module.params['accept_firmware']
    cpc_name = module.params['name']
    select_prop_names = module.params['select_properties']  # with underscores

    session, logoff = open_session(module.params)
    try:
        client = zhmcclient.Client(session)
        console = client.consoles.console
        cpc = client.cpcs.find(name=cpc_name)
        # The default exception handling is sufficient for the above.

        ec_mcl = console.prop('ec-mcl-description')
        hmc_bundle_level = ec_mcl.get('bundle-level', None)
        if hmc_bundle_level is None:
            hmc_version = console.prop('version')
            raise ParameterError(
                f"HMC version {hmc_version} does not support firmware upgrade "
                "through the Web Services API")

        changed = False

        if not module.check_mode:
            try:
                cpc.single_step_install(
                    bundle_level=bundle_level,
                    accept_firmware=accept_firmware,
                    wait_for_completion=True,
                    operation_timeout=upgrade_timeout)
                changed = True
            except zhmcclient.HTTPError as exc:
                if exc.http_status == 400 and exc.reason == 356:
                    # SE was already at that bundle level
                    pass
                else:
                    raise

        pull_properties(cpc, select_prop_names)
        cpc_properties = dict(cpc.properties)

        add_artificial_properties(cpc_properties, cpc)

        return changed, cpc_properties

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
        "inactive": ensure_inactive,
        "active": ensure_active,
        "set": ensure_set,
        "facts": facts,
        "upgrade": upgrade,
    }
    return actions[module.params['state']](module)


def main():
    """Main function"""

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='raw'),
        hmc_auth=hmc_auth_parameter(),
        name=dict(required=True, type='str'),
        state=dict(required=True, type='str',
                   choices=['inactive', 'active', 'set', 'facts', 'upgrade']),
        select_properties=dict(required=False, type='list', elements='str',
                               default=None),
        activation_profile_name=dict(required=False, type='str', default=None),
        properties=dict(required=False, type='dict', default=None),
        bundle_level=dict(required=False, type='str', default=None),
        upgrade_timeout=dict(required=False, type='int', default=10800),
        accept_firmware=dict(required=False, type='bool', default=True),
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

    try:

        changed, result = perform_task(module)

    except (Error, zhmcclient.Error) as exc:
        # These exceptions are considered errors in the environment or in user
        # input. They have a proper message that stands on its own, so we
        # simply pass that message on and will not need a traceback.
        msg = f"{exc.__class__.__name__}: {exc}"
        LOGGER.debug("Module exit (failure): msg: %r", msg)
        module.fail_json(msg=msg)
    # Other exceptions are considered module errors and are handled by Ansible
    # by showing the traceback.

    LOGGER.debug("Module exit (success): changed: %s, cpc: %r",
                 changed, result)
    module.exit_json(
        changed=changed, cpc=result)


if __name__ == '__main__':
    main()
