.. _zhmc_storage_group_attachment_module:


zhmc_storage_group_attachment -- Manages the attachment of storage groups to partitions of Z systems.
=====================================================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Gather facts about the attachment of a storage group to a partition of a CPC (Z system).

Attach and detach a storage group to and from a partition.



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
    The name of the CPC that has the partition and is associated with the storage group.


  storage_group_name (True, str, None)
    The name of the storage group for the attachment.


  partition_name (True, str, None)
    The name of the partition for the attachment.


  state (True, str, None)
    The desired state for the attachment:

    * ``detached``: Ensures that the storage group is not attached to the partition. If the storage group is currently attached to the partition and the partition is currently active, the module will fail.

    * ``attached``: Ensures that the storage group is attached to the partition.

    * ``facts``: Does not change anything on the attachment and returns the attachment status.


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




Return Values
-------------

storage_group_attachment (success, dict, C({"attached": true})
)
  A dictionary with a single key 'attached' whose boolean value indicates whether the storage group is now actually attached to the partition. If check mode was requested, the actual (i.e. not the desired) attachment state is returned.





Status
------




- This module is guaranteed to have backward compatible interface changes going forward. *[stableinterface]*


- This module is maintained by community.



Authors
~~~~~~~

- Andreas Maier (@andy-maier)
- Andreas Scheuring (@scheuran)
- Juergen Leopold (@leopoldjuergen)

