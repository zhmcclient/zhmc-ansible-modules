.. _zhmc_virtual_function:


zhmc_virtual_function - Manages virtual functions in existing partitions
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



.. contents::
   :local:
   :depth: 2


Synopsis
--------

* Creates, updates, and deletes virtual functions in existing partitions of a CPC.
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
        <div>The name of the CPC with the partition containing the virtual function.</div>
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
        <div>The name of the target virtual function that is managed. If the virtual function needs to be created, this value becomes its name.</div>
    </td>
    </tr>

    <tr>
    <td>partition_name<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td></td>
    <td>
        <div>The name of the partition containing the virtual function.</div>
    </td>
    </tr>

    <tr>
    <td>properties<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>No input properties</td>
    <td></td>
    <td>
        <div>Dictionary with input properties for the virtual function, for <code>state=present</code>. Key is the property name with underscores instead of hyphens, and value is the property value in YAML syntax. Integer properties may also be provided as decimal strings. Will be ignored for <code>state=absent</code>.</div>
        <div>The possible input properties in this dictionary are the properties defined as writeable in the data model for Virtual Function resources (where the property names contain underscores instead of hyphens), with the following exceptions:</div>
        <div>* <code>name</code>: Cannot be specified because the name has already been specified in the <code>name</code> module parameter.</div>
        <div>* <code>adapter_uri</code>: Cannot be specified because this information is specified using the artificial property <code>adapter_name</code>.</div>
        <div>* <code>adapter_name</code>: The name of the adapter that backs the target virtual function.</div>
        <div>Properties omitted in this dictionary will remain unchanged when the virtual function already exists, and will get the default value defined in the data model for virtual functions when the virtual function is being created.</div>
    </td>
    </tr>

    <tr>
    <td>state<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td><ul><li>absent</li><li>present</li></ul></td>
    <td>
        <div>The desired state for the target virtual function:</div>
        <div><code>absent</code>: Ensures that the virtual function does not exist in the specified partition.</div>
        <div><code>present</code>: Ensures that the virtual function exists in the specified partition and has the specified properties.</div>
    </td>
    </tr>

    </table>
    </br>



Examples
--------

 ::

    
    ---
    # Note: The following examples assume that some variables named 'my_*' are set.

    - name: Ensure virtual function exists in the partition
      zhmc_partition:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        partition_name: "{{ my_partition_name }}"
        name: "{{ my_vfunction_name }}"
        state: present
        properties:
          adapter_name: "ABC-123"
          description: "The accelerator adapter"
          device_number: "033F"
      register: vfunction1

    - name: Ensure virtual function does not exist in the partition
      zhmc_partition:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        partition_name: "{{ my_partition_name }}"
        name: "{{ my_vfunction_name }}"
        state: absent


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
    <td>virtual_function</td>
    <td>
        <div>For <code>state=absent</code>, an empty dictionary.</div>
        <div>For <code>state=present</code>, a dictionary with the resource properties of the virtual function (after changes, if any). The dictionary keys are the exact property names as described in the data model for the resource, i.e. they contain hyphens (-), not underscores (_). The dictionary values are the property values using the Python representations described in the documentation of the zhmcclient Python package.</div>
    </td>
    <td align=center>success</td>
    <td align=center>dict</td>
    <td align=center><code>{
      "name": "vfunction-1",
      "description": "virtual function #1",
      "adapter-uri': "/api/adapters/...",
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
    - See also Ansible module zhmc_partition.



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


