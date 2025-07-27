
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_hba.py

.. _zhmc_hba_module:
.. _ibm.ibm_zhmc.zhmc_hba_module:


zhmc_hba -- Manage an HBA of a partition (z13 only, DPM mode)
=============================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Create, update, or delete an HBA (virtual Host Bus Adapter) in a partition of a CPC (Z system).
- Note that the Ansible module zhmc\_partition can be used to gather facts about existing HBAs of a partition.


Requirements
------------

- The targeted Z system must be a z13 generation and must be in the Dynamic Partition Manager (DPM) operational mode. The z14 and later generations in DPM mode manage HBAs automatically via the "dpm-storage-management" firmware feature.
- The HMC userid must have these task permissions: 'Partition Details'.
- The HMC userid must have object-access permissions to these objects: Partitions of the target HBAs, CPCs of these partitions, storage adapters backing the target HBAs.




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
  The name of the CPC with the partition containing the HBA.

  | **required**: True
  | **type**: str


partition_name
  The name of the partition containing the HBA.

  | **required**: True
  | **type**: str


name
  The name of the target HBA that is managed. If the HBA needs to be created, this value becomes its name.

  | **required**: True
  | **type**: str


state
  The desired state for the HBA. All states are fully idempotent within the limits of the properties that can be changed:

  \* :literal:`absent`\ : Ensures that the HBA does not exist in the specified partition.

  \* :literal:`present`\ : Ensures that the HBA exists in the specified partition and has the specified properties.

  | **required**: True
  | **type**: str
  | **choices**: absent, present


properties
  Dictionary with input properties for the HBA, for :literal:`state=present`. Key is the property name with underscores instead of hyphens, and value is the property value in YAML syntax. Integer properties may also be provided as decimal strings. Will be ignored for :literal:`state=absent`.

  The possible input properties in this dictionary are the properties defined as writeable in the data model for HBA resources (where the property names contain underscores instead of hyphens), with the following exceptions:

  \* :literal:`name`\ : Cannot be specified because the name has already been specified in the :literal:`name` module parameter.

  \* :literal:`adapter\_port\_uri`\ : Cannot be specified because this information is specified using the artificial properties :literal:`adapter\_name` and :literal:`adapter\_port`.

  \* :literal:`adapter\_name`\ : The name of the adapter that has the port backing the target HBA. Cannot be changed after the HBA exists.

  \* :literal:`adapter\_port`\ : The port index of the adapter port backing the target HBA. Cannot be changed after the HBA exists.

  Properties omitted in this dictionary will remain unchanged when the HBA already exists, and will get the default value defined in the data model for HBAs when the HBA is being created.

  | **required**: False
  | **type**: dict


log_file
  File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.

  | **required**: False
  | **type**: str




Examples
--------

.. code-block:: yaml+jinja

   
   ---
   # Note: The following examples assume that some variables named 'my_*' are set.

   - name: Ensure HBA exists in the partition
     zhmc_partition:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       partition_name: "{{ my_partition_name }}"
       name: "{{ my_hba_name }}"
       state: present
       properties:
         adapter_name: FCP-1
         adapter_port: 0
         description: "The port to our V7K #1"
         device_number: "123F"
     register: hba1

   - name: Ensure HBA does not exist in the partition
     zhmc_partition:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       partition_name: "{{ my_partition_name }}"
       name: "{{ my_hba_name }}"
       state: absent










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

hba
  For :literal:`state=absent`\ , an empty dictionary.

  For :literal:`state=present`\ , the resource properties of the HBA after any changes.

  | **returned**: success
  | **type**: dict

  name
    HBA name

    | **type**: str

  {property}
    Additional properties of the HBA, as described in the data model of the 'HBA' element object of the 'Partition' object in the :ref:`HMC API <HMC API>` book. The property names have hyphens (-) as described in that book.

    | **type**: raw


