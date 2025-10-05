
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_partition_command.py

.. _zhmc_partition_command_module:
.. _ibm.ibm_zhmc.zhmc_partition_command_module:


zhmc_partition_command -- Execute OS console command in a partition (DPM mode)
==============================================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Execute a command in the console of the OS running in a partition and get back the command output.
- Note: The OS console interface provided by the HMC WS\-API does not allow separating multiple concurrent interactions. For example, when OS console commands are executed via the HMC GUI at the same time when executing this Ansible module, the command output returned by the Ansible module may be mixed with output from the concurrently executed command.
- Note: The logic for determining which lines on the OS console belong to the executed command is as follows: The OS console messages are started to be captured just before the console command is sent. The captured console messages are then searched for the occurrence of the command. The command itself and all messages following the command are considered part of the command output, until there are no more new messages for 2 seconds. If there is a lot of traffic on the OS console, that may lead to other messages being included in the command output.


Requirements
------------

- The targeted CPC must be in the DPM operational mode.
- The targeted partition must be active (i.e. running an operating system).
- The HMC userid must have these task permissions: 'Operating System Messages' (view\-only is sufficient)
- The HMC userid must have object\-access permissions to these objects: Target CPC, target partition.




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
  The name of the CPC with the target partition.

  | **required**: True
  | **type**: str


name
  The name of the target partition.

  | **required**: True
  | **type**: str


command
  The OS console command to be executed.

  | **required**: True
  | **type**: str


is_priority
  Controls whether the command is executed as a priority command.

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

   - name: Get z/VM CP level via OS console command
     zhmc_partition_command:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       name: "{{ my_partition_name }}"
       command: "Q CPLEVEL"
     register: zvm_cplevel_output










Return Values
-------------


changed
  Indicates if any change has been made by the module.

  This will always be true, because it is not clear whether the command has performed a change. Note that a playbook using this module with a command that does not perform a change can override that by specifying :literal:`changed\_when: false`.

  | **returned**: always
  | **type**: bool

msg
  An error message that describes the failure.

  | **returned**: failure
  | **type**: str

output
  The command and its output, as one item per line, without any trailing newlines.

  The format of each message text depends on the type of OS. Typical formats are, showing the message with the command:

  z/VM: :literal:`04:30:02 Q CPLEVEL`

  Linux: :literal:`uname \-a`

  | **returned**: success
  | **type**: list
  | **elements**: str
  | **sample**:

    .. code-block:: json

        [
            "04:30:02 Q CPLEVEL",
            "04:30:02 z/VM Version 7 Release 2.0, service level 2101 (64-bit)",
            "04:30:02 Generated at 05/19/21 10:00:00 CES",
            "04:30:02 IPL at 06/04/24 19:18:57 CES"
        ]

