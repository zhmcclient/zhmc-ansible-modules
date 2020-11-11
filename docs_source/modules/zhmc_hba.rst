.. _zhmc_hba_module:


zhmc_hba -- Manages HBAs in partitions of Z systems.
====================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Create, update, or delete an HBA (virtual Host Bus Adapter) in a partition of a CPC (Z system).

Note that the Ansible module zhmc_partition can be used to gather facts about existing HBAs of a partition.



Requirements
------------
The below requirements are needed on the host that executes this module.

- Access to the WS API of the HMC of the targeted Z system (see :term:`HMC API`). The targeted Z system must be in the Dynamic Partition Manager (DPM) operational mode.
- The targeted Z system must be a z13 generation. The z14 and later generations manage HBAs automatically via the "dpm-storage-management" firmware feature.
- Python package zhmcclient >=0.14.0



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
    The name of the CPC with the partition containing the HBA.


  partition_name (True, str, None)
    The name of the partition containing the HBA.


  name (True, str, None)
    The name of the target HBA that is managed. If the HBA needs to be created, this value becomes its name.


  state (True, str, None)
    The desired state for the target HBA:

    ``absent``: Ensures that the HBA does not exist in the specified partition.

    ``present``: Ensures that the HBA exists in the specified partition and has the specified properties.


  properties (False, dict, None)
    Dictionary with input properties for the HBA, for ``state=present``. Key is the property name with underscores instead of hyphens, and value is the property value in YAML syntax. Integer properties may also be provided as decimal strings. Will be ignored for ``state=absent``.

    The possible input properties in this dictionary are the properties defined as writeable in the data model for HBA resources (where the property names contain underscores instead of hyphens), with the following exceptions:

    * ``name``: Cannot be specified because the name has already been specified in the ``name`` module parameter.

    * ``adapter_port_uri``: Cannot be specified because this information is specified using the artificial properties ``adapter_name`` and ``adapter_port``.

    * ``adapter_name``: The name of the adapter that has the port backing the target HBA. Cannot be changed after the HBA exists.

    * ``adapter_port``: The port index of the adapter port backing the target HBA. Cannot be changed after the HBA exists.

    Properties omitted in this dictionary will remain unchanged when the HBA already exists, and will get the default value defined in the data model for HBAs when the HBA is being created.


  log_file (False, str, None)
    File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.


  faked_session (False, raw, None)
    A ``zhmcclient_mock.FakedSession`` object that has a mocked HMC set up. If not null, this session will be used instead of connecting to the HMC specified in ``hmc_host``. This is used for testing purposes only.









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

hba (success, dict, )
  For ``state=absent``, an empty dictionary.

  For ``state=present``, a dictionary with the resource properties of the HBA after changes, if any.


  name (, str, )
    HBA name


  {property} (, any, )
    Additional properties of the HBA, as described in the :term:`HMC API` (using hyphens (-) in the property names).






Status
------




- This module is guaranteed to have backward compatible interface changes going forward. *[stableinterface]*


- This module is maintained by community.



Authors
~~~~~~~

- Andreas Maier (@andy-maier)
- Andreas Scheuring (@scheuran)
- Juergen Leopold (@leopoldjuergen)

