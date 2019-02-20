.. _zhmc_partition:


zhmc_partition - Manages partitions
+++++++++++++++++++++++++++++++++++



.. contents::
   :local:
   :depth: 2


Synopsis
--------

* Gathers facts about a partition, including its child resources (HBAs, NICs and virtual functions).
* Creates, updates, deletes, starts, and stops partitions in a CPC. The child resources of the partition are are managed by separate Ansible modules.
* The targeted CPC must be in the Dynamic Partition Manager (DPM) operational mode.


Requirements (on host that executes module)
-------------------------------------------

  * Network access to HMC
  * zhmcclient >=0.14.0
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
        <div>The name of the CPC with the target partition.</div>
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
        <div>The name of the target partition.</div>
    </td>
    </tr>

    <tr>
    <td>properties<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>No input properties</td>
    <td></td>
    <td>
        <div>Dictionary with input properties for the partition, for <code>state=stopped</code> and <code>state=active</code>. Key is the property name with underscores instead of hyphens, and value is the property value in YAML syntax. Integer properties may also be provided as decimal strings. Will be ignored for <code>state=absent</code>.</div>
        <div>The possible input properties in this dictionary are the properties defined as writeable in the data model for Partition resources (where the property names contain underscores instead of hyphens), with the following exceptions:</div>
        <div>* <code>name</code>: Cannot be specified because the name has already been specified in the <code>name</code> module parameter.</div>
        <div>* <code>type</code>: Cannot be changed once the partition exists, because updating it is not supported.</div>
        <div>* <code>boot_storage_device</code>: Cannot be specified because this information is specified using the artificial property <code>boot_storage_hba_name</code>.</div>
        <div>* <code>boot_network_device</code>: Cannot be specified because this information is specified using the artificial property <code>boot_network_nic_name</code>.</div>
        <div>* <code>boot_storage_hba_name</code>: The name of the HBA whose URI is used to construct <code>boot_storage_device</code>. Specifying it requires that the partition exists.</div>
        <div>* <code>boot_network_nic_name</code>: The name of the NIC whose URI is used to construct <code>boot_network_device</code>. Specifying it requires that the partition exists.</div>
        <div>* <code>crypto_configuration</code>: The crypto configuration for the partition, in the format of the <code>crypto-configuration</code> property of the partition (see HMC API book for details), with the exception that adapters are specified with their names in field <code>crypto_adapter_names</code> instead of their URIs in field <code>crypto_adapter_uris</code>. If the <code>crypto_adapter_names</code> field is null, all crypto adapters of the CPC will be used.</div>
        <div>Properties omitted in this dictionary will remain unchanged when the partition already exists, and will get the default value defined in the data model for partitions in the HMC API book when the partition is being created.</div>
    </td>
    </tr>

    <tr>
    <td>state<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td><ul><li>absent</li><li>stopped</li><li>active</li><li>facts</li></ul></td>
    <td>
        <div>The desired state for the target partition:</div>
        <div><code>absent</code>: Ensures that the partition does not exist in the specified CPC.</div>
        <div><code>stopped</code>: Ensures that the partition exists in the specified CPC, has the specified properties, and is in the 'stopped' status.</div>
        <div><code>active</code>: Ensures that the partition exists in the specified CPC, has the specified properties, and is in the 'active' or 'degraded' status.</div>
        <div><code>facts</code>: Does not change anything on the partition and returns the partition properties and the properties of its child resources (HBAs, NICs, and virtual functions).</div>
    </td>
    </tr>

    </table>
    </br>



Examples
--------

 ::

    
    ---
    # Note: The following examples assume that some variables named 'my_*' are set.

    # Because configuring LUN masking in the SAN requires the host WWPN, and the
    # host WWPN is automatically assigned and will be known only after an HBA has
    # been added to the partition, the partition needs to be created in stopped
    # state. Also, because the HBA has not yet been created, the boot
    # configuration cannot be done yet:
    - name: Ensure the partition exists and is stopped
      zhmc_partition:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_partition_name }}"
        state: stopped
        properties:
          description: "zhmc Ansible modules: Example partition 1"
          ifl_processors: 2
          initial_memory: 1024
          maximum_memory: 1024
      register: part1

    # After an HBA has been added (see Ansible module zhmc_hba), and LUN masking
    # has been configured in the SAN, and a bootable image is available at the
    # configured LUN and target WWPN, the partition can be configured for boot
    # from the FCP LUN and can be started:
    - name: Configure boot device and start the partition
      zhmc_partition:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_partition_name }}"
        state: active
        properties:
          boot_device: storage-adapter
          boot_storage_device_hba_name: hba1
          boot_logical_unit_number: 00000000001
          boot_world_wide_port_name: abcdefabcdef
      register: part1

    - name: Ensure the partition does not exist
      zhmc_partition:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_partition_name }}"
        state: absent

    - name: Define crypto configuration
      zhmc_partition:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_partition_name }}"
        state: active
        properties:
          crypto_configuration:
            crypto_adapter_names:
              - adapter1
              - adapter2
            crypto_domain_configurations:
              - domain_index: 0
                access_mode: control-usage
              - domain_index: 1
                access_mode: control
      register: part1

    - name: Gather facts about a partition
      zhmc_partition:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_partition_name }}"
        state: facts
      register: part1



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
    <td>partition</td>
    <td>
        <div>For <code>state=absent</code>, an empty dictionary.</div>
        <div>For <code>state=stopped</code> and <code>state=active</code>, a dictionary with the resource properties of the partition (after changes, if any). The dictionary keys are the exact property names as described in the data model for the resource, i.e. they contain hyphens (-), not underscores (_). The dictionary values are the property values using the Python representations described in the documentation of the zhmcclient Python package.</div>
        <div>For <code>state=facts</code>, a dictionary with the resource properties of the partition, including its child resources (HBAs, NICs, and virtual functions). The dictionary keys are the exact property names as described in the data model for the resource, i.e. they contain hyphens (-), not underscores (_). The dictionary values are the property values using the Python representations described in the documentation of the zhmcclient Python package. The properties of the child resources are represented in partition properties named 'hbas', 'nics', and 'virtual-functions', respectively.</div>
    </td>
    <td align=center>success</td>
    <td align=center>dict</td>
    <td align=center><code>{
      "name": "part-1",
      "description": "partition #1",
      "status": "active",
      "boot-device": "storage-adapter",
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
    - See also Ansible modules zhmc_hba, zhmc_nic, zhmc_virtual_function.



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


