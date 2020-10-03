.. _zhmc_adapter_module:


zhmc_adapter -- Manages adapters of Z systems.
==============================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Gather facts about an adapter of a CPC (Z system), including its ports.

Update the properties of an adapter.



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
    The name of the target adapter. In case of renaming an adapter, this is the new name of the adapter.


  cpc_name (True, str, None)
    The name of the target CPC.


  match (False, dict, None)
    Only for ``state=set``: Match properties for identifying the target adapter in the set of adapters in the CPC, if an adapter with the name specified in the ``name`` module parameter does not exist in that set. This parameter will be ignored otherwise.

    Use of this parameter allows renaming an adapter: The ``name`` module parameter specifies the new name of the target adapter, and the ``match`` module parameter identifies the adapter to be renamed. This can be combined with other property updates by using the ``properties`` module parameter.

    The parameter is a dictionary. The key of each dictionary item is the property name as specified in the data model for adapter resources, with underscores instead of hyphens. The value of each dictionary item is the match value for the property (in YAML syntax). Integer properties may also be provided as decimal strings.

    The specified match properties follow the rules of filtering for the zhmcclient library as described in https://python-zhmcclient.readthedocs.io/en/stable/concepts.html#filtering

    The possible match properties are all properties in the data model for adapter resources, including ``name``.


  state (True, str, None)
    The desired state for the attachment:

    * ``set``: Ensures that an existing adapter has the specified properties.

    * ``present``: Ensures that a Hipersockets adapter exists and has the specified properties.

    * ``absent``: Ensures that a Hipersockets adapter does not exist.

    * ``facts``: Does not change anything on the adapter and returns the adapter properties including its ports.


  properties (False, dict, None)
    Only for ``state=set|present``: New values for the properties of the adapter. Properties omitted in this dictionary will remain unchanged. This parameter will be ignored for other states.

    The parameter is a dictionary. The key of each dictionary item is the property name as specified in the data model for adapter resources, with underscores instead of hyphens. The value of each dictionary item is the property value (in YAML syntax). Integer properties may also be provided as decimal strings.

    The possible properties in this dictionary are the properties defined as writeable in the data model for adapter resources, with the following exceptions:

    * ``name``: Cannot be specified as a property because the name has already been specified in the ``name`` module parameter.

    * ``type``: The desired adapter type can be specified in order to support adapters that can change their type (e.g. the FICON Express adapter can change its type between 'not-configured', 'fcp' and 'fc').

    * ``crypto_type``: The crypto type can be specified in order to support the ability of the Crypto Express adapters to change their crypto type. Valid values are 'ep11', 'cca' and 'acc'. Changing to 'acc' will zeroize the crypto adapter.


  log_file (False, str, None)
    File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.


  faked_session (False, raw, None)
    A ``zhmcclient_mock.FakedSession`` object that has a mocked HMC set up. If not null, this session will be used instead of connecting to the HMC specified in ``hmc_host``. This is used for testing purposes only.









Examples
--------

.. code-block:: yaml+jinja

    
    ---
    # Note: The following examples assume that some variables named 'my_*' are set.

    - name: Gather facts about an existing adapter
      zhmc_adapter:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_adapter_name }}"
        state: facts
      register: adapter1

    - name: Ensure an existing adapter has the desired property values
      zhmc_adapter:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_adapter_name }}"
        state: set
        properties:
          description: "This is adapter {{ my_adapter_name }}"
      register: adapter1

    - name: "Ensure the existing adapter identified by its name or adapter ID has
             the desired name and property values"
      zhmc_adapter:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_adapter_name }}"
        match:
          adapter_id: "12C"
        state: set
        properties:
          description: "This is adapter {{ my_adapter_name }}"
      register: adapter1

    - name: "Ensure a Hipersockets adapter exists and has the desired property
             values"
      zhmc_adapter:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_adapter_name }}"
        state: present
        properties:
          type: hipersockets
          description: "This is Hipersockets adapter {{ my_adapter_name }}"
      register: adapter1

    - name: "Ensure a Hipersockets adapter does not exist"
      zhmc_adapter:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_adapter_name }}"
        state: absent




Return Values
-------------

cpc (success, dict, C({
  "name": "adapter-1",
  "description": "Adapter 1",
  "status": "active",
  "acceptable_status": [ "active" ],
  ...
  "ports": [
    {
      "name": "Port 0",
      ...
    },
    ...
  ]
})
)
  For ``state=absent``, an empty dictionary.

  For ``state=set|present|facts``, a dictionary with the properties of the adapter. The properties contain these additional artificial properties for listing its child resources: - 'ports': The ports of the adapter, as a dict of key: port name, value: dict of a subset of the port properties (name, status, element_uri).





Status
------




- This module is guaranteed to have backward compatible interface changes going forward. *[stableinterface]*


- This module is maintained by community.



Authors
~~~~~~~

- Andreas Maier (@andy-maier)
- Andreas Scheuring (@scheuran)

