
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_crypto_attachment.py

.. _zhmc_crypto_attachment_module:
.. _ibm.ibm_zhmc.zhmc_crypto_attachment_module:


zhmc_crypto_attachment -- Manage the crypto configuration of a partition (DPM mode)
===================================================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gather facts about the attachment of crypto adapters and crypto domains to a partition of a CPC (Z system).
- Attach a range of crypto domains and a number of crypto adapters to a partition.
- Detach all crypto domains and all crypto adapters from a partition.


Requirements
------------

- The targeted Z system must be in the Dynamic Partition Manager (DPM) operational mode.
- The HMC userid must have these task permissions: 'Partition Details'.
- The HMC userid must have object-access permissions to these objects: Target partitions, target crypto adapters, CPC with target partitions and adapters.




Parameters
----------


hmc_host
  The hostnames or IP addresses of a single HMC or of a list of redundant HMCs. A single HMC can be specified as a string type or as an HMC list with one item. An HMC list can be specified as a list type or as a string type containing a Python list representation.

  The first available HMC of a list of redundant HMCs is used for the entire execution of the module.

  | **required**: True
  | **type**: raw


hmc_auth
  The authentication credentials for the HMC.

  | **required**: True
  | **type**: dict


  userid
    The userid (username) for authenticating with the HMC. This is mutually exclusive with providing :literal:`hmc\_auth.session\_id`.

    | **required**: False
    | **type**: str


  password
    The password for authenticating with the HMC. This is mutually exclusive with providing :literal:`hmc\_auth.session\_id`.

    | **required**: False
    | **type**: str


  session_id
    HMC session ID to be used. This is mutually exclusive with providing :literal:`hmc\_auth.userid` and :literal:`hmc\_auth.password` and can be created as described in the :ref:`zhmc\_session module <zhmc_session_module>`.

    | **required**: False
    | **type**: str


  ca_certs
    Path name of certificate file or certificate directory to be used for verifying the HMC certificate. If null (default), the path name in the :envvar:`REQUESTS\_CA\_BUNDLE` environment variable or the path name in the :envvar:`CURL\_CA\_BUNDLE` environment variable is used, or if neither of these variables is set, the certificates in the Mozilla CA Certificate List provided by the 'certifi' Python package are used for verifying the HMC certificate.

    | **required**: False
    | **type**: str


  verify
    If True (default), verify the HMC certificate as specified in the :literal:`hmc\_auth.ca\_certs` parameter. If False, ignore what is specified in the :literal:`hmc\_auth.ca\_certs` parameter and do not verify the HMC certificate.

    | **required**: False
    | **type**: bool
    | **default**: True



cpc_name
  The name of the CPC that has the partition and the crypto adapters.

  | **required**: True
  | **type**: str


partition_name
  The name of the partition to which the crypto domains and crypto adapters are attached.

  | **required**: True
  | **type**: str


state
  The desired state for the crypto attachment. All states are fully idempotent within the limits of the properties that can be changed:

  \* :literal:`attached`\ : Ensures that the specified number of crypto adapters of the specified crypto type, and the specified range of domain index numbers in the specified access mode are attached to the partition.

  \* :literal:`detached`\ : Ensures that no crypto adapter and no crypto domains are attached to the partition.

  \* :literal:`facts`\ : Returns the crypto configuration of the partition.

  | **required**: True
  | **type**: str
  | **choices**: attached, detached, facts


adapter_count
  Only for :literal:`state=attached`\ : The number of crypto adapters the partition needs to have attached. The special value -1 means all adapters of the desired crypto type in the CPC. The :literal:`adapter\_names` and :literal:`adapter\_count` parameters are mutually exclusive and one of them must be specified.

  | **required**: False
  | **type**: int


crypto_type
  Only for :literal:`state=attached`\ : The crypto type of the crypto adapters that will be selected from when :literal:`adapter\_count` is specified. Ignored when :literal:`adapter\_names` is specified.

  | **required**: False
  | **type**: str
  | **default**: ep11
  | **choices**: ep11, cca, acc


adapter_names
  Only for :literal:`state=attached`\ : The names of the crypto adapters the partition needs to have attached. The :literal:`adapter\_names` and :literal:`adapter\_count` parameters are mutually exclusive and one of them must be specified.

  | **required**: False
  | **type**: list
  | **elements**: str


domain_range
  Only for :literal:`state=attached`\ : The domain range the partition needs to have attached, as a tuple of integers (min, max) that specify the inclusive range of domain index numbers. Other domains attached to the partition remain unchanged. The special value -1 for the max item means the maximum supported domain index number.

  | **required**: False
  | **type**: list
  | **elements**: int
  | **default**: [0, -1]


access_mode
  Only for :literal:`state=attached`\ : The access mode in which the crypto domains specified in :literal:`domain\_range` need to be attached.

  | **required**: False
  | **type**: str
  | **default**: usage
  | **choices**: usage, control


log_file
  File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.

  | **required**: False
  | **type**: str




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










Return Values
-------------


changed
  Indicates if any change has been made by the module. For :literal:`state=facts`\ , always will be false.

  | **returned**: always
  | **type**: bool

msg
  An error message that describes the failure.

  | **returned**: failure
  | **type**: str

changes
  The changes that were performed by the module.

  | **returned**: success
  | **type**: dict

  added-adapters
    Names of the adapters that were added to the partition

    | **type**: list
    | **elements**: str

  added-domains
    Domain index numbers of the crypto domains that were added to the partition

    | **type**: list
    | **elements**: str


crypto_configuration
  The crypto configuration of the partition after the changes performed by the module.

  | **returned**: success
  | **type**: dict
  | **sample**:

    .. code-block:: json

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
                "control_domains": [],
                "domain_config": {
                    "10": "usage",
                    "11": "usage"
                },
                "usage_domains": [
                    10,
                    11
                ]
            }
        }

  {name}
    Partition name

    | **type**: dict

    adapters
      Attached crypto adapters

      | **type**: dict

      {name}
        Adapter name

        | **type**: dict

        name
          Adapter name

          | **type**: str

        {property}
          Additional properties of the adapter, as described in the data model of the 'Adapter' object in the :ref:`HMC API <HMC API>` book. The property names have hyphens (-) as described in that book.

          | **type**: raw



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
      | **elements**: str

    control_domains
      Domain index numbers of the crypto domains attached in control mode

      | **type**: list
      | **elements**: str



