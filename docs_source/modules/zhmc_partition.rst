.. _zhmc_partition_module:


zhmc_partition -- Create partitions
===================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Gather facts about a partition of a CPC (Z system), including its HBAs, NICs, and virtual functions.

Create, update, or delete a partition. The HBAs, NICs, and virtual functions of the partition are managed by separate Ansible modules.

Start or stop a partition.



Requirements
------------
The below requirements are needed on the host that executes this module.

- Access to the WS API of the HMC of the targeted Z system (see :term:`HMC API`). The targeted Z system must be in the Dynamic Partition Manager (DPM) operational mode.



Parameters
----------

  hmc_host (True, str, None)
    The hostname or IP address of the HMC.


  hmc_auth (True, dict, None)
    The authentication credentials for the HMC, as a dictionary of userid, password.


    userid (True, str, None)
      The userid (username) for authenticating with the HMC.


    password (True, str, None)
      The password for authenticating with the HMC.



  cpc_name (True, str, None)
    The name of the CPC with the target partition.


  name (True, str, None)
    The name of the target partition.


  state (True, str, None)
    The desired state for the target partition:

    ``absent``: Ensures that the partition does not exist in the specified CPC.

    ``stopped``: Ensures that the partition exists in the specified CPC, has the specified properties, and is in the 'stopped' status.

    ``active``: Ensures that the partition exists in the specified CPC, has the specified properties, and is in the 'active' or 'degraded' status.

    ``facts``: Does not change anything on the partition and returns the partition properties and the properties of its child resources (HBAs, NICs, and virtual functions).


  properties (False, dict, None)
    Dictionary with input properties for the partition, for ``state=stopped`` and ``state=active``. Key is the property name with underscores instead of hyphens, and value is the property value in YAML syntax. Integer properties may also be provided as decimal strings. Will be ignored for ``state=absent``.

    The possible input properties in this dictionary are the properties defined as writeable in the data model for Partition resources (where the property names contain underscores instead of hyphens), with the following exceptions:

    * ``name``: Cannot be specified because the name has already been specified in the ``name`` module parameter.

    * ``type``: Cannot be changed once the partition exists, because updating it is not supported.

    * ``boot_storage_device``: Cannot be specified because this information is specified using the artificial property ``boot_storage_hba_name``.

    * ``boot_network_device``: Cannot be specified because this information is specified using the artificial property ``boot_network_nic_name``.

    * ``boot_storage_hba_name``: The name of the HBA whose URI is used to construct ``boot_storage_device``. Specifying it requires that the partition exists.

    * ``boot_network_nic_name``: The name of the NIC whose URI is used to construct ``boot_network_device``. Specifying it requires that the partition exists.

    * ``crypto_configuration``: The crypto configuration for the partition, in the format of the ``crypto-configuration`` property of the partition (see :term:`HMC API` for details), with the exception that adapters are specified with their names in field ``crypto_adapter_names`` instead of their URIs in field ``crypto_adapter_uris``. If the ``crypto_adapter_names`` field is null, all crypto adapters of the CPC will be used.

    Properties omitted in this dictionary will remain unchanged when the partition already exists, and will get the default value defined in the data model for partitions in the :term:`HMC API` when the partition is being created.


  expand_storage_groups (False, bool, False)
    Boolean that controls whether the returned partition contains an additional artificial property 'storage-groups' that is the list of storage groups attached to the partition, with properties as described for the zhmc_storage_group module with expand=true.


  expand_crypto_adapters (False, bool, False)
    Boolean that controls whether the returned partition contains an additional artificial property 'crypto-adapters' in its 'crypto-configuration' property that is the list of crypto adapters attached to the partition, with properties as described for the zhmc_adapter module.


  log_file (False, str, None)
    File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.


  faked_session (False, raw, None)
    A ``zhmcclient_mock.FakedSession`` object that has a mocked HMC set up. If not null, this session will be used instead of connecting to the HMC specified in ``hmc_host``. This is used for testing purposes only.







See Also
--------

.. seealso::

   :ref:`zhmc_hba_module`
      The official documentation on the **zhmc_hba** module.
   :ref:`zhmc_nic_module`
      The official documentation on the **zhmc_nic** module.
   :ref:`zhmc_virtual_function_module`
      The official documentation on the **zhmc_virtual_function** module.


Examples
--------

.. code-block:: yaml+jinja

    
    ---
    # Note: The following examples assume that some variables named 'my_*' are set.

    # Because configuring LUN masking in the SAN requires the host WWPN, and the
    # host WWPN is automatically assigned and will be known only after an HBA has
    # been added to the partition, the partition needs to be created in stopped
    # state. Also, because the HBA has not yet been created, the boot
    # configuration cannot be done yet:
    - name: Ensure the partition exists and is stopped
      zhmc_partition:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_partition_name }}"
        state: stopped
        properties:
          description: "zhmc Ansible modules: Example partition 1"
          ifl_processors: 2
          initial_memory: 1024
          maximum_memory: 1024
      register: part1

    # After an HBA has been added (see Ansible module zhmc_hba), and LUN masking
    # has been configured in the SAN, and a bootable image is available at the
    # configured LUN and target WWPN, the partition can be configured for boot
    # from the FCP LUN and can be started:
    - name: Configure boot device and start the partition
      zhmc_partition:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_partition_name }}"
        state: active
        properties:
          boot_device: storage-adapter
          boot_storage_device_hba_name: hba1
          boot_logical_unit_number: 00000000001
          boot_world_wide_port_name: abcdefabcdef
      register: part1

    - name: Ensure the partition does not exist
      zhmc_partition:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_partition_name }}"
        state: absent

    - name: Define crypto configuration
      zhmc_partition:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_partition_name }}"
        state: active
        properties:
          crypto_configuration:
            crypto_adapter_names:
              - adapter1
              - adapter2
            crypto_domain_configurations:
              - domain_index: 0
                access_mode: control-usage
              - domain_index: 1
                access_mode: control
      register: part1

    - name: Gather facts about a partition
      zhmc_partition:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_partition_name }}"
        state: facts
        expand_storage_groups: true
        expand_crypto_adapters: true
      register: part1




Return Values
-------------

partition (success, dict, )
  For ``state=absent``, an empty dictionary.

  For ``state=stopped`` and ``state=active``, a dictionary with the resource properties of the partition after changes, if any.

  For ``state=facts``, a dictionary with the resource properties of the partition, including its child resources as described below.


  name (, str, )
    Partition name


  {property} (, any, )
    Additional properties of the partition, as described in the :term:`HMC API` (using hyphens (-) in the property names).


  hbas (, list, )
    HBAs of the partition (for ``state=facts``).


    name (, str, )
      HBA name


    {property} (, any, )
      Additional properties of the HBA, as described in the :term:`HMC API` (using hyphens (-) in the property names).



  nics (, list, )
    NICs of the partition (for ``state=facts``).


    name (, str, )
      NIC name


    {property} (, any, )
      Additional properties of the NIC, as described in the :term:`HMC API` (using hyphens (-) in the property names).



  virtual-functions (, list, )
    Virtual functions of the partition (for ``state=facts``).


    name (, str, )
      VF name


    {property} (, any, )
      Additional properties of the VF, as described in the :term:`HMC API` (using hyphens (-) in the property names).







Status
------




- This module is guaranteed to have backward compatible interface changes going forward. *[stableinterface]*


- This module is maintained by community.



Authors
~~~~~~~

- Andreas Maier (@andy-maier)
- Andreas Scheuring (@scheuran)
- Juergen Leopold (@leopoldjuergen)

