
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_http.py

.. _zhmc_http_module:
.. _ibm.ibm_zhmc.zhmc_http_module:


zhmc_http -- Perform direct HTTP requests
=========================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Perform a direct GET/POST/DELETE HTTP request against the HMC WS\-API.
- This module can be used as a fallback for HMC WS\-API operations that are not yet supported with other modules of this collection.






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



method
  The HTTP method to be executed, in lower case.

  | **required**: True
  | **type**: str
  | **choices**: get, post, delete


uri
  The canonical URI of the targeted resource starting with '/api/', including any query parameters.

  | **required**: True
  | **type**: str


request_body
  The request body for the HTTP request.

  Only permitted for :literal:`method=post`.

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
   - name: List Dual-Control Requests
     zhmc_http:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth:
         userid: "{{ my_hmc_userid }}"
         password: "{{ my_hmc_password }}"
         verify: true
         ca_certs: "{{ my_certs_dir }}"
       method: get
       uri: /api/console/dual-control-requests
     register: dual_control_result










Return Values
-------------


changed
  Indicates if any change has been made by the module. This will always be false for HTTP GET operations, and will always be true for HTTP POST and DELETE operations.

  | **returned**: always
  | **type**: bool

msg
  An error message that describes the failure. If an HTTP response was received, this will include HTTP status code, reason code and the message from the error response body.

  | **returned**: failure
  | **type**: str

response_body
  The response body of the HTTP operation. If no HTTP response was received, this will be null.

  | **returned**: always
  | **type**: dict

