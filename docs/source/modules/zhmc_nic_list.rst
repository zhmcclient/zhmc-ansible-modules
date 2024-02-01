
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_nic_list.py

.. _zhmc_nic_list_module:


zhmc_nic_list -- List NICs
==========================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- List NICs on a specific partition of a CPC (Z system).


Requirements
------------

- The HMC userid must have object-access permissions to these objects: Target partition, CPC of target partition (only for HMC 2.13.0 and older).




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
  Name of the CPC with the partition whose NICs are to be listed.

  | **required**: True
  | **type**: str


partition_name
  Name of the partition whose NICs are to be listed.

  | **required**: True
  | **type**: str


full_properties
  If True, all properties of each NIC will be returned. Default: False.

  Note: Setting this to True causes a loop of 'Get NIC Properties' operations to be executed.

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

   - name: List the NICs of a partition
     zhmc_nic_list:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: CPCA
       partition_name: PART1
     register: nic_list






See Also
--------

.. seealso::

   - :ref:`zhmc_nic_module`




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

nics
  The list of NICs of the partition, with a subset of their properties.

  | **returned**: success
  | **type**: list
  | **elements**: dict
  | **sample**:

    .. code-block:: json

        [
            {
                "cpc_name": "CPC1",
                "name": "nic1",
                "partition_name": "partition1"
            }
        ]

  name
    NIC name

    | **type**: str

  partition_name
    Name of the parent partition of the NIC

    | **type**: str

  cpc_name
    Name of the parent CPC of the partition

    | **type**: str

  {additional_property}
    Additional properties requested via \ :literal:`full\_properties`\ . The property names will have underscores instead of hyphens.

    | **type**: raw


