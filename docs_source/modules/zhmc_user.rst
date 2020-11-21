
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


     
faked_session
  A ``zhmcclient_mock.FakedSession`` object that has a mocked HMC set up. If not null, this session will be used instead of connecting to the HMC specified in ``hmc_host``. This is used for testing purposes only.


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


   user
        For ``state=absent``, an empty dictionary.

        For ``state=present|facts``, a dictionary with the resource properties of the target user, plus additional artificial properties as described in the following list items.


        | **returned**: success
        | **type**: dict


    name
          User name


          | **type**: str



    {property}
          Additional properties of the user, as described in the :term:`HMC API` (using hyphens (-) in the property names).


          | **type**: 



    user-pattern-name
          Name of the user pattern referenced by property ``user-pattern-uri``.


          | **type**: str



    password-rule-name
          Name of the password rule referenced by property ``password-rule-uri``.


          | **type**: str



    ldap-server-definition-name
          Name of the LDAP server definition referenced by property ``ldap-server-definition-uri``.


          | **type**: str



    default-group-name
          Name of the group referenced by property ``default-group-uri``.


          | **type**: str





