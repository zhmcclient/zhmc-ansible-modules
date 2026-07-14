
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_storage_group_list.py

.. _zhmc_storage_group_list_module:
.. _ibm.ibm_zhmc.zhmc_storage_group_list_module:


zhmc_storage_group_list -- List storage groups (DPM mode)
=========================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- List storage groups.
- The returned storage groups can be filtered by name, associated CPC, type (fc/fcp) and fulfillment state.
- CPCs in classic mode are ignored (i.e. do not lead to a failure).
- Storage groups for which the user has no object access permission are ignored (i.e. do not lead to a failure).


Requirements
------------

- Requires HMC version 2.14 or later (to have the "dpm\-storage\-management" firmware feature) and must be in the Dynamic Partition Manager (DPM) operational mode.
- The HMC userid must have object\-access permissions to these objects: Target storage groups.




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



name
  Filter to limit returned storage groups to those whose name matches the specified regular expression pattern.

  If None/null, no such filtering happens.

  | **required**: False
  | **type**: str


cpc_name
  Filter pattern to limit returned storage groups to those whose associated CPC has the specified name.

  If None/null, no such filtering happens.

  | **required**: False
  | **type**: str


type
  Filter to limit returned storage groups to those that have the specified type (fcp=FB/FCP, fc=ECKD/FICON).

  If None/null, no such filtering happens.

  | **required**: False
  | **type**: str
  | **choices**: fcp, fc


fulfillment_state
  Filter to limit returned storage groups to those that have the specified fulfillment state.

  If None/null, no such filtering happens.

  For possible values, see the description of property "fulfillment\-state" in the data model of the Storage Group object in the :ref:`HMC API <HMC API>` book.

  | **required**: False
  | **type**: str


full_properties
  If True, all properties of each storage group will be returned. Default: False.

  Note: Setting this to True causes a loop of 'Get Storage Group Properties' operations to be executed.

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

   - name: List the storage groups on all managed CPCs
     zhmc_storage_group_list:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
     register: storage_group_list

   - name: List the FCP-type storage groups on CPCA
     zhmc_storage_group_list:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       cpc_name: CPCA
       type: fcp
     register: storage_group_list






See Also
--------

.. seealso::

   - :ref:`ibm.ibm_zhmc.zhmc_storage_group_module`




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

storage_groups
  The list of storage groups, with a subset of their properties.

  | **returned**: success
  | **type**: list
  | **elements**: dict
  | **sample**:

    .. code-block:: json

        [
            {
                "cpc_name": "CPC1",
                "cpc_uri": "/api/cpcs/....",
                "fulfillment_state": "complete",
                "name": "storage_group1",
                "object_uri": "/api/storage-groups/....",
                "type": "fcp"
            }
        ]

  name
    Storage group name

    | **type**: str

  object_uri
    Canonical URI of the storage group object

    | **type**: str

  cpc_name
    Name of the CPC to which the storage group is associated

    | **type**: str

  cpc_uri
    Canonical URI of the associated CPC

    | **type**: str

  type
    Type of the storage group (fcp=FB/FCP, fc=ECKD/FICON).

    | **type**: str

  fulfillment_state
    The current fulfillment state of the storage group. For possible values, see the description of property "fulfillment\-state" in the data model of the Storage Group object in the :ref:`HMC API <HMC API>` book.

    | **type**: str

  {additional_property}
    Additional properties requested via :literal:`full\_properties`. The property names will have underscores instead of hyphens.

    | **type**: raw


