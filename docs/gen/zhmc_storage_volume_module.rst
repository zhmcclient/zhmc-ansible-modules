.. _zhmc_storage_volume:


zhmc_storage_volume - Manages DPM storage volumes in existing storage groups (with "dpm-storage-management" feature)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



.. contents::
   :local:
   :depth: 2


Synopsis
--------

* Gathers facts about a storage volume in a storage group associated with a CPC.
* Creates, deletes and updates a storage volume in a storage group associated with a CPC.


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
        <div>The name of the CPC associated with the storage group containing the target storage volume.</div>
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
        <div>The name of the target storage volume.</div>
    </td>
    </tr>

    <tr>
    <td>properties<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>No properties.</td>
    <td></td>
    <td>
        <div>Dictionary with desired properties for the storage volume. Used for <code>state=present</code>; ignored for <code>state=absent|facts</code>. Dictionary key is the property name with underscores instead of hyphens, and dictionary value is the property value in YAML syntax. Integer properties may also be provided as decimal strings.</div>
        <div>The possible input properties in this dictionary are the properties defined as writeable in the data model for Storage Volume resources (where the property names contain underscores instead of hyphens), with the following exceptions:</div>
        <div>* <code>name</code>: Cannot be specified because the name has already been specified in the <code>name</code> module parameter.</div>
        <div>Properties omitted in this dictionary will remain unchanged when the storage volume already exists, and will get the default value defined in the data model for storage volumes in the HMC API book when the storage volume is being created.</div>
    </td>
    </tr>

    <tr>
    <td>state<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td><ul><li>absent</li><li>present</li><li>facts</li></ul></td>
    <td>
        <div>The desired state for the target storage volume:</div>
        <div>* <code>absent</code>: Ensures that the storage volume does not exist in the specified storage group.</div>
        <div>* <code>present</code>: Ensures that the storage volume exists in the specified storage group, and has the specified properties.</div>
        <div>* <code>facts</code>: Does not change anything on the storage volume and returns the storage volume properties.</div>
    </td>
    </tr>

    <tr>
    <td>storage_group_name<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td></td>
    <td>
        <div>The name of the storage group containing the target storage volume.</div>
    </td>
    </tr>

    </table>
    </br>



Examples
--------

 ::

    
    ---
    # Note: The following examples assume that some variables named 'my_*' are set.

    - name: Gather facts about a storage volume
      zhmc_storage_volume:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        storage_group_name: "{{ my_storage_group_name }}"
        name: "{{ my_storage_volume_name }}"
        state: facts
      register: sv1

    - name: Ensure the storage volume does not exist
      zhmc_storage_volume:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        storage_group_name: "{{ my_storage_group_name }}"
        name: "{{ my_storage_volume_name }}"
        state: absent

    - name: Ensure the storage volume exists
      zhmc_storage_volume:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        storage_group_name: "{{ my_storage_group_name }}"
        name: "{{ my_storage_volume_name }}"
        state: present
        properties:
          description: "Example storage volume 1"
          size: 1
      register: sv1



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
    <td>storage_volume</td>
    <td>
        <div>For <code>state=absent</code>, an empty dictionary.</div>
        <div>For <code>state=present|facts</code>, a dictionary with the resource properties of the storage volume, indicating the state after changes from this module (if any) have been applied. The dictionary keys are the exact property names as described in the data model for the resource, i.e. they contain hyphens (-), not underscores (_). The dictionary values are the property values using the Python representations described in the documentation of the zhmcclient Python package. The additional artificial properties are:</div>
        <div>* <code>type</code>: Type of the storage volume ('fc' or 'fcp'), as defined in its storage group.</div>
    </td>
    <td align=center>success</td>
    <td align=center>dict</td>
    <td align=center><code>{
      "name": "sv-1",
      "description": "storage volume #1",
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
    - The CPC that is associated with the storage group must be in the Dynamic Partition Manager (DPM) operational mode and must have the "dpm-storage-management" firmware feature enabled. That feature has been introduced with the z14-ZR1 / Rockhopper II machine generation.
    - This module performs actions only against the Z HMC regarding the definition of storage volume objects within storage group objects. This module does not perform any actions against storage subsystems or SAN switches.
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


