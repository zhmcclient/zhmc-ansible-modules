
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zhmc_ldap_server_definition.py

.. _zhmc_ldap_server_definition_module:
.. _ibm.ibm_zhmc.zhmc_ldap_server_definition_module:


zhmc_ldap_server_definition -- Manage an LDAP Server Definition on the HMC
==========================================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gather facts about an LDAP Server Definition on an HMC of a Z system.
- Create, delete, or update an LDAP Server Definition on an HMC.


Requirements
------------

- The HMC userid must have these task permissions: 'Manage LDAP Server Definitions'.




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
  The name of the target LDAP Server Definition object.

  The name is case\-insensitive (but case\-preserving).

  | **required**: True
  | **type**: str


state
  The desired state for the LDAP Server Definition. All states are fully idempotent within the limits of the properties that can be changed:

  \* :literal:`absent`\ : Ensures that the LDAP Server Definition does not exist.

  \* :literal:`present`\ : Ensures that the LDAP Server Definition exists and has the specified properties.

  \* :literal:`facts`\ : Returns the LDAP Server Definition properties.

  | **required**: True
  | **type**: str
  | **choices**: absent, present, facts


properties
  Dictionary with desired properties for the LDAP Server Definition. Used for :literal:`state=present`\ ; ignored for :literal:`state=absent\|facts`. Dictionary key is the property name with underscores instead of hyphens, and dictionary value is the property value in YAML syntax. Integer properties may also be provided as decimal strings.

  The possible input properties in this dictionary are the properties defined as writeable in the data model for LDAP Server Definition resources (where the property names contain underscores instead of hyphens), with the following exceptions:

  \* :literal:`name`\ : Cannot be specified because the name has already been specified in the :literal:`name` module parameter.

  Properties omitted in this dictionary will remain unchanged when the LDAP Server Definition already exists, and will get the default value defined in the data model for LDAP Server Definitions in the :ref:`HMC API <HMC API>` book when the LDAP Server Definition is being created.

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

   - name: Gather facts about an LDAP Server Definition
     zhmc_ldap_server_definition:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_lsd_name }}"
       state: facts
     register: lsd1

   - name: Ensure the LDAP Server Definition does not exist
     zhmc_ldap_server_definition:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_lsd_name }}"
       state: absent

   - name: Ensure the LDAP Server Definition exists
     zhmc_ldap_server_definition:
       hmc_host: "{{ my_hmc_host }}"
       hmc_auth: "{{ my_hmc_auth }}"
       name: "{{ my_lsd_name }}"
       state: present
       properties:
         description: "Example LDAP Server Definition 1"
         primary_hostname_ipaddr: "10.11.12.13"
         search_distinguished_name: "test_user{0}"
     register: lsd1










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

ldap_server_definition
  For :literal:`state=absent`\ , an empty dictionary.

  For :literal:`state=present\|facts`\ , a dictionary with the resource properties of the target LDAP Server Definition.

  | **returned**: success
  | **type**: dict
  | **sample**:

    .. code-block:: json

        {
            "backup-hostname-ipaddr": null,
            "bind-distinguished-name": null,
            "class": "ldap-server-definition",
            "connection-port": null,
            "description": "zhmc test LSD 1",
            "element-id": "dcb6d966-465f-11ee-80ca-00106f234c71",
            "element-uri": "/api/console/ldap-server-definitions/dcb6d966-465f-11ee-80ca-00106f234c71",
            "location-method": "pattern",
            "name": "zhmc_test_lsd_1",
            "parent": "/api/console",
            "primary-hostname-ipaddr": "10.11.12.13",
            "replication-overwrite-possible": false,
            "search-distinguished-name": "test_user{0}",
            "search-filter": null,
            "search-scope": null,
            "tolerate-untrusted-certificates": null,
            "use-ssl": false
        }

  name
    LDAP Server Definition name

    | **type**: str

  {property}
    Additional properties of the LDAP Server Definition, as described in the data model of the 'LDAP Server Definition' object in the :ref:`HMC API <HMC API>` book. Write\-only properties in the data model are not included. The property names have hyphens (\-) as described in that book.

    | **type**: raw


