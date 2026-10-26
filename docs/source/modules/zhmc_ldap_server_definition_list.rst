
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_ldap_server_definition_list.py

.. _zhmc_ldap_server_definition_list_module:
.. _ibm.ibm_zhmc.zhmc_ldap_server_definition_list_module:


zhmc_ldap_server_definition_list -- List LDAP Server Definitions on the HMC
===========================================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- List LDAP Server Definitions on the HMC.


Requirements
------------

- The HMC userid must have object\-access permission to the target LDAP Server Definitions, or task permission to the 'Manage Users' task.




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



additional_properties
  List of additional properties to be returned for each LDAP server definition, in addition to the default properties (see result description).

  Mutually exclusive with :literal:`full\_properties`.

  The property names are specified with underscores instead of hyphens.

  Depending on the HMC version, more properties than those specified may be returned, but you should not rely on that.

  | **required**: False
  | **type**: list
  | **elements**: str


full_properties
  If True, all readable properties of each LDAP server definition will be returned. Default: False.

  Mutually exclusive with :literal:`additional\_properties`.

  Note: It is preferable from a performance perspective to use the :literal:`additional\_properties` parameter instead.

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

   - name: List LDAP Server Definitions
     zhmc_ldap_server_definition_list:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
     register: lsd_list










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

ldap_server_definitions
  The list of LDAP Server Definitions, with a subset of their properties.

  | **returned**: success
  | **type**: list
  | **elements**: dict
  | **sample**:

    .. code-block:: json

        [
            {
                "name": "Standard"
            },
            {
                "name": "User 1"
            }
        ]

  name
    User name

    | **type**: str


