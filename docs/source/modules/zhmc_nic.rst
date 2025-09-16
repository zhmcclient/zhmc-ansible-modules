
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_nic.py

.. _zhmc_nic_module:
.. _ibm.ibm_zhmc.zhmc_nic_module:


zhmc_nic -- Manage a NIC of a partition (DPM mode)
==================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gather facts about a NIC (virtual Network Interface Card) in a partition of a CPC (Z system).
- Create, update, or delete a NIC in a partition.
- Note that the Ansible module zhmc\_partition can be used to gather facts about existing NICs of a partition.


Requirements
------------

- The targeted Z system must be in the Dynamic Partition Manager (DPM) operational mode.
- The HMC userid must have these task permissions: 'Partition Details'.
- The HMC userid must have object-access permissions to these objects: Partitions of the target NICs, CPCs of these partitions, network adapters backing the target NICs.




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
  The name of the CPC with the partition containing the NIC.

  | **required**: True
  | **type**: str


partition_name
  The name of the partition containing the NIC.

  | **required**: True
  | **type**: str


name
  The name of the target NIC that is managed. If the NIC needs to be created, this value becomes its name.

  | **required**: True
  | **type**: str


state
  The desired state for the NIC. All states are fully idempotent within the limits of the properties that can be changed:

  \* :literal:`absent`\ : Ensures that the NIC does not exist in the specified partition.

  \* :literal:`present`\ : Ensures that the NIC exists in the specified partition and has the specified properties.

  \* :literal:`facts`\ : Returns the NIC properties.

  | **required**: True
  | **type**: str
  | **choices**: absent, present, facts


properties
  Dictionary with input properties for the NIC, for :literal:`state=present`. Key is the property name with underscores instead of hyphens, and value is the property value in YAML syntax. Integer properties may also be provided as decimal strings. Will be ignored for :literal:`state=absent`.

  The possible input properties in this dictionary are the properties defined as writeable in the data model for NIC resources (where the property names contain underscores instead of hyphens), with the following exceptions:

  \* :literal:`name`\ : Cannot be specified because the name has already been specified in the :literal:`name` module parameter.

  \* :literal:`network\_adapter\_port\_uri` and :literal:`virtual\_switch\_uri`\ : Cannot be specified because this information is specified using the artificial properties :literal:`adapter\_name` and :literal:`adapter\_port`.

  \* :literal:`adapter\_name`\ : The name of the adapter that has the port backing the target NIC. Used for all adapter families (ROCE, OSA, Hipersockets).

  \* :literal:`adapter\_port`\ : The port index of the adapter port backing the target NIC. Used for all adapter families (ROCE, OSA, Hipersockets).

  Properties omitted in this dictionary will remain unchanged when the NIC already exists, and will get the default value defined in the data model for NICs when the NIC is being created.

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

   - name: Ensure NIC exists in the partition
     zhmc_nic:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       partition_name: "{{ my_partition_name }}"
       name: "{{ my_nic_name }}"
       state: present
       properties:
         adapter_name: "OSD 0128 A13B-13"
         adapter_port: 0
         description: "The port to our data network"
         device_number: "023F"
     register: nic1

   - name: Ensure NIC does not exist in the partition
     zhmc_nic:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       partition_name: "{{ my_partition_name }}"
       name: "{{ my_nic_name }}"
       state: absent

   - name: Gather facts about a NIC
     zhmc_nic:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       partition_name: "{{ my_partition_name }}"
       name: "{{ my_nic_name }}"
       state: facts
     register: nic1










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

nic
  For :literal:`state=absent`\ , an empty dictionary.

  For :literal:`state=present\|facts`\ , the resource properties of the NIC after any changes.

  | **returned**: success
  | **type**: dict
  | **sample**:

    .. code-block:: json

        {
            "adapter-id": "128",
            "adapter-name": "OSD_128_MGMT_NET2_30",
            "adapter-port": 0,
            "class": "nic",
            "description": "HAMGMT",
            "device-number": "0004",
            "element-id": "5956e97a-f433-11ea-b67c-00106f239d19",
            "element-uri": "/api/partitions/32323df4-f433-11ea-b67c-00106f239d19/nics/5956e97a-f433-11ea-b67c-00106f239d19",
            "mac-address": "02:d2:4d:80:b9:88",
            "name": "HAMGMT0",
            "parent": "/api/partitions/32323df4-f433-11ea-b67c-00106f239d19",
            "ssc-ip-address": null,
            "ssc-ip-address-type": null,
            "ssc-management-nic": false,
            "ssc-mask-prefix": null,
            "type": "osd",
            "virtual-switch-uri": "/api/virtual-switches/db2f0bec-e578-11e8-bd0a-00106f239c31",
            "vlan-id": null,
            "vlan-type": null
        }

  name
    NIC name

    | **type**: str

  {property}
    Additional properties of the NIC, as described in the data model of the 'NIC' element object of the 'Partition' object in the :ref:`HMC API <HMC API>` book. The property names have hyphens (-) as described in that book.

    | **type**: raw

  adapter-id
    Adapter ID (PCHID) of the backing adapter of the NIC.

    | **type**: str

  adapter-name
    Name of the backing adapter of the NIC.

    | **type**: str

  adapter-port
    Port index of the backing port of the NIC.

    | **type**: int


