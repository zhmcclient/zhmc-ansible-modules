
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_lpar.py

.. _zhmc_lpar_module:


zhmc_lpar -- Manage LPARs
=========================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gather facts about an LPAR of a CPC (Z system) in classic mode.
- Update modifiable properties of an active LPAR.
- Activate an LPAR and update its properties.
- Load an LPAR and update its properties.
- Deactivate an LPAR using the 'Deactivate Logical Partition' operation.
- Initialize for load using the 'Reset Clear' or 'Reset Normal' operations.


Requirements
------------

- The targeted CPC must be in the classic operational mode.
- The HMC userid must have these task permissions: 'Activate', 'Deactivate', 'Logical Processor Add' (if cores are updated), 'Firmware Details' (if 'zaware-...' properties are updated), 'Change Object Options' or 'Customize/Delete Activation Profiles' (if 'next-activation-profile-name' property is updated).
- The HMC userid must have object-access permissions to these objects: Target LPARs, CPCs of target LPARs.




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
  The name of the CPC with the target LPAR.

  | **required**: True
  | **type**: str


name
  The name of the target LPAR.

  | **required**: True
  | **type**: str


state
  The desired state for the LPAR:

  \* \ :literal:`inactive`\ : Ensures that the LPAR is inactive (i.e. status 'not-activated'), unless the LPAR is currently operating and the \ :literal:`force`\  parameter was not set to True. Properties cannot be updated. The LPAR is deactivated if needed.

  \* \ :literal:`active`\ : Ensures that the LPAR is at least active (i.e. status is 'not-operating', 'operating' or 'exceptions'), and then ensures that the LPAR properties have the specified values. The LPAR is activated if needed using the 'Activate Logical Partition' operation. In certain cases, that operation will automatically load the LPAR. For details, see the \ :literal:`activation\_profile\_name`\  parameter.

  \* \ :literal:`loaded`\ : Ensures that the LPAR is loaded (i.e. status is 'operating' or 'exceptions'), and then ensures that the LPAR properties have the specified values. The LPAR is first activated if needed using the 'Activate Logical Partition' operation, and then loaded if needed using the 'Load Logical Partition' operation. For details, see the \ :literal:`activation\_profile\_name`\  parameter.

  \* \ :literal:`reset\_clear`\ : Performs the 'Reset Clear' HMC operation on the LPAR. This initializes the LPAR for loading by clearing its pending interruptions, resetting its channel subsystem, resetting its processors, and clearing its memory). The LPAR must be in status 'not-operating', 'operating', or 'exceptions'. If the LPAR status is 'operating' or 'exceptions', the operation will fail unless the \ :literal:`force`\  parameter is set to True. Properties cannot be updated.

  \* \ :literal:`reset\_normal`\ : Performs the 'Reset Normal' HMC operation on the LPAR. This initializes the LPAR for loading by clearing its pending interruptions, resetting its channel subsystem, and resetting its processors). It does not clear the memory. The LPAR must be in status 'not-operating', 'operating', or 'exceptions'. If the LPAR status is 'operating' or 'exceptions', the operation will fail unless the \ :literal:`force`\  parameter is set to True. Properties cannot be updated.

  \* \ :literal:`set`\ : Ensures that the LPAR properties have the specified values. Requires that the LPAR is at least active (i.e. status is 'not-operating', 'operating' or 'exceptions') but does not activate the LPAR if that is not the case.

  \* \ :literal:`facts`\ : Returns the current LPAR properties.

  In all cases, the LPAR must exist.

  | **required**: True
  | **type**: str
  | **choices**: inactive, active, loaded, reset_clear, reset_normal, set, facts


select_properties
  Limits the returned properties of the LPAR to those specified in this parameter plus those specified in the \ :literal:`properties`\  parameter.

  The properties can be specified with underscores or hyphens in their names.

  Null indicates not to limit the returned properties in this way.

  This parameter is ignored for \ :literal:`state`\  values that cause no properties to be returned.

  The specified properties are passed to the 'Get Logical Partition Properties' HMC operation using the 'properties' query parameter and save time for the HMC to pull together all properties.

  | **required**: False
  | **type**: list
  | **elements**: str


activation_profile_name
  The name of the image or load activation profile to be used when the LPAR needs to be activated, for \ :literal:`state=active`\  and \ :literal:`state=loaded`\ .

  This parameter is not allowed for the other \ :literal:`state`\  values.

  Default: The image or load activation profile specified in the 'next-activation-profile-name' property of the LPAR is used when the LPAR needs to be activated.

  For LPARs with activation modes other than SSC or zAware, the following applies: If an image activation profile is specified, the 'load-at-activation' property of the image activation profile determines whether an automatic load is performed, using the load parameters from the image activation profile. If a load activation profile is specified, an automatic load is always performed, using the parameters from the load activation profile.

  For LPARs with activation modes SSC or zAware, the following applies: A load activation profile cannot be specified. The LPAR is always auto-loaded using internal load parameters (ignoring the 'load-at-activation' property and the load-related properties of their image activation profile).

  | **required**: False
  | **type**: str


load_address
  The hexadecimal address of an I/O device that provides access to the control program to be loaded, for \ :literal:`state=loaded`\ .

  This parameter is not allowed for the other \ :literal:`state`\  values.

  This parameter is used only when the LPAR is explicitly loaded using the 'Load Logical Partition' operation. It is not used when the LPAR is automatically loaded during the 'Activate Logical Partition' operation.

  For z13 and older generations, this parameter is required. Starting with z14, this parameter is optional and defaults to the load address specified in the 'last-used-load-address' property of the LPAR.

  | **required**: False
  | **type**: str


load_parameter
  A parameter string that is passed to the control program when loading it, for \ :literal:`state=loaded`\ .

  This parameter is not allowed for the other \ :literal:`state`\  values.

  This parameter is used only when the LPAR is explicitly loaded using the 'Load Logical Partition' operation. It is not used when the LPAR is automatically loaded during the 'Activate Logical Partition' operation.

  | **required**: False
  | **type**: str


clear_indicator
  Controls whether memory is cleared before performing the load, for \ :literal:`state=loaded`\ .

  This parameter is not allowed for the other \ :literal:`state`\  values.

  This parameter is used only when the LPAR is explicitly loaded using the 'Load Logical Partition' operation. It is not used when the LPAR is automatically loaded during the 'Activate Logical Partition' operation.

  | **required**: False
  | **type**: bool
  | **default**: True


store_status_indicator
  Controls whether the current values of CPU timer, clock comparator, program status word, and the contents of the processor registers are stored to their assigned absolute storage locations, for \ :literal:`state=loaded`\ .

  This parameter is not allowed for the other \ :literal:`state`\  values.

  This parameter is used only when the LPAR is explicitly loaded using the 'Load Logical Partition' operation. It is not used when the LPAR is automatically loaded during the 'Activate Logical Partition' operation.

  | **required**: False
  | **type**: bool


timeout
  Timeout in seconds, for activate (if needed) and for load (if needed).

  | **required**: False
  | **type**: int
  | **default**: 60


force
  Controls whether operations that change the LPAR status are performed when the LPAR is currently loaded (i.e. status 'operating' or 'exceptions'):

  If True, such operations are performed regardless of the current LPAR status.

  If False (default), such operations are performed only if the LPAR is not currently loaded, and are rejected otherwise.

  | **required**: False
  | **type**: bool


os_ipl_token
  Setting this parameter for \ :literal:`state=reset\_clear`\  or \ :literal:`state=reset\_normal`\  requests that the corresponding HMC operations only be performed if the provided value matches the current value of the 'os-ipl-token' property of the LPAR, and be rejected otherwise. Note that the 'os-ipl-token' property of the LPAR is set by the operating system and is set only by some operating systems, such as z/OS. This parameter is ignored for other \ :literal:`state`\  values.

  | **required**: False
  | **type**: str


properties
  Dictionary with new values for the LPAR properties, for \ :literal:`state=active`\ , \ :literal:`state=loaded`\  and \ :literal:`state=set`\ . Key is the property name with underscores instead of hyphens, and value is the property value in YAML syntax. Integer properties may also be provided as decimal strings.

  The possible input properties in this dictionary are the properties defined as writeable in the data model for LPAR resources (where the property names contain underscores instead of hyphens).

  Properties omitted in this dictionary will not be updated.

  This parameter is not allowed for the other \ :literal:`state`\  values.

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

   - name: Ensure the LPAR is inactive
     zhmc_lpar:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       name: "{{ my_lpar_name }}"
       state: inactive
     register: lpar1

   - name: "Ensure the LPAR is active (using the default image profile when it needs to be activated),
            and then set the CP sharing weight to 20"
     zhmc_lpar:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       name: "{{ my_lpar_name }}"
       state: active
       properties:
         initial_processing_weight: 20
     register: lpar1

   - name: Ensure the LPAR is active (using image profile LPAR2 when it needs to be activated)
     zhmc_lpar:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       name: "{{ my_lpar_name }}"
       state: active
       activation_profile_name: LPAR2
     register: lpar1

   - name: Ensure the LPAR is loaded (using the default image profile when it needs to be activated)
     zhmc_lpar:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       name: "{{ my_lpar_name }}"
       state: loaded
     register: lpar1

   - name: Ensure the LPAR is initialized for loading, clearing its memory
     zhmc_lpar:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       name: "{{ my_lpar_name }}"
       state: reset_clear
     register: lpar1

   - name: Ensure the LPAR is initialized for loading, not clearing its memory
     zhmc_lpar:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       name: "{{ my_lpar_name }}"
       state: reset_normal
     register: lpar1

   - name: Ensure the CP sharing weight of the LPAR is 30
     zhmc_lpar:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       name: "{{ my_lpar_name }}"
       state: set
       properties:
         initial_processing_weight: 30
     register: lpar1

   - name: Gather facts about the LPAR
     zhmc_lpar:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       name: "{{ my_lpar_name }}"
       state: facts
     register: lpar1










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

lpar
  For \ :literal:`state=inactive|reset\_clear|reset\_normal`\ , an empty dictionary.

  For \ :literal:`state=active|loaded|set|facts`\ , the resource properties of the LPAR after after any specified updates have been applied.

  Note that the returned properties may show different values than the ones that were specified as input for the update. For example, memory properties may be rounded up, hexadecimal strings may be shown with a different representation format, and other properties may change as a result of updating some properties. For details, see the data model of the 'Logical Partition' object in the :term:\`HMC API\` book.

  | **returned**: success
  | **type**: dict
  | **sample**:

    .. code-block:: json

        {
            "absolute-aap-capping": {
                "type": "none"
            },
            "absolute-cbp-capping": {
                "type": "none"
            },
            "absolute-cf-capping": {
                "type": "none"
            },
            "absolute-ifl-capping": {
                "type": "none"
            },
            "absolute-processing-capping": {
                "type": "none"
            },
            "absolute-ziip-capping": {
                "type": "none"
            },
            "acceptable-status": [
                "operating"
            ],
            "activation-mode": "ssc",
            "additional-status": "",
            "class": "logical-partition",
            "cluster-name": "",
            "current-aap-processing-weight": null,
            "current-aap-processing-weight-capped": null,
            "current-cbp-processing-weight": null,
            "current-cbp-processing-weight-capped": null,
            "current-cf-processing-weight": null,
            "current-cf-processing-weight-capped": null,
            "current-ifl-processing-weight": null,
            "current-ifl-processing-weight-capped": null,
            "current-processing-weight": 10,
            "current-processing-weight-capped": false,
            "current-vfm-storage": 0,
            "current-ziip-processing-weight": null,
            "current-ziip-processing-weight-capped": null,
            "defined-capacity": 0,
            "description": "LPAR Image",
            "group-profile-capacity": null,
            "group-profile-uri": null,
            "has-operating-system-messages": true,
            "has-unacceptable-status": false,
            "initial-aap-processing-weight": null,
            "initial-aap-processing-weight-capped": null,
            "initial-cbp-processing-weight": null,
            "initial-cbp-processing-weight-capped": null,
            "initial-cf-processing-weight": null,
            "initial-cf-processing-weight-capped": null,
            "initial-ifl-processing-weight": null,
            "initial-ifl-processing-weight-capped": null,
            "initial-processing-weight": 10,
            "initial-processing-weight-capped": false,
            "initial-vfm-storage": 0,
            "initial-ziip-processing-weight": null,
            "initial-ziip-processing-weight-capped": null,
            "is-locked": false,
            "last-used-activation-profile": "ANGEL",
            "last-used-boot-record-logical-block-address": "0",
            "last-used-disk-partition-id": 0,
            "last-used-load-address": "00000",
            "last-used-load-parameter": "",
            "last-used-logical-unit-number": "0",
            "last-used-operating-system-specific-load-parameters": "",
            "last-used-world-wide-port-name": "0",
            "maximum-aap-processing-weight": null,
            "maximum-cbp-processing-weight": null,
            "maximum-cf-processing-weight": null,
            "maximum-ifl-processing-weight": null,
            "maximum-processing-weight": 0,
            "maximum-vfm-storage": 0,
            "maximum-ziip-processing-weight": null,
            "minimum-aap-processing-weight": null,
            "minimum-cbp-processing-weight": null,
            "minimum-cf-processing-weight": null,
            "minimum-ifl-processing-weight": null,
            "minimum-processing-weight": 0,
            "minimum-ziip-processing-weight": null,
            "name": "ANGEL",
            "next-activation-profile-name": "ANGEL",
            "object-id": "10fa8489-4e06-3601-9170-eee82e26937c",
            "object-uri": "/api/logical-partitions/10fa8489-4e06-3601-9170-eee82e26937c",
            "os-ipl-token": "0000000000000000",
            "os-level": "1.0.0",
            "os-name": "INSTALL",
            "os-type": "SSC",
            "parent": "/api/cpcs/4f01576a-c3f6-3224-a951-b1bf361886a4",
            "partition-identifier": "33",
            "partition-number": "2f",
            "program-status-word-information": [
                {
                    "cpid": "00",
                    "psw": "0706C00180000000000000000070E050"
                },
                {
                    "cpid": "01",
                    "psw": "0706C00180000000000000000070E050"
                },
                {
                    "cpid": "02",
                    "psw": "0706C00180000000000000000070E050"
                },
                {
                    "cpid": "03",
                    "psw": "0706C00180000000000000000070E050"
                },
                {
                    "cpid": "04",
                    "psw": "0706C00180000000000000000070E050"
                },
                {
                    "cpid": "05",
                    "psw": "0706C00180000000000000000070E050"
                },
                {
                    "cpid": "06",
                    "psw": "0706C00180000000000000000070E050"
                },
                {
                    "cpid": "07",
                    "psw": "0706C00180000000000000000070E050"
                },
                {
                    "cpid": "08",
                    "psw": "0706C00180000000000000000070E050"
                },
                {
                    "cpid": "09",
                    "psw": "0706C00180000000000000000070E050"
                }
            ],
            "ssc-dns-info": null,
            "ssc-gateway-info": null,
            "ssc-host-name": null,
            "ssc-master-userid": null,
            "ssc-network-info": null,
            "status": "operating",
            "storage-central-allocation": [
                {
                    "current": 8192,
                    "gap": 102400,
                    "initial": 8192,
                    "maximum": 8192,
                    "origin": 127322112,
                    "storage-element-type": "central"
                }
            ],
            "storage-expanded-allocation": [],
            "sysplex-name": null,
            "workload-manager-enabled": false
        }

  name
    LPAR name

    | **type**: str

  {property}
    Additional properties of the LPAR, as described in the data model of the 'Logical Partition' object in the :term:\`HMC API\` book. The property names have hyphens (-) as described in that book.



