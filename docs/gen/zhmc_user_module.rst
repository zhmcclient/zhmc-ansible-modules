.. _zhmc_user:


zhmc_user - Manages users defined on the HMC
++++++++++++++++++++++++++++++++++++++++++++



.. contents::
   :local:
   :depth: 2


Synopsis
--------

* Gathers facts about a user on the HMC.
* Creates, deletes and updates a user on the HMC.


Requirements (on host that executes module)
-------------------------------------------

  * Network access to HMC
  * zhmcclient >=0.23.0
  * ansible >=2.2.0.0


Options
-------

.. raw:: html

    <table border=1 cellpadding=4>

    <tr>
    <th class="head">parameter</th>
    <th class="head">required</th>
    <th class="head">default</th>
    <th class="head">choices</th>
    <th class="head">comments</th>
    </tr>

    <tr>
    <td>expand<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td><ul><li>yes</li><li>no</li></ul></td>
    <td>
        <div>Boolean that controls whether the returned user contains additional artificial properties that expand certain URI or name properties to the full set of resource properties (see description of return values of this module).</div>
    </td>
    </tr>

    <tr>
    <td>faked_session<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>Real HMC will be used.</td>
    <td></td>
    <td>
        <div>A <code>zhmcclient_mock.FakedSession</code> object that has a mocked HMC set up. If provided, it will be used instead of connecting to a real HMC. This is used for testing purposes only.</div>
    </td>
    </tr>

    <tr>
    <td rowspan="2">hmc_auth<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td></td>
    <td>
        <div>The authentication credentials for the HMC.</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object hmc_auth</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>password<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>The password for authenticating with the HMC.</div>
        </td>
        </tr>

        <tr>
        <td>userid<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>The userid (username) for authenticating with the HMC.</div>
        </td>
        </tr>

        </table>

    </td>
    </tr>
    </td>
    </tr>

    <tr>
    <td>hmc_host<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td></td>
    <td>
        <div>The hostname or IP address of the HMC.</div>
    </td>
    </tr>

    <tr>
    <td>log_file<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.</div>
    </td>
    </tr>

    <tr>
    <td>name<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td></td>
    <td>
        <div>The userid of the target user (i.e. the 'name' property of the User object).</div>
    </td>
    </tr>

    <tr>
    <td>properties<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>No properties.</td>
    <td></td>
    <td>
        <div>Dictionary with desired properties for the user. Used for <code>state=present</code>; ignored for <code>state=absent|facts</code>. Dictionary key is the property name with underscores instead of hyphens, and dictionary value is the property value in YAML syntax. Integer properties may also be provided as decimal strings.</div>
        <div>The possible input properties in this dictionary are the properties defined as writeable in the data model for User resources (where the property names contain underscores instead of hyphens), with the following exceptions:</div>
        <div>* <code>name</code>: Cannot be specified because the name has already been specified in the <code>name</code> module parameter.</div>
        <div>* <code>type</code>: Cannot be changed once the user exists.</div>
        <div>Properties omitted in this dictionary will remain unchanged when the user already exists, and will get the default value defined in the data model for users in the HMC API book when the user is being created.</div>
    </td>
    </tr>

    <tr>
    <td>state<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td><ul><li>absent</li><li>present</li><li>facts</li></ul></td>
    <td>
        <div>The desired state for the target user:</div>
        <div>* <code>absent</code>: Ensures that the user does not exist.</div>
        <div>* <code>present</code>: Ensures that the user exists and has the specified properties.</div>
        <div>* <code>facts</code>: Does not change anything on the user and returns the user properties.</div>
    </td>
    </tr>

    </table>
    </br>



Examples
--------

 ::

    
    ---
    # Note: The following examples assume that some variables named 'my_*' are set.

    - name: Gather facts about a user
      zhmc_user:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        name: "{{ my_user_name }}"
        state: facts
        expand: true
      register: sg1

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
          type: fcp
          shared: false
          connectivity: 4
          max-partitions: 1
      register: sg1



Return Values
-------------

Common return values are documented here :doc:`common_return_values`, the following are the fields unique to this module:

.. raw:: html

    <table border=1 cellpadding=4>

    <tr>
    <th class="head">name</th>
    <th class="head">description</th>
    <th class="head">returned</th>
    <th class="head">type</th>
    <th class="head">sample</th>
    </tr>

    <tr>
    <td>user</td>
    <td>
        <div>For <code>state=absent</code>, an empty dictionary.</div>
        <div>For <code>state=present|facts</code>, a dictionary with the resource properties of the target user, plus additional artificial properties as described in the following list items. The dictionary keys are the exact property names as described in the data model for the resource, i.e. they contain hyphens (-), not underscores (_). The dictionary values are the property values using the Python representations described in the documentation of the zhmcclient Python package. The additional artificial properties are:</div>
        <div>* <code>attached-partition-names</code>: List of partition names to which the user is attached.</div>
        <div>* <code>cpc-name</code>: Name of the CPC that is associated to this storage group.</div>
        <div>* <code>candidate-adapter-ports</code> (only if expand was requested): List of candidate adapter ports of the user. Each port is represented as a dictionary of its properties; in addition each port has an artificial property <code>parent-adapter</code> which represents the adapter of the port. Each adapter is represented as a dictionary of its properties.</div>
        <div>* <code>storage-volumes</code> (only if expand was requested): List of storage volumes of the user. Each storage volume is represented as a dictionary of its properties.</div>
        <div>* <code>virtual-storage-resources</code> (only if expand was requested): List of virtual storage resources of the user. Each virtual storage resource is represented as a dictionary of its properties.</div>
        <div>* <code>attached-partitions</code> (only if expand was requested): List of partitions to which the user is attached. Each partition is represented as a dictionary of its properties.</div>
        <div>* <code>cpc</code> (only if expand was requested): The CPC that is associated to this user. The CPC is represented as a dictionary of its properties.</div>
    </td>
    <td align=center>success</td>
    <td align=center>dict</td>
    <td align=center><code>{
      "name": "sg-1",
      "description": "user #1",
      ...
    }</code>
    </td>
    </tr>

    </table>
    </br>
    </br>




Status
~~~~~~

This module is flagged as **preview** which means that it is not guaranteed to have a backwards compatible interface.

Support
~~~~~~~

This module is community maintained without core committer oversight.

For more information on what this means please read `Module Support`_.

For help in developing on modules, should you be so inclined, please read the contribution guidelines in the module's `source repository`_, `Testing Ansible`_ and `Developing Modules`_.

.. _`Module Support`: http://docs.ansible.com/ansible/latest/modules_support.html

.. _`Testing Ansible`: http://docs.ansible.com/ansible/latest/dev_guide/testing.html

.. _`Developing Modules`: http://docs.ansible.com/ansible/latest/dev_guide/developing_modules.html


Shipment
~~~~~~~~

This module is a third-party module and is not shipped with Ansible. See the module's `source repository`_ for details.

.. _`source repository`: https://github.com/zhmcclient/zhmc-ansible-modules


