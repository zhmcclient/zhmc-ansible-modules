#!/usr/bin/env python
# Copyright 2018 IBM Corp. All Rights Reserved.
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

from __future__ import absolute_import, print_function

import logging
from ansible.module_utils.basic import AnsibleModule
import requests.packages.urllib3
import zhmcclient

from zhmc_ansible_modules.utils import log_init, Error, ParameterError, \
    get_hmc_auth, get_session

# For information on the format of the ANSIBLE_METADATA, DOCUMENTATION,
# EXAMPLES, and RETURN strings, see
# http://docs.ansible.com/ansible/dev_guide/developing_modules_documenting.html

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community',
    'shipped_by': 'other',
    'other_repo_url': 'https://github.com/zhmcclient/zhmc-ansible-modules'
}

DOCUMENTATION = """
---
module: zhmc_crypto_attachment
version_added: "0.6"
short_description: Manages the attachment of crypto adapters and domains to
    partitions.
description:
  - Gathers facts about the attachment of crypto adapters and domains to a
    partition.
  - Attaches a range of crypto domains and a number of crypto adapters to a
    partition.
  - Detaches all crypto domains and all crypto adapters from a partition.
notes:
  - The CPC of the target partition must be in the
    Dynamic Partition Manager (DPM) operational mode.
author:
  - Andreas Maier (@andy-maier, maiera@de.ibm.com)
  - Andreas Scheuring (@scheuran, scheuran@de.ibm.com)
requirements:
  - Network access to HMC
  - zhmcclient >=0.20.0
  - ansible >=2.2.0.0
options:
  hmc_host:
    description:
      - The hostname or IP address of the HMC.
    required: true
  hmc_auth:
    description:
      - The authentication credentials for the HMC.
    required: true
    suboptions:
      userid:
        description:
          - The userid (username) for authenticating with the HMC.
        required: true
      password:
        description:
          - The password for authenticating with the HMC.
        required: true
  cpc_name:
    description:
      - The name of the CPC that has the partition and the crypto adapters.
    required: true
  partition_name:
    description:
      - The name of the partition to which the crypto domains and crypto
        adapters are attached.
    required: true
  state:
    description:
      - "The desired state for the attachment:"
      - "* C(attached): Ensures that the specified number of crypto adapters
         of the specified crypto type, and the specified range of domain index
         numbers in the specified access mode are attached to the partition."
      - "* C(detached): Ensures that no crypto adapter and no crypto domains
         are attached to the partition."
      - "* C(facts): Does not change anything on the attachment and returns
         the crypto configuration of the partition."
    required: true
    choices: ['attached', 'detached', 'facts']
  adapter_count:
    description:
      - "Only for C(state=attach): The number of crypto adapters the partition
         needs to have attached.
         The special value -1 means all adapters of the desired crypto type in
         the CPC.
         The C(adapter_names) and C(adapter_count) parameters are mutually
         exclusive; if neither is specified the default for C(adapter_count)
         applies."
    required: false
    default: -1
  adapter_names:
    description:
      - "Only for C(state=attach): The names of the crypto adapters the
         partition needs to have attached.
         The C(adapter_names) and C(adapter_count) parameters are mutually
         exclusive; if neither is specified the default for C(adapter_count)
         applies."
    required: false
    default: []
  domain_range:
    description:
      - "Only for C(state=attach): The domain range the partition needs to have
         attached, as a tuple of integers (min, max) that specify the inclusive
         range of domain index numbers.
         Other domains attached to the partition remain unchanged.
         The special value -1 for the max item means the maximum supported
         domain index number."
    required: false
    default: (0, -1)
  access_mode:
    description:
      - "Only for C(state=attach): The access mode in which the crypto domains
         specified in C(domain_range) need to be attached."
    required: false
    default: 'usage'
    choices: ['usage', 'control']
  crypto_type:
    description:
      - "Only for C(state=attach): The crypto type of the crypto adapters that
         will be considered for attaching."
    required: false
    default: 'ep11'
    choices: ['ep11', 'cca', 'acc']
  log_file:
    description:
      - "File path of a log file to which the logic flow of this module as well
         as interactions with the HMC are logged. If null, logging will be
         propagated to the Python root logger."
    required: false
    default: null
  faked_session:
    description:
      - "A C(zhmcclient_mock.FakedSession) object that has a mocked HMC set up.
         If provided, it will be used instead of connecting to a real HMC. This
         is used for testing purposes only."
    required: false
    default: Real HMC will be used.
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

- name: Ensure domains 0-max on two specific ep11 adapters are attached
  zhmc_crypto_attachment:
    hmc_host: "{{ my_hmc_host }}"
    hmc_auth: "{{ my_hmc_auth }}"
    cpc_name: "{{ my_cpc_name }}"
    partition_name: "{{ my_second_partition_name }}"
    state: attached
    crypto_type: ep11
    adapter_names: [CRYP00, CRYP01]
    domain_range: 0,-1
    access_mode: usage

"""

RETURN = """
crypto_configuration:
  description:
    - "For C(state=detached|attached|facts), a
       dictionary with the crypto configuration of the partition after the
       changes applied by the module. Key is the partition name, and value
       is a dictionary with keys:
       - 'adapters': attached adapters, as a dict of key: adapter name, value:
         dict of adapter properties;
       - 'domain_config': attached domains, as a dict of key: domain index,
         value: access mode ('control' or 'usage');
       - 'usage_domains': domains attached in usage mode, as a list of domain
         index numbers;
       - 'control_domains': domains attached in control mode, as a list of
         domain index numbers."
  returned: success
  type: dict
  sample: |
    C({
      "part-1": {
        "adapters": {
          "adapter 1": {
            "type": "crypto",
            ...
          }
        },
        "domain_config": {
          "0": "usage",
          "1": "control",
          "2": "control"
        }
        "usage_domains": [0],
        "control_domains": [1, 2]
      }
    })
changes:
  description:
    - "For C(state=detached|attached|facts), a dictionary with the changes
       performed."
  returned: success
  type: dict
  sample: |
    C({
      "added-adapters": ["adapter 1", "adapter 2"],
      "added-domains": ["0", "1"]
    })
"""

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
    adapters = dict()  # adapter name: adapter properties
    domain_config = dict()  # domain index: access mode
    usage_domains = list()  # domains attached in usage mode
    control_domains = list()  # domains attached in control mode

    partition.pull_full_properties()  # Make sure it contains the changes
    partition_config = partition.get_property('crypto-configuration')
    if partition_config:
        adapter_uris = partition_config['crypto-adapter-uris']
        for a in all_adapters:
            if a.uri in adapter_uris:
                adapters[a.name] = a.properties
        for dc in partition_config['crypto-domain-configurations']:
            di = int(dc['domain-index'])
            am = ACCESS_MODES_HMC2MOD[dc['access-mode']]
            domain_config[di] = am
            if am == 'control':
                control_domains.append(di)
            else:
                assert am == 'usage', \
                    "am={}".format(am)
                usage_domains.append(di)

    result = dict()
    result[partition.name] = dict()
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
    conflicting_domains = dict()
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

    # Note: Defaults specified in argument_spec will be set in params dict
    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['cpc_name']
    partition_name = params['partition_name']
    adapter_count = params.get('adapter_count', None)  # No default specified
    adapter_names = params.get('adapter_names', None)  # No default specified
    domain_range = params['domain_range']
    access_mode = params['access_mode']
    crypto_type = params['crypto_type']
    faked_session = params.get('faked_session', None)  # No default specified

    try:
        assert len(domain_range) == 2, \
            "len(domain_range)={}".format(len(domain_range))
        domain_range_lo = int(domain_range[0])
        domain_range_hi = int(domain_range[1])
    except (ValueError, AssertionError):
        raise ParameterError(
            "The 'domain_range' parameter must be a list containing two "
            "integer numbers, but is: {!r}".format(domain_range))

    hmc_crypto_type = CRYPTO_TYPES_MOD2HMC[crypto_type]
    hmc_access_mode = ACCESS_MODES_MOD2HMC[access_mode]

    changed = False
    result = dict()
    result_changes = dict()

    try:
        session = get_session(faked_session, host, userid, password)
        client = zhmcclient.Client(session)
        cpc = client.cpcs.find(name=cpc_name)
        partition = cpc.partitions.find(name=partition_name)
        # The default exception handling is sufficient for the above.

        # Determine all crypto adapters of the specified crypto type.
        filter_args = {
            'adapter-family': 'crypto',
            'crypto-type': hmc_crypto_type,
        }
        all_adapters = cpc.adapters.list(filter_args=filter_args,
                                         full_properties=True)
        if not all_adapters:
            raise Error("No crypto adapters of type {!r} found on CPC {!r} ".
                        format(crypto_type, cpc_name))

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
                "In the 'domain_range' parameter, the lower boundary (={}) "
                "of the range must be less than the higher boundary (={})".
                format(domain_range_lo, domain_range_hi))

        # Parameter checking on adapter count and adapter names.
        # (can be done only now because it requires the number of adapters).
        if adapter_count is None and adapter_names is None:
            adapter_count == -1
        if adapter_count is not None:
            if adapter_names is not None:
                raise ParameterError(
                    "The 'adapter_count' and 'adapter_names' parameters are "
                    "mutually exclusive, but both have been specified: "
                    "adapter_count={!r}, adapter_names={!r}".
                    format(adapter_count, adapter_names))
            if adapter_count == -1:
                adapter_count = len(all_adapters)
            elif adapter_count < 1:
                raise ParameterError(
                    "The 'adapter_count' parameter must be at least 1, but "
                    "is: {}".
                    format(adapter_count))
            elif adapter_count > len(all_adapters):
                raise ParameterError(
                    "The 'adapter_count' parameter must not exceed the "
                    "number of {} crypto adapters of type {!r} in CPC {!r}, "
                    "but is {}".
                    format(len(all_adapters), crypto_type, cpc_name,
                           adapter_count))
        else:
            adapter_count = len(adapter_names)

        # Verify the specified adapters exist
        if adapter_names is not None:
            for aname in adapter_names:
                if aname not in all_adapters_dict:
                    raise ParameterError(
                        "The 'adapter_name' parameter specifies an adapter "
                        "named {!r} that does not exist in CPC {!r}".
                        format(aname, cpc_name))

        # At this point, we have:
        # - adapter_count is a valid number 1..max in all cases.
        # - adapter_names is None if the adapters do not matter or is a
        #   list of existing adapter names of length adapter_count.

        #
        # Get current crypto config of the target partition.
        #

        # Domains attached to the partition, as a dict with:
        #   key: domain index
        #   value: access mode
        attached_domains = dict()

        # Adapters attached to the partition, as a list of Adapter objects:
        attached_adapters = list()

        # Adapters not attached to the partition, as a list of Adapter objects:
        detached_adapters = list()

        _attached_adapter_uris = list()  # URIs of attached adapters
        cc = partition.get_property('crypto-configuration')
        if cc:
            _attached_adapter_uris = cc['crypto-adapter-uris']
            for dc in cc['crypto-domain-configurations']:
                di = int(dc['domain-index'])
                am = dc['access-mode']
                LOGGER.debug(
                    "Crypto config of partition {!r}: "
                    "Domain {} is attached in {!r} mode".
                    format(partition.name, di, am))
                attached_domains[di] = am
        for a in all_adapters:
            if a.uri in _attached_adapter_uris:
                LOGGER.debug(
                    "Crypto config of partition {!r}: "
                    "Adapter {!r} is attached".
                    format(partition.name, a.name))
                attached_adapters.append(a)
            else:
                LOGGER.debug(
                    "Crypto config of partition {!r}: "
                    "Adapter {!r} is not attached".
                    format(partition.name, a.name))
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
        all_crypto_config = dict()

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
                            all_crypto_config[a_uri] = dict()
                        domains_dict = all_crypto_config[a_uri]  # mutable
                        if di not in domains_dict:
                            domains_dict[di] = list()
                        domains_dict[di].append((am, p.uri))

        #
        # Determine the domains to be attached to the target partition
        #

        desired_domains = list(range(domain_range_lo, domain_range_hi + 1))
        add_domains = list()  # List of domain index numbers to be attached
        for di in desired_domains:
            if di not in attached_domains:
                # This domain is not attached to the target partition
                add_domains.append(di)
            elif attached_domains[di] != hmc_access_mode:
                # This domain is attached to the target partition but not in
                # the desired access mode. The access mode could be extended
                # from control to control+usage, but that is not implemented
                # by this code here.
                raise Error(
                    "Domain {} is currently attached in {!r} mode to target "
                    "partition {!r}, but requested was {!r} mode".
                    format(di,
                           ACCESS_MODES_HMC2MOD[attached_domains[di]],
                           partition.name, access_mode))
            else:
                # This domain is attached to the target partition in the
                # desired access mode
                pass

        # Create the domain config structure for the domains to be attached
        add_domain_config = list()
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
                            raise Error(
                                "Domain {} cannot be attached in {!r} mode to "
                                "target partition {!r} because it is already "
                                "attached in {!r} mode to partition {!r}".
                                format(di, access_mode, partition.name,
                                       ACCESS_MODES_HMC2MOD[am], p.name))

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

        if adapter_names is None:

            # Only the number of adapters was specified so it can be any
            # adapter. We accept any already attached adapter.

            missing_count = max(0, adapter_count - len(attached_adapters))
            assert missing_count <= len(detached_adapters), \
                "missing_count={}, len(detached_adapters)={}".\
                format(missing_count, len(detached_adapters))
            if missing_count == 0 and add_domain_config:
                # Adapters already sufficient, but domains need to be attached

                LOGGER.debug(
                    "Adapters sufficient - attaching domains {!r} in {!r} "
                    "mode to target partition {!r}".
                    format(add_domains, access_mode, partition.name))

                if not check_mode:
                    try:
                        partition.increase_crypto_config([], add_domain_config)
                    except zhmcclient.Error as exc:
                        raise Error(
                            "Attaching domains {!r} in {!r} mode to target "
                            "partition {!r} failed: {}".
                            format(add_domains, access_mode, partition.name,
                                   exc))

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
                            "Skipping adapter {!r} because the following of "
                            "its domains are already attached to other "
                            "partitions: {!r}".
                            format(adapter.name, conflicting_domains))
                        continue

                    LOGGER.debug(
                        "Attaching adapter {!r} and domains {!r} in {!r} mode "
                        "to target partition {!r}".
                        format(adapter.name, add_domains, access_mode,
                               partition.name))

                    if not check_mode:
                        try:
                            partition.increase_crypto_config(
                                [adapter], add_domain_config)
                        except zhmcclient.Error as exc:
                            raise Error(
                                "Attaching adapter {!r} and domains {!r} in "
                                "{!r} mode to target partition {!r} "
                                "failed: {}".
                                format(adapter.name, add_domains, access_mode,
                                       partition.name, exc))

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
                        "domains - missing adapters: {}; Requested domains: "
                        "{}, Access mode: {}".
                        format(missing_count, desired_domains, access_mode))

        else:  # adapter_names is not None

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
                            "Crypto adapter {!r} cannot be attached to "
                            "partition {!r} because the following of "
                            "its domains are already attached to other "
                            "partitions in conflicting modes: {!r}".
                            format(adapter.name, partition.name,
                                   conflicting_domains))

                    if not check_mode:
                        try:
                            partition.increase_crypto_config(
                                [adapter], add_domain_config)
                        except zhmcclient.Error as exc:
                            raise Error(
                                "Attaching adapter {!r} and domains {!r} in "
                                "{!r} mode to target partition {!r} "
                                "failed: {}".
                                format(adapter.name, add_domains, access_mode,
                                       partition.name, exc))

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
                    "Adapters were already attached to target partition {!r} "
                    "- attaching domains {!r} in {!r} mode".
                    format(partition.name, add_domains, access_mode))

                if not check_mode:
                    try:
                        partition.increase_crypto_config(
                            [], add_domain_config)
                    except zhmcclient.Error as exc:
                        raise Error(
                            "Attaching domains {!r} in {!r} mode to "
                            "target partition {!r} failed: {}".
                            format(add_domains, access_mode, partition.name,
                                   exc))

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
        session.logoff()


def ensure_detached(params, check_mode):
    """
    Ensure that the target partition has no adapters and no domains attached.

    Raises:
      ParameterError: An issue with the module parameters.
      Error: Other errors during processing.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    # Note: Defaults specified in argument_spec will be set in params dict
    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['cpc_name']
    partition_name = params['partition_name']
    faked_session = params.get('faked_session', None)  # No default specified

    changed = False
    result = dict()
    result_changes = dict()

    try:
        session = get_session(faked_session, host, userid, password)
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
                "Detaching adapters {!r} and domains {!r} from target "
                "partition {!r}".
                format(remove_adapter_names, remove_domains, partition.name))

            if not check_mode:
                try:
                    partition.decrease_crypto_config(
                        remove_adapters, remove_domains)
                except zhmcclient.Error as exc:
                    raise Error(
                        "Detaching adapters {!r} and domains {!r} from "
                        "target partition {!r} failed: {}".
                        format(remove_adapter_names, remove_domains,
                               partition.name, exc))

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
        session.logoff()


def facts(params, check_mode):
    """
    Return facts about the crypto configuration of the partition.

    Raises:
      ParameterError: An issue with the module parameters.
      zhmcclient.Error: Any zhmcclient exception can happen.
    """

    host = params['hmc_host']
    userid, password = get_hmc_auth(params['hmc_auth'])
    cpc_name = params['cpc_name']
    partition_name = params['partition_name']
    faked_session = params.get('faked_session', None)  # No default specified

    try:
        session = get_session(faked_session, host, userid, password)
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
        session.logoff()


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

    # The following definition of module input parameters must match the
    # description of the options in the DOCUMENTATION string.
    argument_spec = dict(
        hmc_host=dict(required=True, type='str'),
        hmc_auth=dict(required=True, type='dict', no_log=True),
        cpc_name=dict(required=True, type='str'),
        partition_name=dict(required=True, type='str'),
        state=dict(required=True, type='str',
                   choices=['attached', 'detached', 'facts']),
        adapter_count=dict(required=False, type='int'),
        adapter_names=dict(required=False, type='list'),
        domain_range=dict(required=False, type='list', default=[0, -1]),
        access_mode=dict(required=False, type='str',
                         choices=['usage', 'control'], default='usage'),
        crypto_type=dict(required=False, type='str',
                         choices=['ep11', 'cca', 'acc'], default='ep11'),
        log_file=dict(required=False, type='str', default=None),
        faked_session=dict(required=False, type='object'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True)

    log_file = module.params['log_file']
    log_init(LOGGER_NAME, log_file)

    _params = dict(module.params)
    del _params['hmc_auth']
    LOGGER.debug("Module entry: params: {!r}".format(_params))

    try:

        changed, result, changes = perform_task(
            module.params, module.check_mode)

    except (Error, zhmcclient.Error) as exc:
        # These exceptions are considered errors in the environment or in user
        # input. They have a proper message that stands on its own, so we
        # simply pass that message on and will not need a traceback.
        msg = "{}: {}".format(exc.__class__.__name__, exc)
        LOGGER.debug(
            "Module exit (failure): msg: {!r}".
            format(msg))
        module.fail_json(msg=msg)
    # Other exceptions are considered module errors and are handled by Ansible
    # by showing the traceback.

    LOGGER.debug(
        "Module exit (success): changed: {!r}, crypto_configuration: {!r}, "
        "changes: {!r}".format(changed, result, changes))
    module.exit_json(
        changed=changed, crypto_configuration=result, changes=changes)


if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings()
    main()
