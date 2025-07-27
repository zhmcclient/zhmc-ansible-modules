
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_user_role_list.py

.. _zhmc_user_role_list_module:
.. _ibm.ibm_zhmc.zhmc_user_role_list_module:


zhmc_user_role_list -- List HMC user roles
==========================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- List user roles on the HMC.


Requirements
------------

- The HMC userid must have object-access permission to the target user roles, or task permission to the 'Manage User Roles' task.




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
  If True, all properties of each user role will be returned. Default: False.

  Note: Setting this to True causes a loop of 'Get User Role Properties' operations to be executed.

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

   - name: List user roles
     zhmc_user_role_list:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
     register: urole_list










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

user_roles
  The list of user roles, with a subset of their properties.

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
                "name": "role 1",
                "type": "user-defined"
            }
        ]

  name
    User role name

    | **type**: str

  type
    Type of the user role (\ :literal:`system-defined`\ , :literal:`user-defined`\ )

    | **type**: str

  {additional_property}
    Additional properties requested via :literal:`full\_properties`. The property names will have underscores instead of hyphens.

    | **type**: raw


