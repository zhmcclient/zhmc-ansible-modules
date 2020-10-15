.. _zhmc_user_module:


zhmc_user -- Manages users defined on the HMC of Z systems.
===========================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Gather facts about a user on an HMC of a Z system.

Create, delete, or update a user on an HMC.



Requirements
------------
The below requirements are needed on the host that executes this module.

- Access to the WS API of the HMC of the targeted Z system. The targeted Z system can be in any operational mode (classic, DPM)
- Python package zhmcclient >=0.23.0



Parameters
----------

  hmc_host (True, str, None)
    The hostname or IP address of the HMC.


  hmc_auth (True, dict, None)
    The authentication credentials for the HMC, as a dictionary of ``userid``, ``password``.


    userid (True, str, None)
      The userid (username) for authenticating with the HMC.


    password (True, str, None)
      The password for authenticating with the HMC.



  name (True, str, None)
    The userid of the target user (i.e. the 'name' property of the User object).


  state (True, str, None)
    The desired state for the target user:

    * ``absent``: Ensures that the user does not exist.

    * ``present``: Ensures that the user exists and has the specified properties.

    * ``facts``: Does not change anything on the user and returns the user properties.


  properties (False, dict, None)
    Dictionary with desired properties for the user. Used for ``state=present``; ignored for ``state=absent|facts``. Dictionary key is the property name with underscores instead of hyphens, and dictionary value is the property value in YAML syntax. Integer properties may also be provided as decimal strings.

    The possible input properties in this dictionary are the properties defined as writeable in the data model for User resources (where the property names contain underscores instead of hyphens), with the following exceptions:

    * ``name``: Cannot be specified because the name has already been specified in the ``name`` module parameter.

    * ``type``: Cannot be changed once the user exists.

    * ``user-pattern-uri``: Cannot be set directly, but indirectly via the artificial property ``user-pattern-name``.

    * ``password-rule-uri``: Cannot be set directly, but indirectly via the artificial property ``password-rule-name``.

    * ``ldap-server-definition-uri``: Cannot be set directly, but indirectly via the artificial property ``ldap-server-definition-name``.

    * ``default-group-uri``: Cannot be set directly, but indirectly via the artificial property ``default-group-name``.

    Properties omitted in this dictionary will remain unchanged when the user already exists, and will get the default value defined in the data model for users in the HMC API book when the user is being created.


  expand (False, bool, False)
    Boolean that controls whether the returned user contains additional artificial properties that expand certain URI or name properties to the full set of resource properties (see description of return values of this module).


  log_file (False, str, None)
    File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.


  faked_session (False, raw, None)
    A ``zhmcclient_mock.FakedSession`` object that has a mocked HMC set up. If not null, this session will be used instead of connecting to the HMC specified in ``hmc_host``. This is used for testing purposes only.









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

user (success, dict, C({
  "name": "user-1",
  "description": "user #1",
  ...
})
)
  For ``state=absent``, an empty dictionary.

  For ``state=present|facts``, a dictionary with the resource properties of the target user, plus additional artificial properties as described in the following list items. The dictionary keys are the exact property names as described in the data model for the resource, i.e. they contain hyphens (-), not underscores (_). The dictionary values are the property values using the Python representations described in the documentation of the zhmcclient Python package. The additional artificial properties are:

  * ``user-pattern-name``: Name of the user pattern referenced by property ``user-pattern-uri``.

  * ``password-rule-name``: Name of the password rule referenced by property ``password-rule-uri``.

  * ``ldap-server-definition-name``: Name of the LDAP server definition referenced by property ``ldap-server-definition-uri``.

  * ``default-group-name``: Name of the group referenced by property ``default-group-uri``.





Status
------




- This module is guaranteed to have backward compatible interface changes going forward. *[stableinterface]*


- This module is maintained by community.



Authors
~~~~~~~

- Andreas Maier (@andy-maier)

