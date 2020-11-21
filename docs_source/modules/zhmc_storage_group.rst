
:github_url: https://github.com/IBM/ibm_zos_zosmf/tree/master/plugins/modules/zhmc_storage_group.py

.. _zhmc_storage_group_module:


zhmc_storage_group -- Create storage groups
===========================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gather facts about a storage group associated with a CPC (Z system), including its storage volumes and virtual storage resources.
- Create, delete, or update a storage group associated with a CPC.





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
  The name of the CPC associated with the target storage group.


  | **required**: True
  | **type**: str


     
name
  The name of the target storage group.


  | **required**: True
  | **type**: str


     
state
  The desired state for the target storage group:

  * ``absent``: Ensures that the storage group does not exist. If the storage group is currently attached to any partitions, the module will fail.

  * ``present``: Ensures that the storage group exists and is associated with the specified CPC, and has the specified properties. The attachment state of the storage group to a partition is not changed.

  * ``facts``: Does not change anything on the storage group and returns the storage group properties.


  | **required**: True
  | **type**: str
  | **choices**: absent, present, facts


     
properties
  Dictionary with desired properties for the storage group. Used for ``state=present``; ignored for ``state=absent|facts``. Dictionary key is the property name with underscores instead of hyphens, and dictionary value is the property value in YAML syntax. Integer properties may also be provided as decimal strings.

  The possible input properties in this dictionary are the properties defined as writeable in the data model for Storage Group resources (where the property names contain underscores instead of hyphens), with the following exceptions:

  * ``name``: Cannot be specified because the name has already been specified in the ``name`` module parameter.

  * ``type``: Cannot be changed once the storage group exists.

  Properties omitted in this dictionary will remain unchanged when the storage group already exists, and will get the default value defined in the data model for storage groups in the :term:`HMC API` when the storage group is being created.


  | **required**: False
  | **type**: dict


     
expand
  Boolean that controls whether the returned storage group contains additional artificial properties that expand certain URI or name properties to the full set of resource properties (see description of return values of this module).


  | **required**: False
  | **type**: bool


     
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

   - name: Gather facts about a storage group
     zhmc_storage_group:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       name: "{{ my_storage_group_name }}"
       state: facts
       expand: true
     register: sg1

   - name: Ensure the storage group does not exist
     zhmc_storage_group:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       name: "{{ my_storage_group_name }}"
       state: absent

   - name: Ensure the storage group exists
     zhmc_storage_group:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       name: "{{ my_storage_group_name }}"
       state: present
       expand: true
       properties:
         description: "Example storage group 1"
         type: fcp
         shared: false
         connectivity: 4
         max-partitions: 1
     register: sg1





Notes
-----

.. note::
   This module manages only the knowledge of the Z system about its storage, but does not perform any actions against the storage subsystems or SAN switches attached to the Z system.

   Attachment of storage groups to and from partitions is managed by the Ansible module zhmc_storage_group_attachment.







Return Values
-------------


   storage_group
        For ``state=absent``, an empty dictionary.

        For ``state=present|facts``, a dictionary with the resource properties of the target storage group, plus additional artificial properties as described below.


        | **returned**: success
        | **type**: dict


    name
          Storage group name


          | **type**: str



    {property}
          Additional properties of the storage group, as described in the :term:`HMC API` (using hyphens (-) in the property names).


          | **type**: 



    attached-partition-names
          Names of the partitions to which the storage group is attached.


          | **type**: list



    cpc-name
          Name of the CPC that is associated to this storage group.


          | **type**: str



    candidate-adapter-ports
          Only if expand was requested: List of candidate storage adapter ports of the storage group.


          | **returned**: success+expand
          | **type**: list


     name
            Storage port name


            | **type**: str



     index
            Storage port index


            | **type**: int



     {property}
            Additional properties of the storage port, as described in the :term:`HMC API` (using hyphens (-) in the property names).


            | **type**: 



     parent-adapter
            Storage adapter of the port.


            | **type**: dict


      name
              Storage adapter name


              | **type**: str



      {property}
              Additional properties of the storage adapter, as described in the :term:`HMC API` (using hyphens (-) in the property names).


              | **type**: 







    storage-volumes
          Only if expand was requested: List of storage volumes of the storage group.


          | **returned**: success+expand
          | **type**: list


     name
            Storage volume name


            | **type**: str



     {property}
            Additional properties of the storage volume, as described in the :term:`HMC API` (using hyphens (-) in the property names).


            | **type**: 





    virtual-storage-resources
          Only if expand was requested: List of virtual storage resources of the storage group.


          | **returned**: success+expand
          | **type**: list


     {property}
            Properties of the virtual storage resource, as described in the :term:`HMC API` (using hyphens (-) in the property names).


            | **type**: 





    attached-partitions
          Only if expand was requested: List of partitions to which the storage group is attached.


          | **returned**: success+expand
          | **type**: list


     {property}
            Properties of the partition, as described in the :term:`HMC API` (using hyphens (-) in the property names).


            | **type**: 





    cpc
          Only if expand was requested: The CPC that is associated to this storage group.


          | **returned**: success+expand
          | **type**: list


     {property}
            Properties of the CPC, as described in the :term:`HMC API` (using hyphens (-) in the property names).


            | **type**: 







