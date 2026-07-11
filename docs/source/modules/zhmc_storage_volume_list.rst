
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_storage_volume_list.py

.. _zhmc_storage_volume_list_module:
.. _ibm.ibm_zhmc.zhmc_storage_volume_list_module:


zhmc_storage_volume_list -- List storage volumes of a storage group (DPM mode)
==============================================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- List storage volumes of a specific storage group.
- The returned storage volumes can be filtered by name, fulfillment state, minimum and maximum size, and usage (boot/data).
- CPCs in classic mode are ignored (i.e. do not lead to a failure).


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



storage_group_name
  Name of the storage group whose storage volumes are to be listed.

  | **required**: True
  | **type**: str


name
  Filter to limit returned storage volumes to those whose name matches the specified regular expression pattern.

  If None/null, no such filtering happens.

  | **required**: False
  | **type**: str


fulfillment_state
  Filter to limit returned storage volumes to those that have the specified fulfillment state.

  If None/null, no such filtering happens.

  For possible values, see the description of property "fulfillment\-state" in the data model of the Storage Volume object in the :ref:`HMC API <HMC API>` book.

  | **required**: False
  | **type**: str


maximum_size
  Filter to limit returned storage volumes to those with a size that is less than or equal to the specified maximum size (in GiB).

  If None/null, no such filtering happens.

  | **required**: False
  | **type**: int


minimum_size
  Filter to limit returned storage volumes to those with a size that is greater than or equal to the specified minimum size (in GiB).

  If None/null, no such filtering happens.

  | **required**: False
  | **type**: int


usage
  Filter to limit returned storage volumes to those with the specified usage (boot/data).

  If None/null, no such filtering happens.

  | **required**: False
  | **type**: str
  | **choices**: boot, data


additional_properties
  List of additional properties to be returned for each storage volume, in addition to the default properties (see result description).

  Mutually exclusive with :literal:`full\_properties`.

  The property names are specified with underscores instead of hyphens.

  Not all properties defined in the data model are supported. For supported properties, see the description of query parameter "additional\-properties" in the "List Storage Volumes of a Storage Group" operation in the :ref:`HMC API <HMC API>` book.

  | **required**: False
  | **type**: list
  | **elements**: str


full_properties
  If True, all properties of each storage volume will be returned. Default: False.

  Mutually exclusive with :literal:`additional\_properties`.

  Note: Setting this to True causes a loop of 'Get Storage Group Properties' operations to be executed. It is preferable from a performance perspective to use the :literal:`additional\_properties` parameter instead.

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

   - name: List the volumes of storage group SG1
     zhmc_storage_volume_list:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       storage_group_name: SG1
     register: storage_volume_list

   - name: List the data volumes of storage group SG1
     zhmc_storage_volume_list:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       storage_group_name: SG1
       usage: data
     register: storage_volume_list






See Also
--------

.. seealso::

   - :ref:`ibm.ibm_zhmc.zhmc_storage_volume_module`




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

storage_volumes
  The list of storage volumes, with a subset of their properties.

  | **returned**: success
  | **type**: list
  | **elements**: dict
  | **sample**:

    .. code-block:: json

        [
            {
                "element_uri": "/api/storage-groups/..../storage-volumes/....",
                "fulfillment_state": "complete",
                "name": "storage_volume1",
                "size": 500.0,
                "usage": "boot"
            }
        ]

  name
    Storage volume name

    | **type**: str

  element_uri
    Canonical URI of the storage volume object

    | **type**: str

  fulfillment_state
    The current fulfillment state of the storage volume. For possible values, see the description of property "fulfillment\-state" in the data model of the Storage Group object in the :ref:`HMC API <HMC API>` book.

    | **type**: str

  size
    Size of the volume, in GiB.

    | **type**: float

  usage
    Usage of the volume (boot/data).

    | **type**: str

  {additional_property}
    Additional properties requested via :literal:`full\_properties`. The property names will have underscores instead of hyphens.

    | **type**: raw


