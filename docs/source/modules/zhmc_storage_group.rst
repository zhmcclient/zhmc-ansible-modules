.. _zhmc_storage_group_module:


zhmc_storage_group -- Manages storage groups of Z systems.
==========================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Gather facts about a storage group associated with a CPC (Z system), including its storage volumes and virtual storage resources.

Create, delete, or update a storage group associated with a CPC.



Requirements
------------
The below requirements are needed on the host that executes this module.

- Access to the WS API of the HMC of the targeted Z system. The targeted Z system must be in the Dynamic Partition Manager (DPM) operational mode.
- The Z system must be of generation z14 or later, to have the "dpm-storage-management" firmware feature.
- Python package zhmcclient >=0.20.0



Parameters
----------

  hmc_host (True, str, None)
    The hostname or IP address of the HMC.


  hmc_auth (True, dict, None)
    The authentication credentials for the HMC, as a dictionary of ``userid``, ``password``.


    userid (True, str, None)
      The userid (username) for authenticating with the HMC.


    password (True, str, None)
      The password for authenticating with the HMC.



  cpc_name (True, str, None)
    The name of the CPC associated with the target storage group.


  name (True, str, None)
    The name of the target storage group.


  state (True, str, None)
    The desired state for the target storage group:

    * ``absent``: Ensures that the storage group does not exist. If the storage group is currently attached to any partitions, the module will fail.

    * ``present``: Ensures that the storage group exists and is associated with the specified CPC, and has the specified properties. The attachment state of the storage group to a partition is not changed.

    * ``facts``: Does not change anything on the storage group and returns the storage group properties.


  properties (False, dict, None)
    Dictionary with desired properties for the storage group. Used for ``state=present``; ignored for ``state=absent|facts``. Dictionary key is the property name with underscores instead of hyphens, and dictionary value is the property value in YAML syntax. Integer properties may also be provided as decimal strings.

    The possible input properties in this dictionary are the properties defined as writeable in the data model for Storage Group resources (where the property names contain underscores instead of hyphens), with the following exceptions:

    * ``name``: Cannot be specified because the name has already been specified in the ``name`` module parameter.

    * ``type``: Cannot be changed once the storage group exists.

    Properties omitted in this dictionary will remain unchanged when the storage group already exists, and will get the default value defined in the data model for storage groups in the HMC API book when the storage group is being created.


  expand (False, bool, False)
    Boolean that controls whether the returned storage group contains additional artificial properties that expand certain URI or name properties to the full set of resource properties (see description of return values of this module).


  log_file (False, str, None)
    File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.


  faked_session (False, raw, None)
    A ``zhmcclient_mock.FakedSession`` object that has a mocked HMC set up. If not null, this session will be used instead of connecting to the HMC specified in ``hmc_host``. This is used for testing purposes only.





Notes
-----

.. note::
   - This module manages only the knowledge of the Z system about its storage, but does not perform any actions against the storage subsystems or SAN switches attached to the Z system.
   - Attachment of storage groups to and from partitions is managed by the Ansible module zhmc_storage_group_attachment.




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




Return Values
-------------

storage_group (success, dict, C({
  "name": "sg-1",
  "description": "storage group #1",
  ...
})
)
  For ``state=absent``, an empty dictionary.

  For ``state=present|facts``, a dictionary with the resource properties of the target storage group, plus additional artificial properties as described in the following list items. The dictionary keys are the exact property names as described in the data model for the resource, i.e. they contain hyphens (-), not underscores (_). The dictionary values are the property values using the Python representations described in the documentation of the zhmcclient Python package. The additional artificial properties are:

  * ``attached-partition-names``: List of partition names to which the storage group is attached.

  * ``cpc-name``: Name of the CPC that is associated to this storage group.

  * ``candidate-adapter-ports`` (only if expand was requested): List of candidate adapter ports of the storage group. Each port is represented as a dictionary of its properties; in addition each port has an artificial property ``parent-adapter`` which represents the adapter of the port. Each adapter is represented as a dictionary of its properties.

  * ``storage-volumes`` (only if expand was requested): List of storage volumes of the storage group. Each storage volume is represented as a dictionary of its properties.

  * ``virtual-storage-resources`` (only if expand was requested): List of virtual storage resources of the storage group. Each virtual storage resource is represented as a dictionary of its properties.

  * ``attached-partitions`` (only if expand was requested): List of partitions to which the storage group is attached. Each partition is represented as a dictionary of its properties.

  * ``cpc`` (only if expand was requested): The CPC that is associated to this storage group. The CPC is represented as a dictionary of its properties.





Status
------




- This module is guaranteed to have backward compatible interface changes going forward. *[stableinterface]*


- This module is maintained by community.



Authors
~~~~~~~

- Andreas Maier (@andy-maier)
- Andreas Scheuring (@scheuran)
- Juergen Leopold (@leopoldjuergen)

