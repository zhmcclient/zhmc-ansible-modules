
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_storage_group_attachment.py

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


Requirements
------------

- The targeted Z system must be of generation z14 or later (to have the "dpm-storage-management" firmware feature) and must be in the Dynamic Partition Manager (DPM) operational mode.
- The HMC userid must have these task permissions: 'Configure Storage - System Programmer', 'Partition Details'.
- The HMC userid must have object-access permissions to these objects: Target partitions, target storage groups, target CPCs.




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
    The userid (username) for authenticating with the HMC. This is mutually exclusive with providing \ :literal:`session\_id`\ .

    | **required**: False
    | **type**: str


  password
    The password for authenticating with the HMC. This is mutually exclusive with providing \ :literal:`session\_id`\ .

    | **required**: False
    | **type**: str


  session_id
    HMC session ID to be used. This is mutually exclusive with providing \ :literal:`userid`\  and \ :literal:`password`\  and can be created as described in :ref:\`zhmc\_session\_module\`.

    | **required**: False
    | **type**: str


  ca_certs
    Path name of certificate file or certificate directory to be used for verifying the HMC certificate. If null (default), the path name in the 'REQUESTS\_CA\_BUNDLE' environment variable or the path name in the 'CURL\_CA\_BUNDLE' environment variable is used, or if neither of these variables is set, the certificates in the Mozilla CA Certificate List provided by the 'certifi' Python package are used for verifying the HMC certificate.

    | **required**: False
    | **type**: str


  verify
    If True (default), verify the HMC certificate as specified in the \ :literal:`ca\_certs`\  parameter. If False, ignore what is specified in the \ :literal:`ca\_certs`\  parameter and do not verify the HMC certificate.

    | **required**: False
    | **type**: bool
    | **default**: True



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
  The desired state for the storage group attachment. All states are fully idempotent within the limits of the properties that can be changed, unless otherwise stated:

  \* \ :literal:`detached`\ : Ensures that the storage group is not attached to the partition. If the storage group is currently attached to the partition and the partition is currently active, the module will fail (this is an idempotency limitation).

  \* \ :literal:`attached`\ : Ensures that the storage group is attached to the partition.

  \* \ :literal:`facts`\ : Returns the attachment status.

  | **required**: True
  | **type**: str
  | **choices**: detached, attached, facts


log_file
  File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.

  | **required**: False
  | **type**: str




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


changed
  Indicates if any change has been made by the module. For \ :literal:`state=facts`\ , always will be false.

  | **returned**: always
  | **type**: bool

msg
  An error message that describes the failure.

  | **returned**: failure
  | **type**: str

storage_group_attachment
  Attachment state of the storage group. If no check mode was requested, the attachment state after any changes is returned. If check mode was requested, the actual attachment state is returned.

  | **returned**: success
  | **type**: dict
  | **sample**:

    .. code-block:: json

        {
            "attached": false
        }

  attached
    Attachment state of the storage group: Indicates whether the storage group is attached to the partition.

    | **type**: bool


