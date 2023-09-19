
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_console.py

.. _zhmc_console_module:


zhmc_console -- Manage the HMC
==============================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Get facts about the targeted HMC.
- Upgrade the firmware of the targeted HMC.


Requirements
------------

- For \ :literal:`state=facts`\ , no specific task or object-access permissions are required.
- For \ :literal:`state=upgrade`\ , task permission to the 'Single Step Console Internal Code' task is required.




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



state
  The action to be performed on the HMC:

  \* \ :literal:`facts`\ : Returns facts about the HMC.

  \* \ :literal:`upgrade`\ : Upgrades the firmware of the HMC and returns the new facts after the upgrade. If the HMC firmware is already at the requested bundle level, nothing is changed and the module succeeds.

  | **required**: True
  | **type**: str
  | **choices**: facts, upgrade


bundle_level
  Name of the bundle to be installed on the HMC (e.g. 'H71')

  Required for \ :literal:`state=upgrade`\ 

  | **required**: False
  | **type**: str


backup_location_type
  Type of backup location for the HMC backup that is performed:

  \* 'ftp': The FTP server that was used for the last console backup as defined on the 'Configure Backup Settings' user interface task in the HMC GUI.

  \* 'usb': The USB storage device mounted to the HMC.

  Optional for \ :literal:`state=upgrade`\ , default: 'usb'

  | **required**: False
  | **type**: str
  | **choices**: ftp, usb


accept_firmware
  Accept the previous bundle level before installing the new level.

  Optional for \ :literal:`state=upgrade`\ , default: True

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

   - name: Gather facts about the HMC
     zhmc_console:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       state: facts
     register: hmc1

   - name: Upgrade the HMC firmware and return facts
     zhmc_console:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       state: upgrade
       bundle_level: "H71"
     register: hmc1










Return Values
-------------


changed
  Indicates if any change has been made by the module. For \ :literal:`state=facts`\ , always will be false.

  | **returned**: always
  | **type**: bool

msg
  An error message that describes the failure.

  | **returned**: failure
  | **type**: str

hmc
  The facts about the HMC.

  | **returned**: success
  | **type**: dict
  | **sample**:

    .. code-block:: json

        {
            "api_version": {
                "{property}": "... from Query API Version operation ... "
            },
            "name": "HMC1",
            "{property}": "... more Console properties ... "
        }

  name
    HMC name

    | **type**: str

  {property}
    Additional properties of the Console object representing the targeted HMC, as described in the data model of the 'Console' object in the :term:\`HMC API\` book. Note that the set of properties has been extended over the past HMC versions, so you will get less properties on older HMC versions. The property names have hyphens (-) as described in that book.


  api_version
    Additional facts from the 'Query API Version' operation.

    | **type**: dict

    {property}
      The properties returned from the 'Query API Version' operation, as described in the :term:\`HMC API\` book. Note that the set of properties has been extended over the past HMC versions, so you will get less properties on older HMC versions. The property names have hyphens (-) as described in that book.




