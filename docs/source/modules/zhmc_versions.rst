
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_versions.py

.. _zhmc_versions_module:


zhmc_versions -- Retrieve HMC/CPC version and feature facts
===========================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Retrieve version and feature facts for the targeted HMC and its managed CPCs.


Requirements
------------

- No specific task or object-access permissions are required.




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



cpc_names
  List of CPC names for which facts are to be included in the result.

  Default: All managed CPCs.

  | **required**: False
  | **type**: list
  | **elements**: str


log_file
  File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.

  | **required**: False
  | **type**: str




Examples
--------

.. code-block:: yaml+jinja

   
   ---
   # Note: The following examples assume that some variables named 'my_*' are set.

   - name: Retrieve version and feature information for HMC and all managed CPCs
     zhmc_versions:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
     register: hmc1

   - name: Retrieve version and feature information for HMC only
     zhmc_versions:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_names: []
     register: hmc1










Return Values
-------------


changed
  Indicates if any change has been made by the module. This will always be false.

  | **returned**: always
  | **type**: bool

msg
  An error message that describes the failure.

  | **returned**: failure
  | **type**: str

versions
  The version information.

  | **returned**: success
  | **type**: dict
  | **sample**:

    .. code-block:: json

        {
            "cpcs": [
                {
                    "cpc_api_features": [
                        "adapter-network-information",
                        "..."
                    ],
                    "dpm_enabled": true,
                    "has_unacceptable_status": false,
                    "name": "CPC1",
                    "se_version": "2.16.0",
                    "se_version_info": [
                        2,
                        16,
                        0
                    ],
                    "status": "active"
                }
            ],
            "hmc_api_features": [
                "adapter-network-information",
                "..."
            ],
            "hmc_api_version": "4.10",
            "hmc_api_version_info": [
                4,
                10
            ],
            "hmc_name": "HMC1",
            "hmc_version": "2.16.0",
            "hmc_version_info": [
                2,
                16,
                0
            ]
        }

  hmc_name
    HMC name

    | **type**: str

  hmc_version
    HMC version, as a string.

    | **type**: str

  hmc_version_info
    HMC version, as a list of integers.

    | **type**: list
    | **elements**: int

  hmc_api_version
    HMC API version, as a string.

    | **type**: str

  hmc_api_version_info
    HMC API version, as a list of integers.

    | **type**: list
    | **elements**: int

  hmc_api_features
    The available HMC API features.

    | **type**: list
    | **elements**: str

  cpcs
    Version data for the requested CPCs of the HMC.

    | **type**: list
    | **elements**: dict

    name
      CPC name.

      | **type**: str

    status
      The current status of the CPC. For details, see the description of the 'status' property in the data model of the 'CPC' resource (see :term:\`HMC API\`).

      | **type**: str

    has_unacceptable_status
      Indicates whether the current status of the CPC is unacceptable, based on its 'acceptable-status' property.

      | **type**: bool

    dpm_enabled
      Indicates wehether the CPC is in DPM mode (true) or in classic mode (false).

      | **type**: bool

    se_version
      SE version of the CPC, as a string.

      | **type**: str

    se_version_info
      SE version of the CPC, as a list of integers.

      | **type**: list
      | **elements**: int

    cpc_api_features
      The available CPC API features.

      | **type**: list
      | **elements**: str



