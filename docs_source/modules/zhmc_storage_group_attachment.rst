
:github_url: https://github.com/IBM/ibm_zos_zosmf/tree/master/plugins/modules/zhmc_storage_group_attachment.py

.. _zhmc_storage_group_attachment_module:


zhmc_storage_group_attachment -- Attach storage groups to partitions
====================================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gather facts about the attachment of a storage group to a partition of a CPC (Z system).
- Attach and detach a storage group to and from a partition.





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
  The name of the CPC that has the partition and is associated with the storage group.


  | **required**: True
  | **type**: str


     
storage_group_name
  The name of the storage group for the attachment.


  | **required**: True
  | **type**: str


     
partition_name
  The name of the partition for the attachment.


  | **required**: True
  | **type**: str


     
state
  The desired state for the attachment:

  * ``detached``: Ensures that the storage group is not attached to the partition. If the storage group is currently attached to the partition and the partition is currently active, the module will fail.

  * ``attached``: Ensures that the storage group is attached to the partition.

  * ``facts``: Does not change anything on the attachment and returns the attachment status.


  | **required**: True
  | **type**: str
  | **choices**: detached, attached, facts


     
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

   - name: Gather facts about the attachment
     zhmc_storage_group_attachment:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       storage_group_name: "{{ my_storage_group_name }}"
       partition_name: "{{ my_partition_name }}"
       state: facts
     register: sga1

   - name: Ensure the storage group is attached to the partition
     zhmc_storage_group_attachment:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       storage_group_name: "{{ my_storage_group_name }}"
       partition_name: "{{ my_partition_name }}"
       state: attached

   - name: "Ensure the storage group is not attached to the partition."
     zhmc_storage_group_attachment:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       storage_group_name: "{{ my_storage_group_name }}"
       partition_name: "{{ my_partition_name }}"
       state: detached





Notes
-----

.. note::
   This module manages only the knowledge of the Z system about its storage, but does not perform any actions against the storage subsystems or SAN switches attached to the Z system.







Return Values
-------------


   storage_group_attachment
        Attachment state of the storage group. If no check mode was requested, the attachment state after any changes is returned. If check mode was requested, the actual attachment state is returned.


        | **returned**: success
        | **type**: dict


    attached
          Attachment state of the storage group: Indicates whether the storage group is attached to the partition.


          | **type**: bool





