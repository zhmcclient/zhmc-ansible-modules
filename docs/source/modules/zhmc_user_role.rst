
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_user_role.py

.. _zhmc_user_role_module:
.. _ibm.ibm_zhmc.zhmc_user_role_module:


zhmc_user_role -- Manage an HMC user role
=========================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gather facts about a user role on an HMC of a Z system.
- Create, delete, or update a user role on an HMC.


Requirements
------------

- The HMC userid must have these task permissions: 'Manage User Roles'.




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
  The name of the target user role.

  | **required**: True
  | **type**: str


state
  The desired state for the HMC user role. All states are fully idempotent within the limits of the properties that can be changed:

  \* :literal:`absent`\ : Ensures that the user role does not exist.

  \* :literal:`present`\ : Ensures that the user role exists and has the specified properties.

  \* :literal:`facts`\ : Returns the user role properties.

  | **required**: True
  | **type**: str
  | **choices**: absent, present, facts


properties
  Dictionary with desired properties for the user role. Used for :literal:`state=present`\ ; ignored for :literal:`state=absent\|facts`. Dictionary key is the property name with underscores instead of hyphens, and dictionary value is the property value in YAML syntax. Integer properties may also be provided as decimal strings.

  The possible input properties in this dictionary are the properties defined as writeable in the data model for user role resources (where the property names contain underscores instead of hyphens), with the following exceptions:

  \* :literal:`name`\ : Cannot be specified because the name has already been specified in the :literal:`name` module parameter.

  \* :literal:`associated\_system\_defined\_user\_role\_uri`\ : Cannot be specified because this information is specified using the artificial property :literal:`associated\_system\_defined\_user\_role\_name`.

  \* :literal:`associated\_system\_defined\_user\_role\_name`\ : The name of the associated system\-defined user role.

  \* :literal:`permissions`\ : Can be specified as if it were writeable.

  Properties omitted in this dictionary will remain unchanged when the user role already exists, and will get the default value defined in the data model for user roles in the :ref:`HMC API <HMC API>` book when the user role is being created.

  | **required**: False
  | **type**: dict


  {property}
    Any other property defined as writeable in the data model for user role resources (where the property names contain underscores instead of hyphens), except those excluded in the description above.

    | **required**: False
    | **type**: raw


  associated_system_defined_user_role_name
    The name of the associated system\-defined user role. Specifying it requires that the referenced user role exists.

    Optional, default: :literal:`hmc\-operator\-tasks`.

    | **required**: False
    | **type**: str


  permissions
    The permissions for this user role.

    This property is represented different from its description in the :ref:`HMC API <HMC API>`\ : The property is a list of permissions. Each list item is a dictionary that specifies a single permission item, any required scoping items, and optional option items.

    | **required**: False
    | **type**: list
    | **elements**: dict


    task
      Permission item: Task permission to the task with the specified name.

      | **required**: False
      | **type**: str


    view_only
      Option item only for :literal:`task`\ : Indicates whether the task's view\-only version is subject of the permission. Only certain tasks have a view\-only version. Default: true.

      | **required**: False
      | **type**: bool


    class
      Permission item: Object permission to all objects of the specified resource class (= value of :literal:`class` property).

      | **required**: False
      | **type**: str


    group
      Permission item: Object permission to the group with the specified name and optionally to its members.

      | **required**: False
      | **type**: str


    include_members
      Option item only for :literal:`group`\ : Indicates whether the group members are included in the permission. Default: false.

      | **required**: False
      | **type**: bool


    cpc
      Permission item: Object permission to the CPC with the specified name.

      Scoping item: Specifies the CPC name as a scope for the names specified in other permission items.

      | **required**: False
      | **type**: str


    partition
      Permission item: Object permission to the partition with the specified name on the specified CPC (in DPM mode).

      Requires :literal:`cpc` to be specified as a scoping item.

      | **required**: False
      | **type**: str


    lpar
      Permission item: Object permission to the LPAR with the specified name on the specified CPC (in classic mode).

      Requires :literal:`cpc` to be specified as a scoping item.

      | **required**: False
      | **type**: str


    adapter
      Permission item: Object permission to the adapter with the specified name on the specified CPC (in DPM mode).

      Requires :literal:`cpc` to be specified as a scoping item.

      | **required**: False
      | **type**: str


    storage_group
      Permission item: Object permission to the storage group with the specified name that is associated with the specified CPC (in DPM mode).

      Requires :literal:`cpc` to be specified as a scoping item.

      | **required**: False
      | **type**: str


    storage_group_template
      Permission item: Object permission to the storage group template with the specified name that is associated with the specified CPC (in DPM mode).

      Requires :literal:`cpc` to be specified as a scoping item.

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

   - name: Gather facts about a user role
     zhmc_user_role:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_user_role_name }}"
       state: facts
     register: rule1

   - name: Ensure the user role does not exist
     zhmc_user_role:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_user_role_name }}"
       state: absent

   - name: Ensure the user role exists and has certain properties
     zhmc_user_role:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_user_role_name }}"
       state: present
       properties:
         description: "Example user role 1"
         permissions:
           # Task permission to "configure-storage-storageadmin":
           - task: "configure-storage-storageadmin"
           # Task permission to the view-only version of "hardware-messages":
           - task: "hardware-messages"
             view_only: true
           # Object permission to all CPCs:
           - class: cpc
           # Object permission to part1 in cpc1:
           - partition: part1
             cpc: cpc1
           # Object permission to part2 in cpc2:
           - partition: part2
             cpc: cpc2
     register: rule1










Return Values
-------------


changed
  Indicates if any change has been made by the module. For :literal:`state=facts`\ , always will be false.

  | **returned**: always
  | **type**: bool

msg
  An error message that describes the failure.

  | **returned**: failure
  | **type**: str

user_role
  For :literal:`state=absent`\ , an empty dictionary.

  For :literal:`state=present\|facts`\ , a dictionary with the resource properties of the target user role.

  | **returned**: success
  | **type**: dict
  | **sample**:

    .. code-block:: json

        {
            "associated-system-defined-user-role-name": "hmc-operator-tasks",
            "associated-system-defined-user-role-uri": "/api/user-roles/e8c098cb-0597-4003-8e5b-e3a63476c2f8",
            "class": "user-role",
            "description": "zhmc test user role 1",
            "is-inheritance-enabled": false,
            "is-locked": false,
            "name": "zhmc_test_role_1",
            "object-id": "3dc87062-f651-11ec-8ea3-00106f25b43c",
            "object-uri": "/api/user-roles/3dc87062-f651-11ec-8ea3-00106f25b43c",
            "parent": "/api/console",
            "permissions": [
                {
                    "task": "configure-storage-storageadmin"
                },
                {
                    "task": "hardware-messages",
                    "view_only": true
                },
                {
                    "task": "se-cryptographic-management",
                    "view_only": false
                },
                {
                    "class": "cpc"
                },
                {
                    "cpc": "P000A218",
                    "partition": "Test"
                },
                {
                    "adapter": "HiSoClassic",
                    "cpc": "P000A218"
                }
            ],
            "replication-overwrite-possible": false,
            "type": "user-defined"
        }

  name
    User role name

    | **type**: str

  associated-system-defined-user-role-name
    The name of the associated system\-defined user role

    | **type**: str

  permissions
    The permissions for this user role.

    This property is represented different from its description in the :ref:`HMC API <HMC API>`\ : The property is a list of permissions. Each list item is a dictionary that specifies a single permission item, any needed scoping items, and any applicable option items.

    | **type**: list
    | **elements**: dict

    task
      Permission item: Task permission to the task with the specified name.

      | **type**: str

    view_only
      Option item present for :literal:`task`\ : Indicates whether the task's view\-only version is subject of the permission. Only certain tasks have a view\-only version, but the option item will be present for all tasks.

      | **type**: bool

    class
      Permission item: Object permission to all objects of the specified resource class (= value of :literal:`class` property).

      | **type**: str

    group
      Permission item: Object permission to the group with the specified name and optionally to its members.

      | **type**: str

    include_members
      Option item present for :literal:`group`\ : Indicates whether the group members are included in the permission. The option item will be present for all groups.

      | **type**: bool

    cpc
      Permission item: Object permission to the CPC with the specified name.

      Scoping item: Specifies the CPC name as a scope for the names specified in other permission items.

      | **type**: str

    partition
      Permission item: Object permission to the partition with the specified name on the specified CPC (in DPM mode).

      :literal:`cpc` will be present as a scoping item.

      | **type**: str

    lpar
      Permission item: Object permission to the LPAR with the specified name on the specified CPC (in classic mode).

      :literal:`cpc` will be present as a scoping item.

      | **type**: str

    adapter
      Permission item: Object permission to the adapter with the specified name on the specified CPC (in DPM mode).

      :literal:`cpc` will be present as a scoping item.

      | **type**: str

    storage_group
      Permission item: Object permission to the storage group with the specified name that is associated with the specified CPC (in DPM mode).

      :literal:`cpc` will be present as a scoping item.

      | **type**: str

    storage_group_template
      Permission item: Object permission to the storage group template with the specified name that is associated with the specified CPC (in DPM mode).

      :literal:`cpc` will be present as a scoping item.

      | **type**: str


  {property}
    Additional properties of the user role, as described in the data model of the 'User Role' object in the :ref:`HMC API <HMC API>` book. The property names have hyphens (\-) as described in that book.

    | **type**: raw


