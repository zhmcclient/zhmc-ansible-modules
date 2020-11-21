
:github_url: https://github.com/IBM/ibm_zos_zosmf/tree/master/plugins/modules/zhmc_hba.py

.. _zhmc_hba_module:


zhmc_hba -- Create HBAs in partitions
=====================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Create, update, or delete an HBA (virtual Host Bus Adapter) in a partition of a CPC (Z system).
- Note that the Ansible module zhmc_partition can be used to gather facts about existing HBAs of a partition.





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
  The desired state for the target HBA:

  ``absent``: Ensures that the HBA does not exist in the specified partition.

  ``present``: Ensures that the HBA exists in the specified partition and has the specified properties.


  | **required**: True
  | **type**: str
  | **choices**: absent, present


     
properties
  Dictionary with input properties for the HBA, for ``state=present``. Key is the property name with underscores instead of hyphens, and value is the property value in YAML syntax. Integer properties may also be provided as decimal strings. Will be ignored for ``state=absent``.

  The possible input properties in this dictionary are the properties defined as writeable in the data model for HBA resources (where the property names contain underscores instead of hyphens), with the following exceptions:

  * ``name``: Cannot be specified because the name has already been specified in the ``name`` module parameter.

  * ``adapter_port_uri``: Cannot be specified because this information is specified using the artificial properties ``adapter_name`` and ``adapter_port``.

  * ``adapter_name``: The name of the adapter that has the port backing the target HBA. Cannot be changed after the HBA exists.

  * ``adapter_port``: The port index of the adapter port backing the target HBA. Cannot be changed after the HBA exists.

  Properties omitted in this dictionary will remain unchanged when the HBA already exists, and will get the default value defined in the data model for HBAs when the HBA is being created.


  | **required**: False
  | **type**: dict


     
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


   hba
        For ``state=absent``, an empty dictionary.

        For ``state=present``, a dictionary with the resource properties of the HBA after changes, if any.


        | **returned**: success
        | **type**: dict


    name
          HBA name


          | **type**: str



    {property}
          Additional properties of the HBA, as described in the :term:`HMC API` (using hyphens (-) in the property names).


          | **type**: 





