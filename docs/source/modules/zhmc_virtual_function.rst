
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_virtual_function.py

.. _zhmc_virtual_function_module:


zhmc_virtual_function -- Create virtual functions in partitions
===============================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Create, update, or delete a virtual function in a partition of a CPC (Z system).
- Note that the Ansible module zhmc\_partition can be used to gather facts about existing virtual functions of a partition.


Requirements
------------

- The targeted Z system must be in the Dynamic Partition Manager (DPM) operational mode.
- The HMC userid must have these task permissions: 'Partition Details'.
- The HMC userid must have object-access permissions to these objects: Backing accelerator adapters of the target virtual functions, partitions of the target virtual functions, CPCs of these partitions.




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
  The name of the CPC with the partition containing the virtual function.

  | **required**: True
  | **type**: str


partition_name
  The name of the partition containing the virtual function.

  | **required**: True
  | **type**: str


name
  The name of the target virtual function that is managed. If the virtual function needs to be created, this value becomes its name.

  | **required**: True
  | **type**: str


state
  The desired state for the virtual function. All states are fully idempotent within the limits of the properties that can be changed:

  \* \ :literal:`absent`\ : Ensures that the virtual function does not exist in the specified partition.

  \* \ :literal:`present`\ : Ensures that the virtual function exists in the specified partition and has the specified properties.

  | **required**: True
  | **type**: str
  | **choices**: absent, present


properties
  Dictionary with input properties for the virtual function, for \ :literal:`state=present`\ . Key is the property name with underscores instead of hyphens, and value is the property value in YAML syntax. Integer properties may also be provided as decimal strings. Will be ignored for \ :literal:`state=absent`\ .

  The possible input properties in this dictionary are the properties defined as writeable in the data model for Virtual Function resources (where the property names contain underscores instead of hyphens), with the following exceptions:

  \* \ :literal:`name`\ : Cannot be specified because the name has already been specified in the \ :literal:`name`\  module parameter.

  \* \ :literal:`adapter\_uri`\ : Cannot be specified because this information is specified using the artificial property \ :literal:`adapter\_name`\ .

  \* \ :literal:`adapter\_name`\ : The name of the adapter that backs the target virtual function.

  Properties omitted in this dictionary will remain unchanged when the virtual function already exists, and will get the default value defined in the data model for virtual functions when the virtual function is being created.

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
   # Note: The following examples assume that some variables named 'my_*' are set.

   - name: Ensure virtual function exists in the partition
     zhmc_partition:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       partition_name: "{{ my_partition_name }}"
       name: "{{ my_vfunction_name }}"
       state: present
       properties:
         adapter_name: "ABC-123"
         description: "The accelerator adapter"
         device_number: "033F"
     register: vfunction1

   - name: Ensure virtual function does not exist in the partition
     zhmc_partition:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc_name }}"
       partition_name: "{{ my_partition_name }}"
       name: "{{ my_vfunction_name }}"
       state: absent










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

virtual_function
  For \ :literal:`state=absent`\ , an empty dictionary.

  For \ :literal:`state=present`\ , the resource properties of the virtual function after any changes.

  | **returned**: success
  | **type**: dict

  name
    Virtual function name

    | **type**: str

  {property}
    Additional properties of the virtual function, as described in the data model of the 'Virtual Function' element object of the 'Partition' object in the :term:\`HMC API\` book. The property names have hyphens (-) as described in that book.



