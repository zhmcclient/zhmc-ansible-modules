
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_user_list.py

.. _zhmc_user_list_module:


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

- The HMC userid must have object-access permission to the target users, or task permission to the 'Manage Users' task.




Parameters
----------


hmc_host
  The hostname or IP address of the HMC.

  | **required**: True
  | **type**: str


hmc_auth
  The authentication credentials for the HMC.

  | **required**: True
  | **type**: dict


  userid
    The userid (username) for authenticating with the HMC. This is mutually exclusive with providing ``session_id``.

    | **required**: False
    | **type**: str


  password
    The password for authenticating with the HMC. This is mutually exclusive with providing ``session_id``.

    | **required**: False
    | **type**: str


  session_id
    HMC session ID to be used. This is mutually exclusive with providing ``userid`` and ``password`` and can be created as described in :ref:`zhmc_session_module`.

    | **required**: False
    | **type**: str


  ca_certs
    Path name of certificate file or certificate directory to be used for verifying the HMC certificate. If null (default), the path name in the 'REQUESTS_CA_BUNDLE' environment variable or the path name in the 'CURL_CA_BUNDLE' environment variable is used, or if neither of these variables is set, the certificates in the Mozilla CA Certificate List provided by the 'certifi' Python package are used for verifying the HMC certificate.

    | **required**: False
    | **type**: str


  verify
    If True (default), verify the HMC certificate as specified in the ``ca_certs`` parameter. If False, ignore what is specified in the ``ca_certs`` parameter and do not verify the HMC certificate.

    | **required**: False
    | **type**: bool
    | **default**: True



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
    Type of the user ('standard', 'template', 'pattern-based', 'system-defined')

    | **type**: str


