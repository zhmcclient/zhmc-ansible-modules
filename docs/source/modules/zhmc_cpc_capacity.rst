
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_cpc_capacity.py

.. _zhmc_cpc_capacity_module:
.. _ibm.ibm_zhmc.zhmc_cpc_capacity_module:


zhmc_cpc_capacity -- Manage temporary processor capacity
========================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gather facts about the processor capacity of a CPC (Z system).
- Update the processor capacity of a CPC (Z system) via adding or removing temporary capacity (On/Off CoD).
- For details on processor capacity on demand, see the :ref:`Capacity on Demand User's Guide <CoD Users Guide>`.


Requirements
------------

- The HMC userid must have these task permissions: 'Perform Model Conversion'.
- The HMC userid must have object-access permissions to these objects: Target CPCs.
- The CPC must be enabled for On-Off Capacity-On-Demand.




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
    The userid (username) for authenticating with the HMC. This is mutually exclusive with providing :literal:`hmc\_auth.session\_id`.

    | **required**: False
    | **type**: str


  password
    The password for authenticating with the HMC. This is mutually exclusive with providing :literal:`hmc\_auth.session\_id`.

    | **required**: False
    | **type**: str


  session_id
    HMC session ID to be used. This is mutually exclusive with providing :literal:`hmc\_auth.userid` and :literal:`hmc\_auth.password` and can be created as described in the :ref:`zhmc\_session module <zhmc_session_module>`.

    | **required**: False
    | **type**: str


  ca_certs
    Path name of certificate file or certificate directory to be used for verifying the HMC certificate. If null (default), the path name in the :envvar:`REQUESTS\_CA\_BUNDLE` environment variable or the path name in the :envvar:`CURL\_CA\_BUNDLE` environment variable is used, or if neither of these variables is set, the certificates in the Mozilla CA Certificate List provided by the 'certifi' Python package are used for verifying the HMC certificate.

    | **required**: False
    | **type**: str


  verify
    If True (default), verify the HMC certificate as specified in the :literal:`hmc\_auth.ca\_certs` parameter. If False, ignore what is specified in the :literal:`hmc\_auth.ca\_certs` parameter and do not verify the HMC certificate.

    | **required**: False
    | **type**: bool
    | **default**: True



name
  The name of the target CPC.

  | **required**: True
  | **type**: str


state
  The desired state for the operation:

  \* :literal:`set`\ : Ensures that the CPC has the specified specialty processor capacity and the specified software model, and returns the resulting processor capacity of the CPC.

  \* :literal:`facts`\ : Does not change anything on the CPC and returns the current processor capacity of the CPC.

  | **required**: True
  | **type**: str
  | **choices**: set, facts


record_id
  The ID of the capacity record to be used for any updates of the processor capacity.

  Required for :literal:`state=set`.

  | **required**: False
  | **type**: str


software_model
  The target software model to be active. This value must be one of the software models defined within the specified capacity record. The software model implies the number of general purpose processors that will be active.

  If null or not provided, the software model and the number of general purpose processors of the CPC will remain unchanged.

  | **required**: False
  | **type**: str


software_model_direction
  Indicates the direction of the capacity change for general purpose processors in :literal:`software\_model`\ , relative to the current software model:

  \* :literal:`increase`\ : The specified software model defines more general purpose processors than the current software model.

  \* :literal:`decrease`\ : The specified software model defines less general purpose processors than the current software model.

  Ignored when :literal:`software\_model` is null, not provided, or specifies the current software model. Otherwise required.

  | **required**: False
  | **type**: str
  | **choices**: increase, decrease


specialty_processors
  The target number of specialty processors to be active. Processor types not provided will not be changed. Target numbers of general purpose processors can be set via the :literal:`software\_model` parameter.

  Each item in the dictionary identifies the target number of processors of one type of specialty processor. The key identifies the type of specialty processor (\ :literal:`icf`\ , :literal:`ifl`\ , :literal:`iip`\ , :literal:`sap`\ ), and the value is the target number of processors of that type. Note that the target number is the number of permanently activated processors plus the number of temporarily activated processors.

  The target number for each processor type may be larger, equal or lower than the current number, but it must not be lower than the number of permanent processors of that type.

  If the target number of processors is not installed in the CPC, the :literal:`force` parameter controls what happens.

  If null, empty or not provided, the specialty processor capacity will remain unchanged.

  | **required**: False
  | **type**: dict


test_activation
  Indicates that test resources instead of real resources from the capacity record should be activated. Test resources are automatically deactivated after 24h. This is mainly used for Capacity Backup Upgrade (CBU) test activations. For details, see the :ref:`Capacity on Demand User's Guide <CoD Users Guide>`.

  | **required**: False
  | **type**: bool


force
  Indicates that an increase of capacity should be performed even if the necessary processors are not currently installed in the CPC.

  | **required**: False
  | **type**: bool


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
       record_id: R1234
       software_model: "710"
     register: cap1

   - name: Ensure the CPC has a certain IFL processor capacity active
     zhmc_cpc_capacity:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_cpc_name }}"
       state: set
       record_id: R1234
       specialty_processors:
         ifl: 20
     register: cap1










Return Values
-------------


changed
  Indicates if any change has been made by the module. For :literal:`state=facts`\ , always will be false.

  | **returned**: always
  | **type**: bool

msg
  An error message that describes the failure.

  | **returned**: failure
  | **type**: str

cpc
  A dictionary with capacity related properties of the CPC.

  | **returned**: success
  | **type**: dict

  name
    CPC name

    | **type**: str

  has_temporary_capacity_change_allowed
    Boolean indicating whether API applications are allowed to make changes to temporary capacity.

    | **type**: bool

  is_on_off_cod_enabled
    Boolean indicating whether the On/Off Capacity on Demand feature is enabled for the CPC.

    | **type**: bool

  is_on_off_cod_installed
    Boolean indicating whether an On/Off Capacity on Demand record is installed on the CPC.

    | **type**: bool

  is_on_off_cod_activated
    Boolean indicating whether an On/Off Capacity on Demand record is installed and active on the CPC.

    | **type**: bool

  on_off_cod_activation_date
    Timestamp when the On/Off Capacity on Demand record was activated on the CPC.

    | **type**: int

  software_model_purchased
    The software model based on the originally purchased processors. Omitted for SE version below 2.16.0.

    | **type**: str

  software_model_permanent
    The software model based on the permanently present processors (including any permanent capacity changes since the original purchase).

    | **type**: str

  software_model_permanent_plus_billable
    The software model based on the permanently present processors plus billable temporary processors.

    | **type**: str

  software_model_permanent_plus_temporary
    The software model based on the permanently present processors plus all temporary processors.

    | **type**: str

  msu_purchased
    The MSU value associated with the software model based on the originally purchased processors. Omitted for SE version below 2.16.0.

    | **type**: int

  msu_permanent
    The MSU value associated with the software model based on the permanently present processors (including any permanent capacity changes since the original purchase).

    | **type**: int

  msu_permanent_plus_billable
    The MSU value associated with the software model based on the permanently present processors plus billable temporary processors.

    | **type**: int

  msu_permanent_plus_temporary
    The MSU value associated with the software model based on the permanently present processors plus all temporary processors.

    | **type**: int

  processor_count_general_purpose
    The count of active general purpose processors.

    | **type**: int

  processor_count_ifl
    The count of active Integrated Facility for Linux (IFL) processors.

    | **type**: int

  processor_count_icf
    The count of active Internal Coupling Facility (ICF) processors.

    | **type**: int

  processor_count_iip
    The count of active IBM z Integrated Information Processor (zIIP) processors.

    | **type**: int

  processor_count_service_assist
    The count of active service assist processors.

    | **type**: int

  processor_count_spare
    The count of spare processors, across all processor types.

    | **type**: int

  processor_count_defective
    The count of defective processors, across all processor types.

    | **type**: int

  processor_count_pending_general_purpose
    The number of general purpose processors that will become active, when more processors are made available by adding new hardware or by deactivating capacity records.

    | **type**: int

  processor_count_pending_ifl
    The number of Integrated Facility for Linux processors that will become active, when more processors are made available by adding new hardware or by deactivating capacity records.

    | **type**: int

  processor_count_pending_icf
    The number of Integrated Coupling Facility processors that will become active, when more processors are made available by adding new hardware or by deactivating capacity records.

    | **type**: int

  processor_count_pending_iip
    The number of z Integrated Information Processors that will become active, when more processors are made available by adding new hardware or by deactivating capacity records.

    | **type**: int

  processor_count_pending_service_assist
    The number of service assist processors that will become active, when more processors are made available by adding new hardware or by deactivating capacity records.

    | **type**: int

  processor_count_permanent_ifl
    The number of Integrated Facility for Linux processors that are permanent. Omitted for SE version below 2.16.0.

    | **type**: int

  processor_count_permanent_icf
    The number of Integrated Coupling Facility processors that are permanent. Omitted for SE version below 2.16.0.

    | **type**: int

  processor_count_permanent_iip
    The number of z Integrated Information Processors that are permanent. Omitted for SE version below 2.16.0.

    | **type**: int

  processor_count_permanent_service_assist
    The number of service assist processors that are permanent. Omitted for SE version below 2.16.0.

    | **type**: int

  processor_count_unassigned_ifl
    The number of Integrated Facility for Linux processors that are unassigned. Omitted for SE version below 2.16.0.

    | **type**: int

  processor_count_unassigned_icf
    The number of Integrated Coupling Facility processors that are unassigned. Omitted for SE version below 2.16.0.

    | **type**: int

  processor_count_unassigned_iip
    The number of z Integrated Information Processors that are unassigned. Omitted for SE version below 2.16.0.

    | **type**: int

  processor_count_unassigned_service_assist
    The number of service assist processors that are unassigned. Omitted for SE version below 2.16.0.

    | **type**: int


