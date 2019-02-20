.. _zhmc_storage_group:


zhmc_storage_group - Manages DPM storage groups (with "dpm-storage-management" feature)
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



.. contents::
   :local:
   :depth: 2


Synopsis
--------

* Gathers facts about a storage group associated with a CPC, including its storage volumes and virtual storage resources.
* Creates, deletes and updates a storage group associated with a CPC.


Requirements (on host that executes module)
-------------------------------------------

  * Network access to HMC
  * zhmcclient >=0.20.0
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
    <td>cpc_name<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td></td>
    <td>
        <div>The name of the CPC associated with the target storage group.</div>
    </td>
    </tr>

    <tr>
    <td>expand<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td><ul><li>yes</li><li>no</li></ul></td>
    <td>
        <div>Boolean that controls whether the returned storage group contains additional artificial properties that expand certain URI or name properties to the full set of resource properties (see description of return values of this module).</div>
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
        <div>The name of the target storage group.</div>
    </td>
    </tr>

    <tr>
    <td>properties<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>No properties.</td>
    <td></td>
    <td>
        <div>Dictionary with desired properties for the storage group. Used for <code>state=present</code>; ignored for <code>state=absent|facts</code>. Dictionary key is the property name with underscores instead of hyphens, and dictionary value is the property value in YAML syntax. Integer properties may also be provided as decimal strings.</div>
        <div>The possible input properties in this dictionary are the properties defined as writeable in the data model for Storage Group resources (where the property names contain underscores instead of hyphens), with the following exceptions:</div>
        <div>* <code>name</code>: Cannot be specified because the name has already been specified in the <code>name</code> module parameter.</div>
        <div>* <code>type</code>: Cannot be changed once the storage group exists.</div>
        <div>Properties omitted in this dictionary will remain unchanged when the storage group already exists, and will get the default value defined in the data model for storage groups in the HMC API book when the storage group is being created.</div>
    </td>
    </tr>

    <tr>
    <td>state<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td><ul><li>absent</li><li>present</li><li>facts</li></ul></td>
    <td>
        <div>The desired state for the target storage group:</div>
        <div>* <code>absent</code>: Ensures that the storage group does not exist. If the storage group is currently attached to any partitions, the module will fail.</div>
        <div>* <code>present</code>: Ensures that the storage group exists and is associated with the specified CPC, and has the specified properties. The attachment state of the storage group to a partition is not changed.</div>
        <div>* <code>facts</code>: Does not change anything on the storage group and returns the storage group properties.</div>
    </td>
    </tr>

    </table>
    </br>



Examples
--------

 ::

    
    ---
    # Note: The following examples assume that some variables named 'my_*' are set.

    - name: Gather facts about a storage group
      zhmc_storage_group:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_storage_group_name }}"
        state: facts
        expand: true
      register: sg1

    - name: Ensure the storage group does not exist
      zhmc_storage_group:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_storage_group_name }}"
        state: absent

    - name: Ensure the storage group exists
      zhmc_storage_group:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_storage_group_name }}"
        state: present
        expand: true
        properties:
          description: "Example storage group 1"
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
    <td>storage_group</td>
    <td>
        <div>For <code>state=absent</code>, an empty dictionary.</div>
        <div>For <code>state=present|facts</code>, a dictionary with the resource properties of the target storage group, plus additional artificial properties as described in the following list items. The dictionary keys are the exact property names as described in the data model for the resource, i.e. they contain hyphens (-), not underscores (_). The dictionary values are the property values using the Python representations described in the documentation of the zhmcclient Python package. The additional artificial properties are:</div>
        <div>* <code>attached-partition-names</code>: List of partition names to which the storage group is attached.</div>
        <div>* <code>cpc-name</code>: Name of the CPC that is associated to this storage group.</div>
        <div>* <code>candidate-adapter-ports</code> (only if expand was requested): List of candidate adapter ports of the storage group. Each port is represented as a dictionary of its properties; in addition each port has an artificial property <code>parent-adapter</code> which represents the adapter of the port. Each adapter is represented as a dictionary of its properties.</div>
        <div>* <code>storage-volumes</code> (only if expand was requested): List of storage volumes of the storage group. Each storage volume is represented as a dictionary of its properties.</div>
        <div>* <code>virtual-storage-resources</code> (only if expand was requested): List of virtual storage resources of the storage group. Each virtual storage resource is represented as a dictionary of its properties.</div>
        <div>* <code>attached-partitions</code> (only if expand was requested): List of partitions to which the storage group is attached. Each partition is represented as a dictionary of its properties.</div>
        <div>* <code>cpc</code> (only if expand was requested): The CPC that is associated to this storage group. The CPC is represented as a dictionary of its properties.</div>
    </td>
    <td align=center>success</td>
    <td align=center>dict</td>
    <td align=center><code>{
      "name": "sg-1",
      "description": "storage group #1",
      ...
    }</code>
    </td>
    </tr>

    </table>
    </br>
    </br>

Notes
-----

.. note::
    - The CPC that is associated with the target storage group must be in the Dynamic Partition Manager (DPM) operational mode and must have the "dpm-storage-management" firmware feature enabled. That feature has been introduced with the z14-ZR1 / Rockhopper II machine generation.
    - This module performs actions only against the Z HMC regarding the definition of storage group objects and their attachment to partitions. This module does not perform any actions against storage subsystems or SAN switches.
    - Attachment of a storage group to and from partitions is managed by the Ansible module zhmc_storage_group_attachment.
    - The Ansible module zhmc_hba is no longer used on CPCs that have the "dpm-storage-management" feature enabled.



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


