
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_lpar_list.py

.. _zhmc_lpar_list_module:
.. _ibm.ibm_zhmc.zhmc_lpar_list_module:


zhmc_lpar_list -- List LPARs (classic mode)
===========================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- List LPARs on a specific CPC (Z system) or on all managed CPCs.
- CPCs in DPM mode are ignored (i.e. do not lead to a failure).
- LPARs for which the user has no object access permission are ignored (i.e. do not lead to a failure).
- On HMCs with version 2.14.0 or higher, the "List Permitted Logical Partitions" operation is used by this module. Otherwise, the managed CPCs are listed and then the LPARs on each desired CPC or CPCs are listed. This improves the execution time of the module on newer HMCs but does not affect the module result data.


Requirements
------------

- The HMC userid must have object-access permissions to these objects: Target LPArs, CPCs of target LPARs (only for z13 and older).




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



cpc_name
  Name of the CPC for which the LPARs are to be listed.

  Default: All managed CPCs.

  | **required**: False
  | **type**: str


additional_properties
  List of additional properties to be returned for each LPAR, in addition to the default properties (see result description).

  Mutually exclusive with :literal:`full\_properties`.

  The property names are specified with underscores instead of hyphens.

  On HMCs with an API version below 4.10 (= HMC version 2.16.0 plus some post-GA updates), all properties of each LPAR will be returned if this parameter is specified, but you should not rely on that.

  | **required**: False
  | **type**: list
  | **elements**: str


full_properties
  If True, all properties of each LPAR will be returned. Default: False.

  Mutually exclusive with :literal:`additional\_properties`.

  Note: Setting this to True causes a loop of 'Get Logical Partition Properties' operations to be executed. It is preferable from a performance perspective to use the :literal:`additional\_properties` parameter instead.

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

   - name: List the permitted LPARs on all managed CPCs
     zhmc_lpar_list:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
     register: lpar_list

   - name: List the permitted LPARs on a CPC
     zhmc_lpar_list:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: CPCA
     register: lpar_list










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

lpars
  The list of permitted LPARs, with a subset of their properties.

  | **returned**: success
  | **type**: list
  | **elements**: dict
  | **sample**:

    .. code-block:: json

        [
            {
                "activation_mode": "linux",
                "cpc_name": "CPC1",
                "has_unacceptable_status": false,
                "name": "LPAR1",
                "se_version": "2.15.0",
                "status": "active"
            }
        ]

  name
    LPAR name

    | **type**: str

  cpc_name
    Name of the parent CPC of the LPAR

    | **type**: str

  se_version
    SE version of the parent CPC of the LPAR

    | **type**: str

  status
    The current status of the LPAR. For details, see the description of the 'status' property in the data model of the 'Logical Partition' resource (see :ref:`HMC API <HMC API>`\ ).

    | **type**: str

  has_unacceptable_status
    Indicates whether the current status of the LPAR is unacceptable, based on its 'acceptable-status' property.

    | **type**: bool

  activation_mode
    The activation mode of the LPAR. For details, see the description of the 'activation-mode' property in the data model of the 'Logical Partition' resource (see :ref:`HMC API <HMC API>`\ ).

    | **type**: str

  {additional_property}
    Additional properties requested via :literal:`full\_properties` or :literal:`additional\_properties`. The property names will have underscores instead of hyphens.

    | **type**: raw


