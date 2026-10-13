
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_storage_group_attachment_list.py

.. _zhmc_storage_group_attachment_list_module:
.. _ibm.ibm_zhmc.zhmc_storage_group_attachment_list_module:


zhmc_storage_group_attachment_list -- List the partitions attached to a storage group (DPM mode)
================================================================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- List the partitions attached to a storage group.
- The returned partitions can be filtered by name and status.


Requirements
------------

- Requires HMC version 2.14 or later (to have the "dpm\-storage\-management" firmware feature) and must be in the Dynamic Partition Manager (DPM) operational mode.
- The HMC userid must have object\-access permissions to these objects: Target storage group.




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
  The name of the CPC associated with the target storage group.

  | **required**: True
  | **type**: str


name
  The name of the target storage group.

  | **required**: True
  | **type**: str


partition_name
  Filter to limit returned partitions to those whose name matches the specified regular expression pattern.

  If None/null, no such filtering happens.

  | **required**: False
  | **type**: str


partition_status
  Filter to limit returned partitions to those that have the specified status.

  If None/null, no such filtering happens.

  For possible values, see the description of property "status" in the data model of the Partition object in the :ref:`HMC API <HMC API>` book.

  | **required**: False
  | **type**: str


log_file
  File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.

  | **required**: False
  | **type**: str




Examples
--------

.. code-block:: yaml+jinja

   
   ---
   # Note: The following examples assume that some variables named 'my_*' are set.

   - name: List the partitions attached to a storage group
     zhmc_storage_group_attachment_list:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: "{{ my_cpc }}"
       name: "{{ my_name }}"
     register: storage_group_attachment_list






See Also
--------

.. seealso::

   - :ref:`ibm.ibm_zhmc.zhmc_storage_group_attachment_module`




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

partitions
  The list of attached partitions, with a subset of their properties.

  | **returned**: success
  | **type**: list
  | **elements**: dict
  | **sample**:

    .. code-block:: json

        [
            {
                "cpc_name": "CPC1",
                "cpc_uri": "/api/cpcs/....",
                "name": "partition1",
                "object_uri": "/api/partitions/....",
                "status": "active"
            }
        ]

  name
    Partition name

    | **type**: str

  object_uri
    Canonical URI of the Partition

    | **type**: str

  cpc_uri
    Canonical URI of the CPC of the partition

    | **type**: str

  cpc_name
    Name of the CPC of the partition

    | **type**: str

  status
    The status of the partition. For possible values, see the description of property "status" in the data model of the Partition object in the :ref:`HMC API <HMC API>` book.

    | **type**: str


