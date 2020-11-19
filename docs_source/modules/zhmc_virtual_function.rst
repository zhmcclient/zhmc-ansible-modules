.. _zhmc_virtual_function_module:


zhmc_virtual_function -- Create virtual functions in partitions
===============================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Create, update, or delete a virtual function in a partition of a CPC (Z system).

Note that the Ansible module zhmc_partition can be used to gather facts about existing virtual functions of a partition.



Requirements
------------
The below requirements are needed on the host that executes this module.

- Access to the WS API of the HMC of the targeted Z system (see :term:`HMC API`). The targeted Z system must be in the Dynamic Partition Manager (DPM) operational mode.
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
    The name of the CPC with the partition containing the virtual function.


  partition_name (True, str, None)
    The name of the partition containing the virtual function.


  name (True, str, None)
    The name of the target virtual function that is managed. If the virtual function needs to be created, this value becomes its name.


  state (True, str, None)
    The desired state for the target virtual function:

    ``absent``: Ensures that the virtual function does not exist in the specified partition.

    ``present``: Ensures that the virtual function exists in the specified partition and has the specified properties.


  properties (False, dict, None)
    Dictionary with input properties for the virtual function, for ``state=present``. Key is the property name with underscores instead of hyphens, and value is the property value in YAML syntax. Integer properties may also be provided as decimal strings. Will be ignored for ``state=absent``.

    The possible input properties in this dictionary are the properties defined as writeable in the data model for Virtual Function resources (where the property names contain underscores instead of hyphens), with the following exceptions:

    * ``name``: Cannot be specified because the name has already been specified in the ``name`` module parameter.

    * ``adapter_uri``: Cannot be specified because this information is specified using the artificial property ``adapter_name``.

    * ``adapter_name``: The name of the adapter that backs the target virtual function.

    Properties omitted in this dictionary will remain unchanged when the virtual function already exists, and will get the default value defined in the data model for virtual functions when the virtual function is being created.


  log_file (False, str, None)
    File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.


  faked_session (False, raw, None)
    A ``zhmcclient_mock.FakedSession`` object that has a mocked HMC set up. If not null, this session will be used instead of connecting to the HMC specified in ``hmc_host``. This is used for testing purposes only.









Examples
--------

.. code-block:: yaml+jinja

    
    ---
    # Note: The following examples assume that some variables named 'my_*' are set.

    - name: Ensure virtual function exists in the partition
      zhmc_partition:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        partition_name: "{{ my_partition_name }}"
        name: "{{ my_vfunction_name }}"
        state: present
        properties:
          adapter_name: "ABC-123"
          description: "The accelerator adapter"
          device_number: "033F"
      register: vfunction1

    - name: Ensure virtual function does not exist in the partition
      zhmc_partition:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        partition_name: "{{ my_partition_name }}"
        name: "{{ my_vfunction_name }}"
        state: absent



Return Values
-------------

virtual_function (success, dict, )
  For ``state=absent``, an empty dictionary.

  For ``state=present``, a dictionary with the resource properties of the virtual function (after changes, if any).


  name (, str, )
    Virtual function name


  {property} (, any, )
    Additional properties of the virtual function, as described in the :term:`HMC API` (using hyphens (-) in the property names).






Status
------




- This module is guaranteed to have backward compatible interface changes going forward. *[stableinterface]*


- This module is maintained by community.



Authors
~~~~~~~

- Andreas Maier (@andy-maier)
- Andreas Scheuring (@scheuran)
- Juergen Leopold (@leopoldjuergen)

