
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_user_list.py

.. _zhmc_user_list_module:
.. _ibm.ibm_zhmc.zhmc_user_list_module:


zhmc_user_list -- List HMC users
================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- List users on the HMC.


Requirements
------------

- The HMC userid must have object\-access permission to the target users, or task permission to the 'Manage Users' task.




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



full_properties
  If True, all properties of each user will be returned. Default: False.

  Note: Setting this to True causes a loop of 'Get User Properties' operations to be executed.

  | **required**: False
  | **type**: bool


expand_names
  If True and :literal:`full\_properties` is set, additional artificial properties will be returned for the names of referenced objects, such as user roles, password rule, etc. Default: False.

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

   - name: List users
     zhmc_user_list:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
     register: user_list










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

users
  The list of users, with a subset of their properties.

  | **returned**: success
  | **type**: list
  | **elements**: dict
  | **sample**:

    .. code-block:: json

        [
            {
                "name": "Standard",
                "type": "system-defined"
            },
            {
                "name": "User 1",
                "type": "standard"
            }
        ]

  name
    User name

    | **type**: str

  type
    Type of the user (\ :literal:`standard`\ , :literal:`template`\ , :literal:`pattern\-based`\ , :literal:`system\-defined`\ )

    | **type**: str

  {additional_property}
    Additional properties requested via :literal:`full\_properties`. The property names will have underscores instead of hyphens.

    | **type**: raw

  user_role_names
    Only present if :literal:`expand\_names=true`\ : Name of the user roles referenced by property :literal:`user\_roles`.

    | **type**: str

  user_pattern_name
    Only present for users with :literal:`type=pattern` and if :literal:`expand\_names=true`\ : Name of the user pattern referenced by property :literal:`user\_pattern\_uri`.

    | **type**: str

  user_template_name
    Only present for users with :literal:`type=pattern` and if :literal:`expand\_names=true`\ : Name of the template user referenced by property :literal:`user\_template\_uri`.

    | **type**: str

  password_rule_name
    Only present if :literal:`expand\_names=true`\ : Name of the password rule referenced by property :literal:`password\_rule\_uri`.

    | **type**: str

  ldap_server_definition_name
    Only present if :literal:`expand\_names=true`\ : Name of the LDAP server definition referenced by property :literal:`ldap\_server\_definition\_uri`.

    | **type**: str

  primary_mfa_server_definition_name
    Only present if :literal:`expand\_names=true`\ : Name of the MFA server definition referenced by property :literal:`primary\_mfa\_server\_definition\_uri`.

    | **type**: str

  backup_mfa_server_definition_name
    Only present if :literal:`expand\_names=true`\ : Name of the MFA server definition referenced by property :literal:`backup\_mfa\_server\_definition\_uri`.

    | **type**: str

  default_group_name
    Only present if :literal:`expand\_names=true`\ : Name of the Group referenced by property :literal:`default\_group\_uri`.

    | **type**: str


