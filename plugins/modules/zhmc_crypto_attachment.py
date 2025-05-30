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
module: zhmc_crypto_attachment
version_added: "2.9.0"
short_description: Manage the crypto configuration of a partition (DPM mode)
description:
  - Gather facts about the attachment of crypto adapters and crypto domains to
    a partition of a CPC (Z system).
  - Attach a range of crypto domains and a number of crypto adapters to a
    partition.
  - Detach all crypto domains and all crypto adapters from a partition.
author:
  - Andreas Maier (@andy-maier)
  - Andreas Scheuring (@scheuran)
requirements:
  - The targeted Z system must be in the Dynamic Partition Manager (DPM)
    operational mode.
  - "The HMC userid must have these task permissions:
    'Partition Details'."
  - "The HMC userid must have object-access permissions to these objects:
    Target partitions, target crypto adapters, CPC with target partitions and
    adapters."
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
      - The name of the CPC that has the partition and the crypto adapters.
    type: str
    required: true
  partition_name:
    description:
      - The name of the partition to which the crypto domains and crypto
        adapters are attached.
    type: str
    required: true
  state:
    description:
      - "The desired state for the crypto attachment. All states are fully
         idempotent within the limits of the properties that can be changed:"
      - "* V(attached): Ensures that the specified number of crypto adapters
         of the specified crypto type, and the specified range of domain index
         numbers in the specified access mode are attached to the partition."
      - "* V(detached): Ensures that no crypto adapter and no crypto domains
         are attached to the partition."
      - "* V(facts): Returns the crypto configuration of the partition."
    type: str
    required: true
    choices: ['attached', 'detached', 'facts']
  adapter_count:
    description:
      - "Only for O(state=attached): The number of crypto adapters the
         partition needs to have attached.
         The special value -1 means all adapters of the desired crypto type in
         the CPC.
         The O(adapter_names) and O(adapter_count) parameters are mutually
         exclusive and one of them must be specified."
    type: int
    required: false
    default: null
  crypto_type:
    description:
      - "Only for O(state=attached): The crypto type of the crypto adapters
         that will be selected from when O(adapter_count) is specified.
         Ignored when O(adapter_names) is specified."
    type: str
    required: false
    default: 'ep11'
    choices: ['ep11', 'cca', 'acc']
  adapter_names:
    description:
      - "Only for O(state=attached): The names of the crypto adapters the
         partition needs to have attached.
         The O(adapter_names) and O(adapter_count) parameters are mutually
         exclusive and one of them must be specified."
    type: list
    elements: str
    required: false
    default: []
  domain_range:
    description:
      - "Only for O(state=attached): The domain range the partition needs to
         have attached, as a tuple of integers (min, max) that specify the
         inclusive range of domain index numbers.
         Other domains attached to the partition remain unchanged.
         The special value -1 for the max item means the maximum supported
         domain index number."
    type: list
    elements: int
    required: false
    default: [0,-1]
  access_mode:
    description:
      - "Only for O(state=attached): The access mode in which the crypto
         domains specified in O(domain_range) need to be attached."
    type: str
    required: false
    default: 'usage'
    choices: ['usage', 'control']
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

- name: Gather facts about the crypto configuration of a partition
  zhmc_crypto_attachment:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    partition_name: "{{ my_partition_name }}"
    state: facts
  register: crypto1

- name: Ensure domain 0 on all ep11 adapters is attached in usage mode
  zhmc_crypto_attachment:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    partition_name: "{{ my_first_partition_name }}"
    state: attached
    crypto_type: ep11
    adapter_count: -1
    domain_range: 0,0
    access_mode: usage

- name: Ensure domains 1-max on all ep11 adapters are attached in control mode
  zhmc_crypto_attachment:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    partition_name: "{{ my_first_partition_name }}"
    state: attached
    crypto_type: ep11
    adapter_count: -1
    domain_range: 1,-1
    access_mode: control

- name: Ensure domains 0-max on 1 ep11 adapter are attached to in usage mode
  zhmc_crypto_attachment:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    partition_name: "{{ my_second_partition_name }}"
    state: attached
    crypto_type: ep11
    adapter_count: 1
    domain_range: 0,-1
    access_mode: usage

- name: Ensure domains 0-max on two specific adapters are attached
  zhmc_crypto_attachment:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    partition_name: "{{ my_second_partition_name }}"
    state: attached
    adapter_names: [CRYP00, CRYP01]
    domain_range: 0,-1
    access_mode: usage
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
changes:
  description: The changes that were performed by the module.
  returned: success
  type: dict
  contains:
    added-adapters:
      description: Names of the adapters that were added to the partition
      type: list
      elements: str
    added-domains:
      description: Domain index numbers of the crypto domains that were added
        to the partition
      type: list
      elements: str
crypto_configuration:
  description: The crypto configuration of the partition after the changes
    performed by the module.
  returned: success
  type: dict
  contains:
    "{name}":
      description: "Partition name"
      type: dict
      contains:
        adapters:
          description: "Attached crypto adapters"
          type: dict
          contains:
            "{name}":
              description: "Adapter name"
              type: dict
              contains:
                name:
                  description: "Adapter name"
                  type: str
                "{property}":
                  description: "Additional properties of the adapter, as
                    described in the data model of the 'Adapter' object in the
                    R(HMC API,HMC API) book. The property names have hyphens
                    (-) as described in that book."
                  type: raw
        domain_config:
          description: "Attached crypto domains"
          type: dict
          contains:
            "{index}":
              description: "Crypto domain index"
              type: dict
              contains:
                "{access_mode}":
                  description: "Access mode ('control' or 'usage')."
                  type: str
        usage_domains:
          description: "Domain index numbers of the crypto domains attached
            in usage mode"
          type: list
          elements: str
        control_domains:
          description: "Domain index numbers of the crypto domains attached
            in control mode"
          type: list
          elements: str
  sample:
    {
        "CSPF1": {
            "adapters": {
                "CRYP00": {
                    "adapter-family": "crypto",
                    "adapter-id": "118",
                    "card-location": "A14B-LG09",
                    "class": "adapter",
                    "crypto-number": 0,
                    "crypto-type": "ep11-coprocessor",
                    "description": "",
                    "detected-card-type": "crypto-express-6s",
                    "name": "CRYP00",
                    "object-id": "e1274d16-e578-11e8-a87c-00106f239c31",
                    "object-uri": "/api/adapters/e1274d16-e578-11e8-a87c-00106f239c31",
                    "parent": "/api/cpcs/66942455-4a14-3f99-8904-3e7ed5ca28d7",
                    "physical-channel-status": "operating",
                    "state": "online",
                    "status": "active",
                    "tke-commands-enabled": true,
                    "type": "crypto",
                    "udx-loaded": false
                }
            },
            "domain_config": {
                "10": "usage",
                "11": "usage"
            },
            "control_domains": [],
            "usage_domains": [10, 11]
        }
    }
"""

import logging  # noqa: E402
import traceback  # noqa: E402
from ansible.module_utils.basic import AnsibleModule  # noqa: E402

from ..module_utils.common import log_init, open_session, close_session, \
    hmc_auth_parameter, Error, ParameterError, missing_required_lib, \
    common_fail_on_import_errors, parse_hmc_host, blanked_params  # noqa: E402


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
LOGGER_NAME = 'zhmc_crypto_attachment'

LOGGER = logging.getLogger(LOGGER_NAME)

# Conversion of crypto types between module parameter values and HMC values
CRYPTO_TYPES_MOD2HMC = {
    'acc': 'accelerator',
    'cca': 'cca-coprocessor',
    'ep11': 'ep11-coprocessor',
}

# Conversion of access modes between module parameter values and HMC values
ACCESS_MODES_MOD2HMC = {
    'usage': 'control-usage',
    'control': 'control',
}
ACCESS_MODES_HMC2MOD = {
    'control-usage': 'usage',
    'control': 'control',
}


def get_partition_config(partition, all_adapters):
    """
    Return the result of the module by inspecting the current crypto
    config. Used for all 'state' parameter values.

    Parameters:

      partition: Partition object for target partition

      all_adapters: List of Adapter objects for all crypto adapters in the CPC
    """

    # result items
    adapters = {}  # adapter name: adapter properties
    domain_config = {}  # domain index: access mode
    usage_domains = []  # domains attached in usage mode
    control_domains = []  # domains attached in control mode

    partition.pull_full_properties()  # Make sure it contains the changes
    partition_config = partition.get_property('crypto-configuration')
    if partition_config:
        adapter_uris = partition_config['crypto-adapter-uris']
        for a in all_adapters:
            if a.uri in adapter_uris:
                adapters[a.name] = dict(a.properties)
        for dc in partition_config['crypto-domain-configurations']:
            di = int(dc['domain-index'])
            am = ACCESS_MODES_HMC2MOD[dc['access-mode']]
            domain_config[di] = am
            if am == 'control':
                control_domains.append(di)
            else:
                if am != 'usage':
                    raise AssertionError(f"am={am}")
                usage_domains.append(di)

    result = {}
    result[partition.name] = {}
    partition_result = result[partition.name]
    partition_result['adapters'] = adapters
    partition_result['domain_config'] = domain_config
    partition_result['usage_domains'] = usage_domains
    partition_result['control_domains'] = control_domains
    return result


def get_conflicting_domains(
        desired_domains, hmc_access_mode, adapter, partition,
        all_crypto_config, all_partitions):
    """
    Internal function that determines those domains from the desired domains
    on a particular adapter that cannot be attached to a particular partition
    in the desired mode because they are already attached to other partitions
    in a mode that prevents that.
    """
    conflicting_domains = {}
    if adapter.uri in all_crypto_config:
        domains_dict = all_crypto_config[adapter.uri]
        for di in desired_domains:
            if di in domains_dict:
                # The domain is already attached to some
                # partition(s) in some access mode
                for am, p_uri in domains_dict[di]:
                    if am == 'control':
                        # An attachment in control mode does not
                        # prevent additional attachments
                        continue
                    if p_uri == partition.uri and \
                            am == hmc_access_mode:
                        # This is our target partition, and the
                        # domain is already attached in the desired
                        # mode.
                        continue
                    p = all_partitions[p_uri]
                    conflicting_domains[di] = (am, p.name)
    return conflicting_domains


def ensure_attached(params, check_mode):
    """
    Ensure that the specified crypto adapters and crypto domains are attached
    to the target partition.

    Raises:
      ParameterError: An issue with the module parameters.
      Error: Other errors during processing.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    cpc_name = params['cpc_name']
    partition_name = params['partition_name']
    adapter_count = params['adapter_count']
    adapter_names = params['adapter_names']
    domain_range = params['domain_range']
    access_mode = params['access_mode']
    crypto_type = params['crypto_type']

    try:
        if len(domain_range) != 2:
            raise AssertionError(f"len(domain_range)={len(domain_range)}")

        domain_range_lo = int(domain_range[0])
        domain_range_hi = int(domain_range[1])
    except (ValueError, AssertionError):
        raise ParameterError(
            "The 'domain_range' parameter must be a list containing two "
            f"integer numbers, but is: {domain_range!r}")

    if adapter_count and adapter_names:
        raise ParameterError(
            "The 'adapter_count' and 'adapter_names' parameters are "
            "mutually exclusive, but both have been specified: "
            f"adapter_count={adapter_count!r}, "
            f"adapter_names={adapter_names!r}")

    # Ignore crypto_type if adapter_names is specified
    if adapter_names:
        crypto_type = None

    hmc_access_mode = ACCESS_MODES_MOD2HMC[access_mode]

    changed = False
    result = {}
    result_changes = {}

    session, logoff = open_session(params)
    try:
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        partition = cpc.partitions.find(name=partition_name)
        # The default exception handling is sufficient for the above.

        filter_args = {
            'adapter-family': 'crypto',
        }
        if crypto_type:
            filter_args['crypto-type'] = CRYPTO_TYPES_MOD2HMC[crypto_type]
        all_adapters = cpc.adapters.list(filter_args=filter_args,
                                         full_properties=True)
        if not all_adapters:
            raise Error(f"No crypto adapters found on CPC {cpc_name!r}")

        all_adapters_dict = {a.name: a for a in all_adapters}

        # All crypto adapters in a CPC have the same number of domains
        # (otherwise the concept of attaching domains across all attached
        # adapters cannot work). Therefore, the max number of domains can be
        # gathered from any adapter.
        max_domains = all_adapters[0].maximum_crypto_domains

        # Parameter checking on domain range.
        # (can be done only now because it requires the max_domains).
        if domain_range_hi == -1:
            domain_range_hi = max_domains - 1
        if domain_range_lo > domain_range_hi:
            raise ParameterError(
                "In the 'domain_range' parameter, the lower boundary "
                f"(={domain_range_lo}) of the range must be less than the "
                f"higher boundary (={domain_range_hi})")

        # Parameter checking on adapter count.
        # (can be done only now because it requires the adapters listed)
        if adapter_count:
            if adapter_count < 1:
                raise ParameterError(
                    "The 'adapter_count' parameter must be at least 1, but "
                    f"is: {adapter_count}")

            if adapter_count > len(all_adapters):
                raise ParameterError(
                    "The 'adapter_count' parameter must not exceed the "
                    f"number of {len(all_adapters)} crypto adapters of type "
                    f"{crypto_type!r} in CPC {cpc_name!r}, but is "
                    f"{adapter_count}")

        # Verify the specified adapter names exist.
        # (can be done only now because it requires the adapters listed)
        if adapter_names:
            for aname in adapter_names:
                if aname not in all_adapters_dict:
                    raise ParameterError(
                        "The 'adapter_names' parameter specifies a crypto"
                        f"adapter named {aname!r} that does not exist on CPC "
                        f"{cpc_name!r}")

        #
        # Get current crypto config of the target partition.
        #

        # Domains attached to the partition, as a dict with:
        #   key: domain index
        #   value: access mode
        attached_domains = {}

        # Adapters attached to the partition, as a list of Adapter objects:
        attached_adapters = []

        # Adapters not attached to the partition, as a list of Adapter objects:
        detached_adapters = []

        _attached_adapter_uris = []  # URIs of attached adapters
        cc = partition.get_property('crypto-configuration')
        if cc:
            _attached_adapter_uris = cc['crypto-adapter-uris']
            for dc in cc['crypto-domain-configurations']:
                di = int(dc['domain-index'])
                am = dc['access-mode']
                LOGGER.debug(
                    "Crypto config of partition %r: "
                    "Domain %r is attached in %r mode", partition.name, di, am)
                attached_domains[di] = am
        for a in all_adapters:
            if a.uri in _attached_adapter_uris:
                LOGGER.debug(
                    "Crypto config of partition %r: "
                    "Adapter %r is attached", partition.name, a.name)
                attached_adapters.append(a)
            else:
                LOGGER.debug(
                    "Crypto config of partition %r: "
                    "Adapter %r is not attached", partition.name, a.name)
                detached_adapters.append(a)
        del _attached_adapter_uris

        #
        # Get the current crypto config of all partitions of the CPC.
        #
        # This is needed because finding out whether an adapter has the right
        # domains available by simply attaching it to the target partition
        # and reacting to the returned status does not work for stopped
        # partitions.
        #

        # All partition of the CPC, as a dict:
        #   key: partition URI
        #   value: Partition object
        all_partitions = cpc.partitions.list()
        all_partitions = dict(zip([p.uri for p in all_partitions],
                                  all_partitions))

        # Crypto config of all partitions of the CPC, as a dict with:
        #   key: adapter URI
        #   value: dict:
        #     key: domain index (for attached domains)
        #     value: list of tuple(access mode, partition URI)
        all_crypto_config = {}

        for p_uri in all_partitions:
            p = all_partitions[p_uri]
            cc = p.get_property('crypto-configuration')
            # The 'crypto-configuration' property is None or:
            # {
            #   'crypto-adapter-uris': ['/api/...', ...],
            #   'crypto-domain-configurations': [
            #     {'domain-index': 15, 'access-mode': 'control-usage'},
            #     ...
            #   ]
            # }
            if cc:
                _adapter_uris = cc['crypto-adapter-uris']
                for dc in cc['crypto-domain-configurations']:
                    di = int(dc['domain-index'])
                    am = dc['access-mode']
                    for a_uri in _adapter_uris:
                        if a_uri not in all_crypto_config:
                            all_crypto_config[a_uri] = {}
                        domains_dict = all_crypto_config[a_uri]  # mutable
                        if di not in domains_dict:
                            domains_dict[di] = []
                        domains_dict[di].append((am, p.uri))

        #
        # Determine the domains to be attached to the target partition
        #

        desired_domains = list(range(domain_range_lo, domain_range_hi + 1))
        add_domains = []  # List of domain index numbers to be attached
        for di in desired_domains:
            if di not in attached_domains:
                # This domain is not attached to the target partition
                add_domains.append(di)
            elif attached_domains[di] != hmc_access_mode:
                # This domain is attached to the target partition but not in
                # the desired access mode. The access mode could be extended
                # from control to control+usage, but that is not implemented
                # by this code here.
                am_str = ACCESS_MODES_HMC2MOD[attached_domains[di]]
                raise Error(
                    f"Domain {di} is currently attached in {am_str!r} mode to "
                    f"target partition {partition.name!r}, but requested was "
                    f"for mode {access_mode!r}")
            else:
                # This domain is attached to the target partition in the
                # desired access mode
                pass

        # Create the domain config structure for the domains to be attached
        add_domain_config = []
        for di in add_domains:
            add_domain_config.append(
                {'domain-index': di,
                 'access-mode': hmc_access_mode})

        # Check that the domains to be attached to the partition are available
        # on the currently attached adapters
        for a in attached_adapters:
            domains_dict = all_crypto_config[a.uri]
            for di in add_domains:
                if di in domains_dict:
                    for am, p_uri in domains_dict[di]:
                        if am != 'control' and hmc_access_mode != 'control':
                            # Multiple attachments conflict only when both are
                            # in usage mode
                            p = all_partitions[p_uri]
                            am_str = ACCESS_MODES_HMC2MOD[am]
                            raise Error(
                                f"Domain {di} cannot be attached in "
                                f"{access_mode!r} mode to target partition "
                                f"{partition.name!r} because it is already "
                                f"attached in {am_str!r} mode to partition "
                                f"{p.name!r}")

        # Make sure the desired adapters are attached to the partition
        # and the desired domains are attached.
        # The HMC enforces the following for non-empty crypto configurations of
        # a partition:
        # - In the resulting config, the partition needs to have at least one
        #   adapter attached.
        # - In the resulting config, the partition needs to have at least one
        #   domain attached in usage mode.
        # As a result, on an empty crypto config, the first adapter and the
        # first domain(s) need to be attached at the same time.
        result_changes['added-adapters'] = []
        result_changes['added-domains'] = []

        if not adapter_names:
            # Only the number of adapters was specified so it can be any
            # adapter. We accept any already attached adapter.

            missing_count = max(0, adapter_count - len(attached_adapters))
            if missing_count == 0 and add_domain_config:
                # Adapters already sufficient, but domains need to be attached

                LOGGER.debug(
                    "Adapters sufficient - attaching domains %r in %r mode to "
                    "target partition %r",
                    add_domains, access_mode, partition.name)

                if not check_mode:
                    try:
                        partition.increase_crypto_config([], add_domain_config)
                    except zhmcclient.Error as exc:
                        raise Error(
                            f"Attaching domains {add_domains!r} in "
                            f"{access_mode!r} mode to target partition "
                            f"{partition.name!r} failed: {exc}")

                changed = True
                result_changes['added-domains'].extend(add_domains)

            elif missing_count > 0:
                # Adapters need to be attached

                for adapter in detached_adapters:
                    if missing_count == 0:
                        break

                    # Check that the adapter has all needed domains available
                    conflicting_domains = get_conflicting_domains(
                        desired_domains, hmc_access_mode, adapter, partition,
                        all_crypto_config, all_partitions)

                    if conflicting_domains:
                        LOGGER.debug(
                            "Skipping adapter %r because the following of "
                            "its domains are already attached to other "
                            "partitions: %r",
                            adapter.name, conflicting_domains)
                        continue

                    LOGGER.debug(
                        "Attaching adapter %r and domains %r in %r mode to "
                        "target partition %r",
                        adapter.name, add_domains, access_mode, partition.name)

                    if not check_mode:
                        try:
                            partition.increase_crypto_config(
                                [adapter], add_domain_config)
                        except zhmcclient.Error as exc:
                            raise Error(
                                f"Attaching adapter {adapter.name!r} and "
                                f"domains {add_domains!r} in {access_mode!r} "
                                f"mode to target partition {partition.name!r} "
                                f"failed: {exc}")

                    changed = True
                    result_changes['added-adapters'].append(adapter.name)
                    result_changes['added-domains'].extend(add_domains)

                    # Don't try to add domains again for next adapter:
                    add_domain_config = []
                    add_domains = []

                    missing_count -= 1

                if missing_count > 0:
                    # Because adapters may be skipped, it is possible that
                    # there are not enough adapters
                    raise Error(
                        "Did not find enough crypto adapters with attachable "
                        f"domains - missing adapters: {missing_count}; "
                        f"Requested domains: {desired_domains}, Access mode: "
                        f"{access_mode}")

        else:
            # Specific adapters need to be attached. We check already attached
            # adapters and add the missing ones. We do not detach adapters
            # that are currently attached but not in the input list.

            attached_adapter_names = {a.name for a in attached_adapters}
            for aname in adapter_names:
                if aname not in attached_adapter_names:
                    adapter = all_adapters_dict[aname]

                    # Check that the adapter has all needed domains available
                    conflicting_domains = get_conflicting_domains(
                        desired_domains, hmc_access_mode, adapter, partition,
                        all_crypto_config, all_partitions)
                    if conflicting_domains:
                        raise Error(
                            f"Crypto adapter {adapter.name!r} cannot be "
                            f"attached to partition {partition.name!r} because "
                            "the following of its domains are already attached "
                            "to other partitions in conflicting modes: "
                            f"{conflicting_domains!r}")

                    if not check_mode:
                        try:
                            partition.increase_crypto_config(
                                [adapter], add_domain_config)
                        except zhmcclient.Error as exc:
                            raise Error(
                                f"Attaching adapter {adapter.name!r} and "
                                f"domains {add_domains!r} in {access_mode!r} "
                                f"mode to target partition {partition.name!r} "
                                f"failed: {exc}")

                    changed = True
                    result_changes['added-adapters'].append(adapter.name)
                    result_changes['added-domains'].extend(add_domains)

                    # Don't try to add domains again for next adapter:
                    add_domain_config = []
                    add_domains = []

            if add_domain_config:
                # The desired adapters were already attached so the additional
                # domains need to be added to the crypto config.

                LOGGER.debug(
                    "Adapters were already attached to target partition %r "
                    "- attaching domains %r in %r mode",
                    partition.name, add_domains, access_mode)

                if not check_mode:
                    try:
                        partition.increase_crypto_config(
                            [], add_domain_config)
                    except zhmcclient.Error as exc:
                        raise Error(
                            f"Attaching domains {add_domains!r} in "
                            f"{access_mode!r} mode to target partition "
                            f"{partition.name!r} failed: {exc}")

                changed = True
                result_changes['added-domains'].extend(add_domains)

        if not check_mode:
            # This is not optimal because it does not produce a result
            # in check mode, but because the actual config is determined,
            # instead of the artificially calculated one, it seems better
            # to return no config than the unchanged actual config.
            result.update(get_partition_config(partition, all_adapters))

        return changed, result, result_changes

    finally:
        close_session(session, logoff)


def ensure_detached(params, check_mode):
    """
    Ensure that the target partition has no adapters and no domains attached.

    Raises:
      ParameterError: An issue with the module parameters.
      Error: Other errors during processing.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    cpc_name = params['cpc_name']
    partition_name = params['partition_name']

    changed = False
    result = {}
    result_changes = {}

    session, logoff = open_session(params)
    try:
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        partition = cpc.partitions.find(name=partition_name)
        # The default exception handling is sufficient for the above.

        # Determine all crypto adapters of any crypto type
        filter_args = {
            'adapter-family': 'crypto',
        }
        all_adapters = cpc.adapters.list(filter_args=filter_args,
                                         full_properties=True)

        cc = partition.get_property('crypto-configuration')
        # The 'crypto-configuration' property is None or:
        # {
        #   'crypto-adapter-uris': ['/api/...', ...],
        #   'crypto-domain-configurations': [
        #     {'domain-index': 15, 'access-mode': 'control-usage'},
        #     ...
        #   ]
        # }
        if cc:
            attached_adapter_uris = cc['crypto-adapter-uris']
            remove_adapters = []
            remove_adapter_names = []
            for a in all_adapters:
                if a.uri in attached_adapter_uris:
                    remove_adapters.append(a)
                    remove_adapter_names.append(a.name)

            remove_domains = []
            for dc in cc['crypto-domain-configurations']:
                di = dc['domain-index']
                remove_domains.append(di)

            LOGGER.debug(
                "Detaching adapters %r and domains %r from target "
                "partition %r", remove_adapter_names, remove_domains,
                partition.name)

            if not check_mode:
                try:
                    partition.decrease_crypto_config(
                        remove_adapters, remove_domains)
                except zhmcclient.Error as exc:
                    raise Error(
                        f"Detaching adapters {remove_adapter_names!r} and "
                        f"domains {remove_domains!r} from target partition "
                        f"{partition.name!r} failed: {exc}")

            changed = True
            result_changes['removed-adapters'] = remove_adapter_names
            result_changes['removed-domains'] = remove_domains

        if not check_mode:
            # This is not optimal because it does not produce a result
            # in check mode, but because the actual config is determined,
            # instead of the artificially calculated one, it seems better
            # to return no config than the unchanged actual config.
            result.update(get_partition_config(partition, all_adapters))

        return changed, result, result_changes

    finally:
        close_session(session, logoff)


def facts(params, check_mode):
    # pylint: disable=unused-argument
    """
    Return facts about the crypto configuration of the partition.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    cpc_name = params['cpc_name']
    partition_name = params['partition_name']

    session, logoff = open_session(params)
    try:
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        partition = cpc.partitions.find(name=partition_name)
        # The default exception handling is sufficient for the above.

        # Determine all crypto adapters of any crypto type
        filter_args = {
            'adapter-family': 'crypto',
        }
        all_adapters = cpc.adapters.list(filter_args=filter_args,
                                         full_properties=True)

        result = get_partition_config(partition, all_adapters)

        return False, result, None

    finally:
        close_session(session, logoff)


def perform_task(params, check_mode):
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
        "attached": ensure_attached,
        "detached": ensure_detached,
        "facts": facts,
    }
    return actions[params['state']](params, check_mode)


def main():
    """Main function"""

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='raw'),
        hmc_auth=hmc_auth_parameter(),
        cpc_name=dict(required=True, type='str'),
        partition_name=dict(required=True, type='str'),
        state=dict(required=True, type='str',
                   choices=['attached', 'detached', 'facts']),
        adapter_count=dict(required=False, type='int', default=None),
        crypto_type=dict(required=False, type='str',
                         choices=['ep11', 'cca', 'acc'], default='ep11'),
        adapter_names=dict(required=False, type='list', elements='str',
                           default=[]),
        domain_range=dict(required=False, type='list', elements='int',
                          default=[0, -1]),
        access_mode=dict(required=False, type='str',
                         choices=['usage', 'control'], default='usage'),
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

    if LOGGER.isEnabledFor(logging.DEBUG):
        LOGGER.debug("Module entry: params: %r",
                     blanked_params(module.params))

    try:

        changed, result, changes = perform_task(
            module.params, module.check_mode)

    except (Error, zhmcclient.Error) as exc:
        # These exceptions are considered errors in the environment or in user
        # input. They have a proper message that stands on its own, so we
        # simply pass that message on and will not need a traceback.
        msg = f"{exc.__class__.__name__}: {exc}"
        LOGGER.debug("Module exit (failure): msg: %s", msg)
        module.fail_json(msg=msg)
    # Other exceptions are considered module errors and are handled by Ansible
    # by showing the traceback.

    LOGGER.debug(
        "Module exit (success): changed: %r, crypto_configuration: %r, "
        "changes: %r", changed, result, changes)
    module.exit_json(
        changed=changed, crypto_configuration=result, changes=changes)


if __name__ == '__main__':
    main()
