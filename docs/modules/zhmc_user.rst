
:github_url: https://github.com/IBM/ibm_zos_zosmf/tree/master/plugins/modules/zhmc_user.py

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





Parameters
----------


     
hmc_host
  The hostname or IP address of the HMC.


  | **required**: True
  | **type**: str


     
hmc_auth
  The authentication credentials for the HMC, as a dictionary of ``userid``, ``password``.


  | **required**: True
  | **type**: dict


     
  userid
    The userid (username) for authenticating with the HMC.


    | **required**: True
    | **type**: str


     
  password
    The password for authenticating with the HMC.


    | **required**: True
    | **type**: str



     
name
  The userid of the target user (i.e. the 'name' property of the User object).


  | **required**: True
  | **type**: str


     
state
  The desired state for the target user:

  * ``absent``: Ensures that the user does not exist.

  * ``present``: Ensures that the user exists and has the specified properties.

  * ``facts``: Does not change anything on the user and returns the user properties.


  | **required**: True
  | **type**: str
  | **choices**: absent, present, facts


     
properties
  Dictionary with desired properties for the user. Used for ``state=present``; ignored for ``state=absent|facts``. Dictionary key is the property name with underscores instead of hyphens, and dictionary value is the property value in YAML syntax. Integer properties may also be provided as decimal strings.

  The possible input properties in this dictionary are the properties defined as writeable in the data model for User resources (where the property names contain underscores instead of hyphens), with the following exceptions:

  * ``name``: Cannot be specified because the name has already been specified in the ``name`` module parameter.

  * ``type``: Cannot be changed once the user exists.

  * ``user-pattern-uri``: Cannot be set directly, but indirectly via the artificial property ``user-pattern-name``.

  * ``password-rule-uri``: Cannot be set directly, but indirectly via the artificial property ``password-rule-name``.

  * ``ldap-server-definition-uri``: Cannot be set directly, but indirectly via the artificial property ``ldap-server-definition-name``.

  * ``default-group-uri``: Cannot be set directly, but indirectly via the artificial property ``default-group-name``.

  Properties omitted in this dictionary will remain unchanged when the user already exists, and will get the default value defined in the data model for users in the :term:`HMC API` when the user is being created.


  | **required**: False
  | **type**: dict


     
expand
  Boolean that controls whether the returned user contains additional artificial properties that expand certain URI or name properties to the full set of resource properties (see description of return values of this module).


  | **required**: False
  | **type**: bool


     
log_file
  File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.


  | **required**: False
  | **type**: str


     
_faked_session
  An internal parameter used for testing the module.


  | **required**: False
  | **type**: raw




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
       expand: true
     register: user1

   - name: Ensure the user does not exist
     zhmc_user:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_user_name }}"
       state: absent

   - name: Ensure the user exists
     zhmc_user:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_user_name }}"
       state: present
       expand: true
       properties:
         description: "Example user 1"
         type: standard
     register: user1











Return Values
-------------


   changed
        Indicates if any change has been made by the module. For ``state=facts``, always will be false.


        | **returned**: always
        | **type**: bool



   msg
        An error message that describes the failure.


        | **returned**: failure
        | **type**: str



   user
        For ``state=absent``, an empty dictionary.

        For ``state=present|facts``, a dictionary with the resource properties of the target user, plus additional artificial properties as described in the following list items.


        | **returned**: success
        | **type**: dict

        **sample**: ::

                  {"allow-management-interfaces": true, "allow-remote-access": true, "authentication-type": "local", "class": "user", "default-group-uri": null, "description": "", "disable-delay": 1, "disabled": false, "disruptive-pw-required": true, "disruptive-text-required": false, "email-address": null, "force-password-change": false, "force-shared-secret-key-change": null, "idle-timeout": 0, "inactivity-timeout": 0, "is-locked": false, "ldap-server-definition-uri": null, "max-failed-logins": 3, "max-web-services-api-sessions": 1000, "min-pw-change-time": 0, "multi-factor-authentication-required": false, "name": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER", "object-id": "91773b88-0c99-11eb-b4d3-00106f237ab1", "object-uri": "/api/users/91773b88-0c99-11eb-b4d3-00106f237ab1", "parent": "/api/console", "password-expires": 87, "password-rule": {"case-sensitive": true, "character-rules": [{"alphabetic": "required", "custom-character-sets": [], "max-characters": 30, "min-characters": 15, "numeric": "required", "special": "required"}], "class": "password-rule", "consecutive-characters": 1, "description": "ZaaS password rule definition", "element-id": "518ac1d8-bf98-11e9-b9dd-00106f237ab1", "element-uri": "/api/console/password-rules/518ac1d8-bf98-11e9-b9dd-00106f237ab1", "expiration": 90, "history-count": 10, "max-length": 30, "min-length": 15, "name": "ZaaS", "parent": "/api/console", "replication-overwrite-possible": true, "similarity-count": 0, "type": "user-defined"}, "password-rule-name": "ZaaS", "password-rule-uri": "/api/console/password-rules/518ac1d8-bf98-11e9-b9dd-00106f237ab1", "replication-overwrite-possible": true, "session-timeout": 0, "type": "standard", "user-role-names": ["hmc-system-programmer-tasks"], "user-role-objects": [{"associated-system-defined-user-role-uri": null, "class": "user-role", "description": "Tasks used by system programmers to configure and manage the system", "is-inheritance-enabled": false, "is-locked": false, "name": "hmc-system-programmer-tasks", "object-id": "19e90e27-1cae-422c-91ba-f76ac7fb8b82", "object-uri": "/api/user-roles/19e90e27-1cae-422c-91ba-f76ac7fb8b82", "parent": "/api/console", "permissions": [{"permitted-object": "/api/console/tasks/900e4676-fd59-4e4d-8bf2-03ef73c3a3df", "permitted-object-type": "object"}], "replication-overwrite-possible": true, "type": "system-defined"}], "user-roles": ["/api/user-roles/19e90e27-1cae-422c-91ba-f76ac7fb8b82"], "userid-on-ldap-server": null, "verify-timeout": 15, "web-services-api-session-idle-timeout": 360}


    name
          User name


          | **type**: str



    {property}
          Additional properties of the user, as described in the data model of the 'User' object in the :term:`HMC API` book. The property names have hyphens (-) as described in that book.


          | **type**: 



    user-pattern-name
          Only for users with ``type=pattern``: Name of the user pattern referenced by property ``user-pattern-uri``.


          | **type**: str



    user-pattern
          Only for users with ``type=pattern`` and if ``expand=true``: User pattern referenced by property ``user-pattern-uri``.


          | **type**: dict


     {property}
            Properties of the user pattern, as described in the data model of the 'User Pattern' object in the :term:`HMC API` book. The property names have hyphens (-) as described in that book.


            | **type**: 





    password-rule-name
          Only for users with ``authentication-type=local``: Name of the password rule referenced by property ``password-rule-uri``.


          | **type**: str



    password-rule
          Only for users with ``authentication-type=local`` and if ``expand=true``: Password rule referenced by property ``password-rule-uri``.


          | **type**: dict


     {property}
            Properties of the password rule, as described in the data model of the 'Password Rule' object in the :term:`HMC API` book. The property names have hyphens (-) as described in that book.


            | **type**: 





    ldap-server-definition-name
          Only for users with ``authentication-type=ldap``: Name of the LDAP server definition referenced by property ``ldap-server-definition-uri``.


          | **type**: str



    ldap-server-definition
          Only for users with ``authentication-type=ldap`` and if ``expand=true``: LDAP server definition referenced by property ``ldap-server-definition-uri``.


          | **type**: dict


     {property}
            Properties of the LDAP server definition, as described in the data model of the 'LDAP Server Definition' object in the :term:`HMC API` book. The property names have hyphens (-) as described in that book.


            | **type**: 







