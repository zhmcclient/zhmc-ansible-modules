
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_session.py

.. _zhmc_session_module:


zhmc_session -- Manage HMC sessions across tasks
================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Create a session on the HMC for use by other ibm\_zhmc modules, with \ :literal:`action=create`\ .
- Delete a session on the HMC, with \ :literal:`action=delete`\ .
- This module can be used in order to create an HMC session once and then use it for multiple tasks that use ibm\_zhmc modules, reducing the number of HMC sessions that need to be created, to just one. When this module is not used, each ibm\_zhmc module invocation will create and delete a separate HMC session.






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
    The userid (username) for creating the HMC session.

    Required for \ :literal:`action=create`\ , not permitted for \ :literal:`action=delete`\ .

    | **required**: False
    | **type**: str


  password
    The password for creating the HMC session.

    Required for \ :literal:`action=create`\ , not permitted for \ :literal:`action=delete`\ .

    | **required**: False
    | **type**: str


  session_id
    Session ID of the HMC session to be deleted.

    Required for \ :literal:`action=delete`\ , not permitted for \ :literal:`action=create`\ .

    | **required**: False
    | **type**: str


  ca_certs
    Path name of certificate file or certificate directory to be used for verifying the HMC certificate. If null (default), the path name in the \ :envvar:`REQUESTS\_CA\_BUNDLE`\  environment variable or the path name in the \ :envvar:`CURL\_CA\_BUNDLE`\  environment variable is used, or if neither of these variables is set, the certificates in the Mozilla CA Certificate List provided by the 'certifi' Python package are used for verifying the HMC certificate.

    Optional for \ :literal:`action=create`\ , not permitted for \ :literal:`action=delete`\ .

    | **required**: False
    | **type**: str


  verify
    If True (default), verify the HMC certificate as specified in the \ :literal:`hmc\_auth.ca\_certs`\  parameter. If False, ignore what is specified in the \ :literal:`hmc\_auth.ca\_certs`\  parameter and do not verify the HMC certificate.

    Optional for \ :literal:`action=create`\ , not permitted for \ :literal:`action=delete`\ .

    | **required**: False
    | **type**: bool
    | **default**: True



action
  The action to perform for the HMC session. Since an HMC session does not have a name, it is not possible to specify the desired end state in an idempotent manner, so this module uses actions:

  \* \ :literal:`create`\ : Create a new session on the HMC and verify that the credentials are valid. Requires \ :literal:`hmc\_auth.userid`\  and \ :literal:`hmc\_auth.password`\  and uses \ :literal:`hmc\_auth.ca\_certs`\  and \ :literal:`hmc\_auth.verify`\  if provided.

  \* \ :literal:`delete`\ : Delete the specified session on the HMC. No longer existing sessions are tolerated. Requires \ :literal:`hmc\_auth.session\_id`\ .

  | **required**: True
  | **type**: str
  | **choices**: create, delete


log_file
  File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.

  | **required**: False
  | **type**: str




Examples
--------

.. code-block:: yaml+jinja

   
   ---
   # Note: The following is a sequence of tasks that demonstrates the use
   #       of the zhmc_session module for one other ibm_zhmc task. The example
   #       assumes that some variables named 'my_*' are set.

   - name: Create an HMC session
     zhmc_session:
       hmc_host: "{{ my_hmc_host }}"  # Single HMC or list of redundant HMCs
       hmc_auth:
         userid: "{{ my_hmc_userid }}"
         password: "{{ my_hmc_password }}"
         verify: true                      # optional
         ca_certs: "{{ my_certs_dir }}"    # optional
       action: create
     register: session
     no_log: true    # Protect result containing HMC session ID from being logged

   - name: Example task using the previously created HMC session
     zhmc_cpc_list:
       hmc_host: "{{ session.hmc_host }}"  # The actually used HMC
       hmc_auth: "{{ session.hmc_auth }}"
     register: cpc_list

   - name: Delete the HMC session
     zhmc_session:
       hmc_host: "{{ session.hmc_host }}"  # The actually used HMC
       hmc_auth: "{{ session.hmc_auth }}"
       action: delete
     register: session    # Just for safety in case it is used after that










Return Values
-------------


changed
  Indicates if any change has been made by the module. This will always be false, since a session creation on the HMC does not count as a change.

  | **returned**: always
  | **type**: bool

msg
  An error message that describes the failure.

  | **returned**: failure
  | **type**: str

hmc_host
  The hostname or IP address of the HMC that was actually used for the session creation, for \ :literal:`action=create`\ . This value must be specified as \ :literal:`hmc\_host`\  for \ :literal:`action=delete`\ .

  For \ :literal:`action=delete`\ , returns the null value.

  | **returned**: success
  | **type**: str

hmc_auth
  Credentials for the HMC session, for use by other tasks. This return value should be protected with \ :literal:`no\_log=true`\  for \ :literal:`action=create`\ , since it contains the HMC session ID. For \ :literal:`action=delete`\ , the same structure is returned, just with null values. This can be used to reset the variable that was set for \ :literal:`action=create`\ .

  | **returned**: success
  | **type**: dict
  | **sample**:

    .. code-block:: json

        {
            "ca_certs": null,
            "session_id": "xyz.........",
            "verify": true
        }

  session_id
    New HMC session ID for \ :literal:`action=create`\ , or null for \ :literal:`action=delete`\ .

    | **type**: str

  ca_certs
    Value of \ :literal:`hmc\_auth.ca\_certs`\  input parameter for \ :literal:`action=create`\ , or null for \ :literal:`action=delete`\ .

    | **type**: str

  verify
    Value of \ :literal:`hmc\_auth.verify`\  input parameter for \ :literal:`action=create`\ , or null for \ :literal:`action=delete`\ .

    | **type**: bool


