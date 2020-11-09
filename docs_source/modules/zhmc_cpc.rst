.. _zhmc_cpc_module:


zhmc_cpc -- Manages Z systems at the system level.
==================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Gather facts about a CPC (Z system), including its adapters and partitions.

Update the properties of a CPC.



Requirements
------------
The below requirements are needed on the host that executes this module.

- Access to the WS API of the HMC of the targeted Z system. The targeted Z system must be in the Dynamic Partition Manager (DPM) operational mode.
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



  name (True, str, None)
    The name of the target CPC.


  state (True, str, None)
    The desired state for the attachment:

    * ``set``: Ensures that the CPC has the specified properties.

    * ``facts``: Does not change anything on the CPC and returns the CPC properties including its child resources.


  properties (False, dict, None)
    Only for ``state=set``: New values for the properties of the CPC. Properties omitted in this dictionary will remain unchanged. This parameter will be ignored for ``state=facts``.

    The parameter is a dictionary. The key of each dictionary item is the property name as specified in the data model for CPC resources, with underscores instead of hyphens. The value of each dictionary item is the property value (in YAML syntax). Integer properties may also be provided as decimal strings.

    The possible properties in this dictionary are the properties defined as writeable in the data model for CPC resources.


  log_file (False, str, None)
    File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.


  faked_session (False, raw, None)
    A ``zhmcclient_mock.FakedSession`` object that has a mocked HMC set up. If not null, this session will be used instead of connecting to the HMC specified in ``hmc_host``. This is used for testing purposes only.









Examples
--------

.. code-block:: yaml+jinja

    
    ---
    # Note: The following examples assume that some variables named 'my_*' are set.

    - name: Gather facts about the CPC
      zhmc_cpc:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        name: "{{ my_cpc_name }}"
        state: facts
      register: cpc1

    - name: Ensure the CPC has the desired property values
      zhmc_cpc:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        name: "{{ my_cpc_name }}"
        state: set
        properties:
          acceptable_status:
           - active
          description: "This is CPC {{ my_cpc_name }}"




Return Values
-------------

cpc (success, dict, )
  A dictionary with the properties of the CPC, including additional artificial properties as described below.


  name (, str, )
    CPC name


  {property} (, any, )
    Additional properties of the CPC, as described in the HMC WS-API book (using hyphens (-) in the property names).


  partitions (, dict, )
    Artificial property for the defined partitions of the CPC, with a subset of its properties.


    {name} (, dict, )
      Partition name


      name (, str, )
        Partition name


      status (, str, )
        Status of the partition


      object_uri (, str, )
        Canonical URI of the partition




  adapters (, dict, )
    Artificial property for the adapters of the CPC, with a subset of its properties.


    {name} (, dict, )
      Adapter name


      name (, str, )
        Adapter name


      status (, str, )
        Status of the adapter


      object_uri (, str, )
        Canonical URI of the adapter








Status
------




- This module is guaranteed to have backward compatible interface changes going forward. *[stableinterface]*


- This module is maintained by community.



Authors
~~~~~~~

- Andreas Maier (@andy-maier)
- Andreas Scheuring (@scheuran)

