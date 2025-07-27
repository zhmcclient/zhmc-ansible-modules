
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_user_pattern_list.py

.. _zhmc_user_pattern_list_module:
.. _ibm.ibm_zhmc.zhmc_user_pattern_list_module:


zhmc_user_pattern_list -- List HMC user patterns
================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- List User Patterns on the HMC.


Requirements
------------

- The HMC userid must have object-access permission to the User Pattern objects included in the result, or task permission to the 'Manage User Patterns' task.




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
  If True, all properties of each user pattern will be returned. Default: False.

  Note: Setting this to True causes a loop of 'Get User Pattern Properties' operations to be executed.

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

   - name: List User Patterns
     zhmc_user_pattern_list:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
     register: upattern_list










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

user_patterns
  The list of User Patterns, with a subset or all of their properties, dependent on :literal:`full\_properties`.

  | **returned**: success
  | **type**: list
  | **elements**: dict
  | **sample**:

    .. code-block:: json

        [
            {
                "element_uri": "/api/console/user-patterns/cbcaf7a0-46cc-11e9-bfd3-f44a39cd42f9",
                "name": "Bluepages email address",
                "type": "glob-like"
            },
            {
                "element_uri": "/api/console/user-patterns/fb22d4a2-4e40-11e9-a8a8-00106f23f636",
                "name": "regexp pattern 1",
                "type": "regular-expression"
            }
        ]

  name
    User pattern name

    | **type**: str

  element_uri
    Element URI of the User Pattern object

    | **type**: str

  type
    The style in which the user pattern is expressed, as one of the following values:

    :literal:`glob-like` - Glob-like pattern as used in file names, supporting the special characters :literal:`\*` and :literal:`?`.

    :literal:`regular-expression` - Regular expression pattern using :ref:`Java regular expressions <Java regular expressions>`.

    | **type**: str

  {additional_property}
    Additional properties requested via :literal:`full\_properties`\ , as described in the data model of the 'User Pattern' object in the :ref:`HMC API <HMC API>` book. The property names will have underscores instead of hyphens.

    | **type**: raw


