
:github_url: https://github.com/IBM/ibm_zos_zosmf/tree/master/plugins/modules/zhmc_storage_volume.py

.. _zhmc_storage_volume_module:


zhmc_storage_volume -- Create storage volumes
=============================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gather facts about a storage volume in a storage group associated with a CPC (Z system).
- Create, delete, or update a storage volume in a storage group associated with a CPC.





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
  The name of the CPC associated with the storage group containing the target storage volume.


  | **required**: True
  | **type**: str


     
storage_group_name
  The name of the storage group containing the target storage volume.


  | **required**: True
  | **type**: str


     
name
  The name of the target storage volume.


  | **required**: True
  | **type**: str


     
state
  The desired state for the target storage volume:

  * ``absent``: Ensures that the storage volume does not exist in the specified storage group.

  * ``present``: Ensures that the storage volume exists in the specified storage group, and has the specified properties.

  * ``facts``: Does not change anything on the storage volume and returns the storage volume properties.


  | **required**: True
  | **type**: str
  | **choices**: absent, present, facts


     
properties
  Dictionary with desired properties for the storage volume. Used for ``state=present``; ignored for ``state=absent|facts``. Dictionary key is the property name with underscores instead of hyphens, and dictionary value is the property value in YAML syntax. Integer properties may also be provided as decimal strings.

  The possible input properties in this dictionary are the properties defined as writeable in the data model for Storage Volume resources (where the property names contain underscores instead of hyphens), with the following exceptions:

  * ``name``: Cannot be specified because the name has already been specified in the ``name`` module parameter.

  Properties omitted in this dictionary will remain unchanged when the storage volume already exists, and will get the default value defined in the data model for storage volumes in the :term:`HMC API` when the storage volume is being created.


  | **required**: False
  | **type**: dict


     
log_file
  File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.


  | **required**: False
  | **type**: str


     
_faked_session
  An internal parameter used for testing the module.


  | **required**: False
  | **type**: raw




Examples
--------

.. code-block:: yaml+jinja

   
   ---
   # Note: The following examples assume that some variables named 'my_*' are set.

   - name: Gather facts about a storage volume
     zhmc_storage_volume:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       storage_group_name: "{{ my_storage_group_name }}"
       name: "{{ my_storage_volume_name }}"
       state: facts
     register: sv1

   - name: Ensure the storage volume does not exist
     zhmc_storage_volume:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       storage_group_name: "{{ my_storage_group_name }}"
       name: "{{ my_storage_volume_name }}"
       state: absent

   - name: Ensure the storage volume exists
     zhmc_storage_volume:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       storage_group_name: "{{ my_storage_group_name }}"
       name: "{{ my_storage_volume_name }}"
       state: present
       properties:
         description: "Example storage volume 1"
         size: 1
     register: sv1





Notes
-----

.. note::
   This module manages only the knowledge of the Z system about its storage, but does not perform any actions against the storage subsystems or SAN switches attached to the Z system.







Return Values
-------------


   storage_volume
        For ``state=absent``, an empty dictionary.

        For ``state=present|facts``, a dictionary with the resource properties of the storage volume, indicating the state after changes from this module (if any) have been applied.


        | **returned**: success
        | **type**: dict


    name
          Storage volume name


          | **type**: str



    {property}
          Additional properties of the storage volume, as described in the :term:`HMC API` (using hyphens (-) in the property names).


          | **type**: 



    type
          Type of the storage volume ('fc' or 'fcp'), as defined in its storage group.


          | **type**: str





