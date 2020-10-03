.. _zhmc_storage_volume_module:


zhmc_storage_volume -- Manages storage volumes of Z systems.
============================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Gather facts about a storage volume in a storage group associated with a CPC (Z system).

Create, delete, or update a storage volume in a storage group associated with a CPC.



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
    The name of the CPC associated with the storage group containing the target storage volume.


  storage_group_name (True, str, None)
    The name of the storage group containing the target storage volume.


  name (True, str, None)
    The name of the target storage volume.


  state (True, str, None)
    The desired state for the target storage volume:

    * ``absent``: Ensures that the storage volume does not exist in the specified storage group.

    * ``present``: Ensures that the storage volume exists in the specified storage group, and has the specified properties.

    * ``facts``: Does not change anything on the storage volume and returns the storage volume properties.


  properties (False, dict, None)
    Dictionary with desired properties for the storage volume. Used for ``state=present``; ignored for ``state=absent|facts``. Dictionary key is the property name with underscores instead of hyphens, and dictionary value is the property value in YAML syntax. Integer properties may also be provided as decimal strings.

    The possible input properties in this dictionary are the properties defined as writeable in the data model for Storage Volume resources (where the property names contain underscores instead of hyphens), with the following exceptions:

    * ``name``: Cannot be specified because the name has already been specified in the ``name`` module parameter.

    Properties omitted in this dictionary will remain unchanged when the storage volume already exists, and will get the default value defined in the data model for storage volumes in the HMC API book when the storage volume is being created.


  log_file (False, str, None)
    File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.


  faked_session (False, raw, None)
    A ``zhmcclient_mock.FakedSession`` object that has a mocked HMC set up. If not null, this session will be used instead of connecting to the HMC specified in ``hmc_host``. This is used for testing purposes only.





Notes
-----

.. note::
   - This module manages only the knowledge of the Z system about its storage, but does not perform any actions against the storage subsystems or SAN switches attached to the Z system.




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




Return Values
-------------

storage_volume (success, dict, C({
  "name": "sv-1",
  "description": "storage volume #1",
  ...
})
)
  For ``state=absent``, an empty dictionary.

  For ``state=present|facts``, a dictionary with the resource properties of the storage volume, indicating the state after changes from this module (if any) have been applied. The dictionary keys are the exact property names as described in the data model for the resource, i.e. they contain hyphens (-), not underscores (_). The dictionary values are the property values using the Python representations described in the documentation of the zhmcclient Python package. The additional artificial properties are:

  * ``type``: Type of the storage volume ('fc' or 'fcp'), as defined in its storage group.





Status
------




- This module is guaranteed to have backward compatible interface changes going forward. *[stableinterface]*


- This module is maintained by community.



Authors
~~~~~~~

- Andreas Maier (@andy-maier)
- Andreas Scheuring (@scheuran)
- Juergen Leopold (@leopoldjuergen)

