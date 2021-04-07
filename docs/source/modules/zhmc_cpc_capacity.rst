
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_cpc_capacity.py

.. _zhmc_cpc_capacity_module:


zhmc_cpc_capacity -- Manage processor capacity on demand
========================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gather facts about the processor capacity of a CPC (Z system).
- Update the processor capacity of a CPC (Z system) via adding or removing temporary capacity (On/Off CoD).
- For details on processor capacity on demand, see the :term:`Capacity on Demand User's Guide`.





Parameters
----------


hmc_host
  The hostname or IP address of the HMC.

  | **required**: True
  | **type**: str


hmc_auth
  The authentication credentials for the HMC, as a dictionary of ``userid``, ``password``.

  | **required**: True
  | **type**: dict


  userid
    The userid (username) for authenticating with the HMC.

    | **required**: True
    | **type**: str


  password
    The password for authenticating with the HMC.

    | **required**: True
    | **type**: str



name
  The name of the target CPC.

  | **required**: True
  | **type**: str


state
  The desired state for the operation:

  * ``set``: Ensures that the CPC has the specified processor capacity and returns capacity related properties of the CPC..

  * ``facts``: Does not change anything on the CPC and returns capacity related properties of the CPC.

  | **required**: True
  | **type**: str
  | **choices**: set, facts


test
  Indicates whether real or test resources should be activated. Test resources are automatically deactivated after 24h.

  | **required**: False
  | **type**: bool


record_id
  The ID of the capacity record to be used for any updates of the processor capacity.

  | **required**: True
  | **type**: str


software_model
  The target software model to be active. This value must be one of the software models defined within the specified capacity record. The software model implies the number of general purpose processors that will be active. Target numbers of specialty processors can be specified with the ``specialty_processors`` parameter.

  | **required**: False
  | **type**: str


specialty_processors
  The target number of specialty processors to be active. Processor types not specified will not be changed. Target numbers of general purpose processors can be set via the ``software_model`` parameter.

  Each item in the dictionary identifies the target number of processors of one type of specialty processor. The key identifies the type of specialty processor ('aap', 'cbp', 'icf', 'ifl', 'iip', 'sap'), and the value is the target number of processors of that type. Note that the target number is the number of permanently activated processors plus the number of temporarily activated processors.

  If the target number of processors is not installed in the system, or if the specified software model or number of a specialty processors exceeds the limits of the capacity record, the task will fail.

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

   - name: Gather facts about the CPC processor capacity
     zhmc_cpc_capacity:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_cpc_name }}"
       state: facts
     register: cap1

   - name: Ensure the CPC has a certain general purpose processor capacity active
     zhmc_cpc_capacity:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_cpc_name }}"
       state: set
       record_id: 1234
       software_model: "710"
     register: cap1

   - name: Ensure the CPC has a certain IFL processor capacity active
     zhmc_cpc_capacity:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_cpc_name }}"
       state: set
       record_id: 1234
       specialty_processors:
         ifl: 20
     register: cap1










Return Values
-------------


changed
  Indicates if any change has been made by the module. For ``state=facts``, always will be false.

  | **returned**: always
  | **type**: bool

msg
  An error message that describes the failure.

  | **returned**: failure
  | **type**: str

cpc
  A dictionary with capacity related properties of the CPC that indicate the currently active processor capacity.

  | **returned**: success
  | **type**: dict

  name
    CPC name

    | **type**: str

  software_model
    The current software model that is active. The software model implies the number of general purpose processors that are active.

    | **type**: str

  general_processors
    The current number of general purpose processors that are active.

    | **type**: int

  specialty_processors
    The current number of specialty processors that are active.

    Each item in the dictionary identifies the number of processors of one type of specialty processor. The key identifies the type of specialty processor ('aap', 'cbp', 'icf', 'ifl', 'iip', 'sap'), and the value is the current number of processors of that type that are active. Note that this number is the number of permanently activated processors plus the number of temporarily activated processors.

    | **type**: dict


