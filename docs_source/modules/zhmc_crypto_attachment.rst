.. _zhmc_crypto_attachment_module:


zhmc_crypto_attachment -- Attach crypto resources to partitions
===============================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Gather facts about the attachment of crypto adapters and crypto domains to a partition of a CPC (Z system).

Attach a range of crypto domains and a number of crypto adapters to a partition.

Detach all crypto domains and all crypto adapters from a partition.



Requirements
------------
The below requirements are needed on the host that executes this module.

- Access to the WS API of the HMC of the targeted Z system (see :term:`HMC API`). The targeted Z system must be in the Dynamic Partition Manager (DPM) operational mode.



Parameters
----------

  hmc_host (True, str, None)
    The hostname or IP address of the HMC.


  hmc_auth (True, dict, None)
    The authentication credentials for the HMC, as a dictionary of ``userid``, ``password``.


    userid (True, str, None)
      The userid (username) for authenticating with the HMC.


    password (True, str, None)
      The password for authenticating with the HMC.



  cpc_name (True, str, None)
    The name of the CPC that has the partition and the crypto adapters.


  partition_name (True, str, None)
    The name of the partition to which the crypto domains and crypto adapters are attached.


  state (True, str, None)
    The desired state for the attachment:

    * ``attached``: Ensures that the specified number of crypto adapters of the specified crypto type, and the specified range of domain index numbers in the specified access mode are attached to the partition.

    * ``detached``: Ensures that no crypto adapter and no crypto domains are attached to the partition.

    * ``facts``: Does not change anything on the attachment and returns the crypto configuration of the partition.


  adapter_count (False, int, -1)
    Only for ``state=attach``: The number of crypto adapters the partition needs to have attached. The special value -1 means all adapters of the desired crypto type in the CPC. The ``adapter_names`` and ``adapter_count`` parameters are mutually exclusive; if neither is specified the default for ``adapter_count`` applies.


  adapter_names (False, list, [])
    Only for ``state=attach``: The names of the crypto adapters the partition needs to have attached. The ``adapter_names`` and ``adapter_count`` parameters are mutually exclusive; if neither is specified the default for ``adapter_count`` applies.


  domain_range (False, list, [0, -1])
    Only for ``state=attach``: The domain range the partition needs to have attached, as a tuple of integers (min, max) that specify the inclusive range of domain index numbers. Other domains attached to the partition remain unchanged. The special value -1 for the max item means the maximum supported domain index number.


  access_mode (False, str, usage)
    Only for ``state=attach``: The access mode in which the crypto domains specified in ``domain_range`` need to be attached.


  crypto_type (False, str, ep11)
    Only for ``state=attach``: The crypto type of the crypto adapters that will be considered for attaching.


  log_file (False, str, None)
    File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.


  faked_session (False, raw, None)
    A ``zhmcclient_mock.FakedSession`` object that has a mocked HMC set up. If not null, this session will be used instead of connecting to the HMC specified in ``hmc_host``. This is used for testing purposes only.









Examples
--------

.. code-block:: yaml+jinja

    
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




Return Values
-------------

crypto_configuration (success, dict, )
  For ``state=detached|attached|facts``, the crypto configuration of the partition after the changes performed by the module.


  {name} (, dict, )
    Partition name


    adapters (, dict, )
      Attached adapters


      {name} (, dict, )
        Adapter name


        name (, str, )
          Adapter name


        {property} (, any, )
          Additional properties of the adapter, as described in the :term:`HMC API` (using hyphens (-) in the property names).




    domain_config (, dict, )
      Attached crypto domains


      {index} (, dict, )
        Crypto domain index


        {access_mode} (, str, )
          Access mode ('control' or 'usage').




    usage_domains (, list, )
      Domain index numbers of the crypto domains attached in usage mode


    control_domains (, list, )
      Domain index numbers of the crypto domains attached in control mode




changes (success, dict, )
  For ``state=detached|attached|facts``, a dictionary with the changes performed.


  added-adapters (, list, )
    Names of the adapters that were added to the partition


  added-domains (, list, )
    Domain index numbers of the crypto domains that were added to the partition






Status
------




- This module is guaranteed to have backward compatible interface changes going forward. *[stableinterface]*


- This module is maintained by community.



Authors
~~~~~~~

- Andreas Maier (@andy-maier)
- Andreas Scheuring (@scheuran)

