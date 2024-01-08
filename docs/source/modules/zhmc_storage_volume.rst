
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_storage_volume.py

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


Requirements
------------

- The targeted Z system must be of generation z14 or later (to have the "dpm-storage-management" firmware feature) and must be in the Dynamic Partition Manager (DPM) operational mode.
- The HMC userid must have these task permissions: 'Configure Storage - System Programmer'.
- The HMC userid must have object-access permissions to these objects: Target storage groups.




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
  The desired state for the storage volume. All states are fully idempotent within the limits of the properties that can be changed:

  \* \ :literal:`absent`\ : Ensures that the storage volume does not exist in the specified storage group.

  \* \ :literal:`present`\ : Ensures that the storage volume exists in the specified storage group, and has the specified properties.

  \* \ :literal:`facts`\ : Returns the storage volume properties.

  | **required**: True
  | **type**: str
  | **choices**: absent, present, facts


properties
  Dictionary with desired properties for the storage volume. Used for \ :literal:`state=present`\ ; ignored for \ :literal:`state=absent|facts`\ . Dictionary key is the property name with underscores instead of hyphens, and dictionary value is the property value in YAML syntax. Integer properties may also be provided as decimal strings.

  The possible input properties in this dictionary are the properties defined as writeable in the data model for Storage Volume resources (where the property names contain underscores instead of hyphens), with the following exceptions:

  \* \ :literal:`name`\ : Cannot be specified because the name has already been specified in the \ :literal:`name`\  module parameter.

  Properties omitted in this dictionary will remain unchanged when the storage volume already exists, and will get the default value defined in the data model for storage volumes in the :term:\`HMC API\` when the storage volume is being created.

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


changed
  Indicates if any change has been made by the module. For \ :literal:`state=facts`\ , always will be false.

  | **returned**: always
  | **type**: bool

msg
  An error message that describes the failure.

  | **returned**: failure
  | **type**: str

storage_volume
  For \ :literal:`state=absent`\ , an empty dictionary.

  For \ :literal:`state=present|facts`\ , the resource properties of the storage volume after any changes.

  | **returned**: success
  | **type**: dict
  | **sample**:

    .. code-block:: json

        {
            "active-size": 128.0,
            "class": "storage-volume",
            "description": "Boot volume",
            "element-id": "f02e2632-200a-11e9-8748-00106f239c31",
            "element-uri": "/api/storage-groups/edd782f2-200a-11e9-a142-00106f239c31/storage-volumes/f02e2632-200a-11e9-8748-00106f239c31",
            "fulfillment-state": "complete",
            "name": "MGMT1_MGMT1-boot",
            "parent": "/api/storage-groups/edd782f2-200a-11e9-a142-00106f239c31",
            "paths": [
                {
                    "device-number": "0015",
                    "logical-unit-number": "0000000000000000",
                    "partition-uri": "/api/partitions/009c0f4c-3588-11e9-bad3-00106f239d19",
                    "target-world-wide-port-name": "5005076810260382"
                }
            ],
            "size": 128.0,
            "type": "fcp",
            "usage": "boot",
            "uuid": "600507681081001D4800000000000083"
        }

  name
    Storage volume name

    | **type**: str

  type
    Type of the storage volume ('fc' or 'fcp'), as defined in its storage group.

    | **type**: str

  {property}
    Additional properties of the storage volume, as described in the data model of the 'Storage Volume' element object of the 'Storage Group' object in the :term:\`HMC API\` book. The property names have hyphens (-) as described in that book.



