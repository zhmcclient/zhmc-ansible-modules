
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_adapter.py

.. _zhmc_adapter_module:


zhmc_adapter -- Update adapters and create Hipersocket adapters
===============================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gather facts about an adapter of a CPC (Z system), including its ports.
- Update the properties of an adapter and its ports.
- Create or delete a Hipersocket adapter.


Requirements
------------

- The targeted Z system must be in the Dynamic Partition Manager (DPM) operational mode.
- The HMC userid must have these task permissions: 'Adapter Details', 'Create HiperSockets Adapter', 'Delete HiperSockets Adapter', 'Configure Storage - System Programmer'.
- The HMC userid must have object-access permissions to these objects: Target adapters, CPCs of target adapters.




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
  The name of the CPC with the target adapter.

  | **required**: True
  | **type**: str


name
  The name of the target adapter. In case of renaming an adapter, this is the new name of the adapter.

  | **required**: True
  | **type**: str


match
  Only for \ :literal:`state=set`\ : Match properties for identifying the target adapter in the set of adapters in the CPC, if an adapter with the name specified in the \ :literal:`name`\  module parameter does not exist in that set. This parameter will be ignored otherwise.

  Use of this parameter allows renaming an adapter: The \ :literal:`name`\  module parameter specifies the new name of the target adapter, and the \ :literal:`match`\  module parameter identifies the adapter to be renamed. This can be combined with other property updates by using the \ :literal:`properties`\  module parameter.

  The parameter is a dictionary. The key of each dictionary item is the property name as specified in the data model for adapter resources, with underscores instead of hyphens. The value of each dictionary item is the match value for the property (in YAML syntax). Integer properties may also be provided as decimal strings.

  The specified match properties follow the rules of filtering for the zhmcclient library as described in https://python-zhmcclient.readthedocs.io/en/stable/concepts.html#filtering

  The possible match properties are all properties in the data model for adapter resources, including \ :literal:`name`\ .

  | **required**: False
  | **type**: dict


state
  The desired state for the adapter. All states are fully idempotent within the limits of the properties that can be changed:

  \* \ :literal:`set`\ : Ensures that an existing adapter has the specified properties.

  \* \ :literal:`present`\ : Ensures that a Hipersockets adapter exists and has the specified properties.

  \* \ :literal:`absent`\ : Ensures that a Hipersockets adapter does not exist.

  \* \ :literal:`facts`\ : Returns the adapter properties including its ports.

  | **required**: True
  | **type**: str
  | **choices**: set, present, absent, facts


properties
  Only for \ :literal:`state=set|present`\ : New values for the properties of the adapter. Properties omitted in this dictionary will remain unchanged. This parameter will be ignored for other states.

  The parameter is a dictionary. The key of each dictionary item is the property name as specified in the data model for adapter resources, with underscores instead of hyphens. The value of each dictionary item is the property value (in YAML syntax). Integer properties may also be provided as decimal strings.

  The possible properties in this dictionary are the properties defined as writeable in the data model for adapter resources, with the following exceptions:

  \* \ :literal:`name`\ : Cannot be specified as a property because the name has already been specified in the \ :literal:`name`\  module parameter.

  \* \ :literal:`type`\ : The desired adapter type can be specified in order to support adapters that can change their type (e.g. the FICON Express adapter can change its type between 'not-configured', 'fcp' and 'fc').

  \* \ :literal:`crypto\_type`\ : The crypto type can be specified in order to support the ability of the Crypto Express adapters to change their crypto type. Valid values are 'ep11', 'cca' and 'acc'. Changing to 'acc' will zeroize the crypto adapter.

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






See Also
--------

.. seealso::

   - :ref:`zhmc_adapter_list_module`




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

adapter
  For \ :literal:`state=absent`\ , an empty dictionary.

  For \ :literal:`state=set|present|facts`\ , the adapter and its ports.

  | **returned**: success
  | **type**: dict
  | **sample**:

    .. code-block:: json

        {
            "adapter-family": "ficon",
            "adapter-id": "120",
            "allowed-capacity": 64,
            "card-location": "A14B-D112-J.01",
            "channel-path-id": "09",
            "class": "adapter",
            "configured-capacity": 14,
            "description": "",
            "detected-card-type": "ficon-express-16s-plus",
            "maximum-total-capacity": 254,
            "name": "FCP_120_SAN1_02",
            "object-id": "dfb2147a-e578-11e8-a87c-00106f239c31",
            "object-uri": "/api/adapters/dfb2147a-e578-11e8-a87c-00106f239c31",
            "parent": "/api/cpcs/66942455-4a14-3f99-8904-3e7ed5ca28d7",
            "physical-channel-status": "operating",
            "port-count": 1,
            "ports": [
                {
                    "class": "storage-port",
                    "description": "",
                    "element-id": "0",
                    "element-uri": "/api/adapters/dfb2147a-e578-11e8-a87c-00106f239c31/storage-ports/0",
                    "fabric-id": "100088947155A1E9",
                    "index": 0,
                    "name": "Port 0",
                    "parent": "/api/adapters/dfb2147a-e578-11e8-a87c-00106f239c31"
                }
            ],
            "state": "online",
            "status": "active",
            "storage-port-uris": [
                "/api/adapters/dfb2147a-e578-11e8-a87c-00106f239c31/storage-ports/0"
            ],
            "type": "fcp",
            "used-capacity": 20
        }

  name
    Adapter name

    | **type**: str

  {property}
    Additional properties of the adapter, as described in the data model of the 'Adapter' object in the :term:\`HMC API\` book. The property names have hyphens (-) as described in that book.

    | **type**: raw

  ports
    Artificial property for the ports of the adapter.

    | **type**: list
    | **elements**: dict

    name
      Port name

      | **type**: str

    {property}
      Additional properties of the port, as described in the data model of the 'Network Port' or 'Storage Port' element object of the 'Adapter' object in the :term:\`HMC API\` book. The property names have hyphens (-) as described in that book. In case of unconfigured FICON adapters, the property list is short.

      | **type**: raw



