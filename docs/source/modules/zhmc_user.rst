
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_user.py

.. _zhmc_user_module:


zhmc_user -- Create HMC users
=============================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gather facts about a user on an HMC of a Z system.
- Create, delete, or update a user on an HMC.


Requirements
------------

- The HMC userid must have these task permissions: 'Manage Users' (for standard users), 'Manage User Templates' (for template users).
- For updating its own HMC password, it is sufficient if the HMC userid has task permission for Manage Users or object-access permission for its own User object.




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



name
  The userid of the target user (i.e. the 'name' property of the User object).

  | **required**: True
  | **type**: str


state
  The desired state for the HMC user. All states are fully idempotent within the limits of the properties that can be changed:

  \* \ :literal:`absent`\ : Ensures that the user does not exist.

  \* \ :literal:`present`\ : Ensures that the user exists and has the specified properties.

  \* \ :literal:`facts`\ : Returns the user properties.

  | **required**: True
  | **type**: str
  | **choices**: absent, present, facts


properties
  Dictionary with desired properties for the user. Used for \ :literal:`state=present`\ ; ignored for \ :literal:`state=absent|facts`\ . Dictionary key is the property name with underscores instead of hyphens, and dictionary value is the property value in YAML syntax. Integer properties may also be provided as decimal strings.

  The possible input properties in this dictionary are the properties defined as writeable in the data model for User resources (where the property names contain underscores instead of hyphens), with the following exceptions:

  \* \ :literal:`name`\ : Cannot be specified because the name has already been specified in the \ :literal:`name`\  module parameter.

  \* \ :literal:`type`\ : Cannot be changed once the user exists.

  \* \ :literal:`user\_roles`\ : Cannot be set directly, but indirectly via the artificial property \ :literal:`user\_role\_names`\  which replaces the current user roles, if specified.

  \* \ :literal:`user\_pattern\_uri`\ : Cannot be set directly, but indirectly via the artificial property \ :literal:`user\_pattern\_name`\ .

  \* \ :literal:`password\_rule\_uri`\ : Cannot be set directly, but indirectly via the artificial property \ :literal:`password\_rule\_name`\ .

  \* \ :literal:`ldap\_server\_definition\_uri`\ : Cannot be set directly, but indirectly via the artificial property \ :literal:`ldap\_server\_definition\_name`\ .

  \* \ :literal:`default\_group\_uri`\ : Cannot be set directly, but indirectly via the artificial property \ :literal:`default\_group\_name`\ .

  Properties omitted in this dictionary will remain unchanged when the user already exists, and will get the default value defined in the data model for users in the :term:\`HMC API\` when the user is being created.

  | **required**: False
  | **type**: dict


expand
  Deprecated: The \ :literal:`expand`\  parameter is deprecated because the returned password rule, user role, user pattern and LDAP server definition objects have an independent lifecycle, so the same objects are returned when invoking this module in a loop through all users. Use the respective other modules of this collection to get the properties of these objects.

  Boolean that controls whether the returned user contains additional artificial properties that expand certain URI or name properties to the full set of resource properties (see description of return values of this module).

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

   - name: Gather facts about a user
     zhmc_user:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_user_name }}"
       state: facts
     register: user1

   - name: Ensure the user does not exist
     zhmc_user:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_user_name }}"
       state: absent

   - name: Ensure the user exists and has certain roles
     zhmc_user:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_user_name }}"
       state: present
       properties:
         description: "Example user 1"
         type: standard
         authentication_type: local
         password_rule_name: Basic
         password: foobar
         user_role_names:
           - hmc-access-administrator-tasks
           - hmc-all-system-managed-objects
     register: user1










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

user
  For \ :literal:`state=absent`\ , an empty dictionary.

  For \ :literal:`state=present|facts`\ , a dictionary with the resource properties of the target user, plus additional artificial properties as described in the following list items.

  | **returned**: success
  | **type**: dict
  | **sample**:

    .. code-block:: json

        {
            "allow-management-interfaces": true,
            "allow-remote-access": true,
            "authentication-type": "local",
            "class": "user",
            "default-group-uri": null,
            "description": "",
            "disable-delay": 1,
            "disabled": false,
            "disruptive-pw-required": true,
            "disruptive-text-required": false,
            "email-address": null,
            "force-password-change": false,
            "force-shared-secret-key-change": null,
            "idle-timeout": 0,
            "inactivity-timeout": 0,
            "is-locked": false,
            "ldap-server-definition-name": null,
            "ldap-server-definition-uri": null,
            "max-failed-logins": 3,
            "max-web-services-api-sessions": 1000,
            "min-pw-change-time": 0,
            "multi-factor-authentication-required": false,
            "name": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
            "object-id": "91773b88-0c99-11eb-b4d3-00106f237ab1",
            "object-uri": "/api/users/91773b88-0c99-11eb-b4d3-00106f237ab1",
            "parent": "/api/console",
            "password-expires": 87,
            "password-rule-name": "ZaaS",
            "password-rule-uri": "/api/console/password-rules/518ac1d8-bf98-11e9-b9dd-00106f237ab1",
            "replication-overwrite-possible": true,
            "session-timeout": 0,
            "type": "standard",
            "user-role-names": [
                "hmc-system-programmer-tasks"
            ],
            "user-roles": [
                "/api/user-roles/19e90e27-1cae-422c-91ba-f76ac7fb8b82"
            ],
            "userid-on-ldap-server": null,
            "verify-timeout": 15,
            "web-services-api-session-idle-timeout": 360
        }

  name
    User name

    | **type**: str

  {property}
    Additional properties of the user, as described in the data model of the 'User' object in the :term:\`HMC API\` book. The property names have hyphens (-) as described in that book.


  user-role-names
    Name of the user roles referenced by property \ :literal:`user-roles`\ .

    | **type**: str

  user-role-objects
    Deprecated: This result property is deprecated because the \ :literal:`expand`\  parameter is deprecated.

    Only if \ :literal:`expand=true`\ : User roles referenced by property \ :literal:`user-roles`\ .

    | **type**: dict

    {property}
      Properties of the user role, as described in the data model of the 'User Pattern' object in the :term:\`HMC API\` book. The property names have hyphens (-) as described in that book.



  user-pattern-name
    Only for users with \ :literal:`type=pattern`\ : Name of the user pattern referenced by property \ :literal:`user-pattern-uri`\ .

    | **type**: str

  user-pattern
    Deprecated: This result property is deprecated because the \ :literal:`expand`\  parameter is deprecated.

    Only for users with \ :literal:`type=pattern`\  and if \ :literal:`expand=true`\ : User pattern referenced by property \ :literal:`user-pattern-uri`\ .

    | **type**: dict

    {property}
      Properties of the user pattern, as described in the data model of the 'User Pattern' object in the :term:\`HMC API\` book. The property names have hyphens (-) as described in that book.



  password-rule-name
    Only for users with \ :literal:`authentication-type=local`\ : Name of the password rule referenced by property \ :literal:`password-rule-uri`\ .

    | **type**: str

  password-rule
    Deprecated: This result property is deprecated because the \ :literal:`expand`\  parameter is deprecated.

    Only for users with \ :literal:`authentication-type=local`\  and if \ :literal:`expand=true`\ : Password rule referenced by property \ :literal:`password-rule-uri`\ .

    | **type**: dict

    {property}
      Properties of the password rule, as described in the data model of the 'Password Rule' object in the :term:\`HMC API\` book. The property names have hyphens (-) as described in that book.



  ldap-server-definition-name
    Only for users with \ :literal:`authentication-type=ldap`\ : Name of the LDAP server definition referenced by property \ :literal:`ldap-server-definition-uri`\ .

    | **type**: str

  ldap-server-definition
    Deprecated: This result property is deprecated because the \ :literal:`expand`\  parameter is deprecated.

    Only for users with \ :literal:`authentication-type=ldap`\  and if \ :literal:`expand=true`\ : LDAP server definition referenced by property \ :literal:`ldap-server-definition-uri`\ .

    | **type**: dict

    {property}
      Properties of the LDAP server definition, as described in the data model of the 'LDAP Server Definition' object in the :term:\`HMC API\` book. The property names have hyphens (-) as described in that book.




