
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_partition_messages.py

.. _zhmc_partition_messages_module:


zhmc_partition_messages -- Get console messages for OS in a partition
=====================================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Get the OS console messages for the OS running in an active partition.


Requirements
------------

- The targeted CPC must be in the DPM operational mode.
- The targeted partition must be active (i.e. running an operating system).
- The HMC userid must have these task permissions: 'Operating System Messages' (view-only is sufficient)
- The HMC userid must have object-access permissions to these objects: Target CPC, target partition.




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



cpc_name
  The name of the CPC with the target partition.

  | **required**: True
  | **type**: str


name
  The name of the target partition.

  | **required**: True
  | **type**: str


begin
  A message sequence number to limit returned messages. Messages with a sequence number less than this are omitted from the results.

  If null, no such filtering is performed.

  | **required**: False
  | **type**: int


end
  A message sequence number to limit returned messages. Messages with a sequence number greater than this are omitted from the results.

  If null, no such filtering is performed.

  | **required**: False
  | **type**: int


log_file
  File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.

  | **required**: False
  | **type**: str




Examples
--------

.. code-block:: yaml+jinja

   
   ---
   # Note: The following examples assume that some variables named 'my_*' are set.

   - name: Get OS console messages for the OS in the partition
     zhmc_partition_messages:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       name: "{{ my_part_name }}"
     register: part_messages











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

messages
  The list of operating system console messages.

  | **returned**: success
  | **type**: list
  | **elements**: dict
  | **sample**:

    .. code-block:: json

        [
            {
                "is_held": false,
                "is_priority": false,
                "message_id": 2328551,
                "message_text": "Uncompressing Linux... ",
                "os_name": null,
                "prompt_text": "",
                "sequence_number": 0,
                "sound_alarm": false,
                "timestamp": null
            },
            {
                "is_held": false,
                "is_priority": false,
                "message_id": 2328552,
                "message_text": "Ok, booting the kernel. ",
                "os_name": null,
                "prompt_text": "",
                "sequence_number": 1,
                "sound_alarm": false,
                "timestamp": null
            }
        ]

  sequence_number
    The sequence number assigned to this message by the HMC.

    Although sequence numbers may wrap over time, this number can be considered a unique identifier for the message.

    | **type**: int

  message_text
    The text of the message

    | **type**: str

  message_id
    The message identifier assigned to this message by the operating system.

    | **type**: str

  timestamp
    The point in time (as an ISO 8601 date and time value) when the message was created, or null if this information is not available from the operating system.

    | **type**: str

  sound_alarm
    Indicates whether the message should cause the alarm to be sounded.

    | **type**: bool

  is_priority
    Indicates whether the message is a priority message.

    A priority message indicates a critical condition that requires immediate attention.

    | **type**: bool

  is_held
    Indicates whether the message is a held message.

    A held message is one that requires a response.

    | **type**: bool

  prompt_text
    The prompt text that is associated with this message, or null indicating that there is no prompt text for this message.

    The prompt text is used when responding to a message. The response is to be sent as an operating system command where the command is prefixed with the prompt text and followed by the response to the message.

    | **type**: str

  os_name
    The name of the operating system that generated this omessage, or null indicating there is no operating system name  associated with this message.

    This name is determined by the operating system and may be unrelated to the name of the partition in which the operating system is running.

    | **type**: str


