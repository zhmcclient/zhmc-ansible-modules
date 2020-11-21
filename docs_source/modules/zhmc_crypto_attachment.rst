
:github_url: https://github.com/IBM/ibm_zos_zosmf/tree/master/plugins/modules/zhmc_crypto_attachment.py

.. _zhmc_crypto_attachment_module:


zhmc_crypto_attachment -- Attach crypto resources to partitions
===============================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gather facts about the attachment of crypto adapters and crypto domains to a partition of a CPC (Z system).
- Attach a range of crypto domains and a number of crypto adapters to a partition.
- Detach all crypto domains and all crypto adapters from a partition.





Parameters
----------


     
hmc_host
  The hostname or IP address of the HMC.


  | **required**: True
  | **type**: str


     
hmc_auth
  The authentication credentials for the HMC, as a dictionary of ``userid``, ``password``.


  | **required**: True
  | **type**: dict


     
  userid
    The userid (username) for authenticating with the HMC.


    | **required**: True
    | **type**: str


     
  password
    The password for authenticating with the HMC.


    | **required**: True
    | **type**: str



     
cpc_name
  The name of the CPC that has the partition and the crypto adapters.


  | **required**: True
  | **type**: str


     
partition_name
  The name of the partition to which the crypto domains and crypto adapters are attached.


  | **required**: True
  | **type**: str


     
state
  The desired state for the attachment:

  * ``attached``: Ensures that the specified number of crypto adapters of the specified crypto type, and the specified range of domain index numbers in the specified access mode are attached to the partition.

  * ``detached``: Ensures that no crypto adapter and no crypto domains are attached to the partition.

  * ``facts``: Does not change anything on the attachment and returns the crypto configuration of the partition.


  | **required**: True
  | **type**: str
  | **choices**: attached, detached, facts


     
adapter_count
  Only for ``state=attach``: The number of crypto adapters the partition needs to have attached. The special value -1 means all adapters of the desired crypto type in the CPC. The ``adapter_names`` and ``adapter_count`` parameters are mutually exclusive; if neither is specified the default for ``adapter_count`` applies.


  | **required**: False
  | **type**: int
  | **default**: -1


     
adapter_names
  Only for ``state=attach``: The names of the crypto adapters the partition needs to have attached. The ``adapter_names`` and ``adapter_count`` parameters are mutually exclusive; if neither is specified the default for ``adapter_count`` applies.


  | **required**: False
  | **type**: list


     
domain_range
  Only for ``state=attach``: The domain range the partition needs to have attached, as a tuple of integers (min, max) that specify the inclusive range of domain index numbers. Other domains attached to the partition remain unchanged. The special value -1 for the max item means the maximum supported domain index number.


  | **required**: False
  | **type**: list
  | **default**: [0, -1]


     
access_mode
  Only for ``state=attach``: The access mode in which the crypto domains specified in ``domain_range`` need to be attached.


  | **required**: False
  | **type**: str
  | **default**: usage
  | **choices**: usage, control


     
crypto_type
  Only for ``state=attach``: The crypto type of the crypto adapters that will be considered for attaching.


  | **required**: False
  | **type**: str
  | **default**: ep11
  | **choices**: ep11, cca, acc


     
log_file
  File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.


  | **required**: False
  | **type**: str


     
faked_session
  A ``zhmcclient_mock.FakedSession`` object that has a mocked HMC set up. If not null, this session will be used instead of connecting to the HMC specified in ``hmc_host``. This is used for testing purposes only.


  | **required**: False
  | **type**: raw




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


   crypto_configuration
        For ``state=detached|attached|facts``, the crypto configuration of the partition after the changes performed by the module.


        | **returned**: success
        | **type**: dict


    {name}
          Partition name


          | **type**: dict


     adapters
            Attached adapters


            | **type**: dict


      {name}
              Adapter name


              | **type**: dict


       name
                Adapter name


                | **type**: str



       {property}
                Additional properties of the adapter, as described in the :term:`HMC API` (using hyphens (-) in the property names).


                | **type**: 







     domain_config
            Attached crypto domains


            | **type**: dict


      {index}
              Crypto domain index


              | **type**: dict


       {access_mode}
                Access mode ('control' or 'usage').


                | **type**: str







     usage_domains
            Domain index numbers of the crypto domains attached in usage mode


            | **type**: list



     control_domains
            Domain index numbers of the crypto domains attached in control mode


            | **type**: list







   changes
        For ``state=detached|attached|facts``, a dictionary with the changes performed.


        | **returned**: success
        | **type**: dict


    added-adapters
          Names of the adapters that were added to the partition


          | **type**: list



    added-domains
          Domain index numbers of the crypto domains that were added to the partition


          | **type**: list





