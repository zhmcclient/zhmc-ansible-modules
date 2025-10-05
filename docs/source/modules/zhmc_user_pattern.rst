
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_user_pattern.py

.. _zhmc_user_pattern_module:
.. _ibm.ibm_zhmc.zhmc_user_pattern_module:


zhmc_user_pattern -- Manage an HMC user pattern
===============================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gather facts about a user pattern on an HMC of a Z system.
- Create, delete, or update a user pattern on an HMC.


Requirements
------------

- The HMC userid must have these task permissions: 'Manage User Patterns'.




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
  The name of the target user pattern.

  | **required**: True
  | **type**: str


state
  The desired state for the HMC user pattern. All states are fully idempotent within the limits of the properties that can be changed:

  \* :literal:`absent`\ : Ensures that the user pattern does not exist.

  \* :literal:`present`\ : Ensures that the user pattern exists and has the specified properties.

  \* :literal:`facts`\ : Returns the user pattern properties.

  | **required**: True
  | **type**: str
  | **choices**: absent, present, facts


properties
  Dictionary with desired properties for the user pattern. Used for :literal:`state=present`\ ; ignored for :literal:`state=absent\|facts`. Dictionary key is the property name with underscores instead of hyphens, and dictionary value is the property value in YAML syntax. Integer properties may also be provided as decimal strings.

  The possible input properties in this dictionary are the properties defined as writeable in the data model for User Pattern resources (where the property names contain underscores instead of hyphens), with the following exceptions:

  \* :literal:`name`\ : Cannot be specified because the name has already been specified in the :literal:`name` module parameter.

  \* :literal:`...\_uri`\ : Cannot be set directly, but indirectly via the corresponding artificial property :literal:`...\_name`. An empty string for the name will set the URI to null.

  Properties omitted in this dictionary will remain unchanged when the user pattern already exists, and will get the default value defined in the data model for user patterns in the :ref:`HMC API <HMC API>` book when the user pattern is being created.

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

   - name: Gather facts about a user pattern
     zhmc_user_pattern:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_user_pattern_name }}"
       state: facts
     register: userpattern1

   - name: Ensure the user pattern does not exist
     zhmc_user_pattern:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_user_pattern_name }}"
       state: absent

   - name: Ensure the user pattern exists and has certain properties
     zhmc_user_pattern:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_user_pattern_name }}"
       state: present
       properties:
         description: "Example user pattern 1"
     register: userpattern1










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

user_pattern
  For :literal:`state=absent`\ , an empty dictionary.

  For :literal:`state=present\|facts`\ , a dictionary with the resource properties of the target user pattern and some additional artificial properties.

  | **returned**: success
  | **type**: dict
  | **sample**:

    .. code-block:: json

        {
            "class": "user-pattern",
            "description": "A pattern that matches a bluepages email address.",
            "domain_name_restrictions": null,
            "domain_name_restrictions_ldap_server_definition_name": null,
            "domain_name_restrictions_ldap_server_definition_uri": null,
            "element_id": "cbcaf7a0-46cc-11e9-bfd3-f44a39cd42f9",
            "element_uri": "/api/console/user-patterns/cbcaf7a0-46cc-11e9-bfd3-f44a39cd42f9",
            "ldap_group_default_template_name": null,
            "ldap_group_default_template_uri": null,
            "ldap_group_ldap_server_definition_name": null,
            "ldap_group_ldap_server_definition_uri": null,
            "ldap_group_to_template_mappings": null,
            "ldap_server_definition_name": null,
            "ldap_server_definition_uri": null,
            "name": "Bluepages email address",
            "parent": "/api/console",
            "pattern": "*@*ibm.com",
            "replication_overwrite_possible": false,
            "retention_time": 90,
            "search_order_index": 0,
            "specific_template_name": "Product Engineering and Access Administrator",
            "specific_template_uri": "/api/users/97769500-4a81-11e9-aa1b-00106f23f636",
            "template_name_override": null,
            "template_name_override_default_template_name": null,
            "template_name_override_default_template_uri": null,
            "template_name_override_ldap_server_definition_name": null,
            "template_name_override_ldap_server_definition_uri": null,
            "type": "glob-like",
            "user_template_name": "Product Engineering and Access Administrator",
            "user_template_uri": "/api/users/97769500-4a81-11e9-aa1b-00106f23f636"
        }

  name
    User Pattern name

    | **type**: str

  {property}
    Additional properties of the user pattern, as described in the data model of the 'User Pattern' object in the :ref:`HMC API <HMC API>` book. The property names will have underscores instead of hyphens.

    The items in the :literal:`ldap\_group\_to\_template\_mappings` property have an additional item :literal:`template\-name` which is the name of the resource object referenced by :literal:`template\-uri`.

    | **type**: raw

  domain_name_restrictions_ldap_server_definition_name
    Name of the resource object referenced by the corresponding ...\_uri property.

    | **type**: str

  ldap_group_default_template_name
    Name of the resource object referenced by the corresponding ...\_uri property.

    | **type**: str

  ldap_group_ldap_server_definition_name
    Name of the resource object referenced by the corresponding ...\_uri property.

    | **type**: str

  ldap_server_definition_name
    Name of the resource object referenced by the corresponding ...\_uri property.

    | **type**: str

  specific_template_name
    Name of the resource object referenced by the corresponding ...\_uri property.

    | **type**: str

  template_name_override_default_template_name
    Name of the resource object referenced by the corresponding ...\_uri property.

    | **type**: str

  template_name_override_ldap_server_definition_name
    Name of the resource object referenced by the corresponding ...\_uri property.

    | **type**: str

  user_template_name
    Name of the resource object referenced by the corresponding ...\_uri property.

    | **type**: str


