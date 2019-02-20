.. _zhmc_cpc:


zhmc_cpc - Manages a CPC.
+++++++++++++++++++++++++



.. contents::
   :local:
   :depth: 2


Synopsis
--------

* Gathers facts about the CPC including its child resources.
* Updates the properties of a CPC.


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
        <div>The name of the target CPC.</div>
    </td>
    </tr>

    <tr>
    <td>properties<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>No property changes.</td>
    <td></td>
    <td>
        <div>Only for <code>state=set</code>: New values for the properties of the CPC. Properties omitted in this dictionary will remain unchanged. This parameter will be ignored for <code>state=facts</code>.</div>
        <div>The parameter is a dictionary. The key of each dictionary item is the property name as specified in the data model for CPC resources, with underscores instead of hyphens. The value of each dictionary item is the property value (in YAML syntax). Integer properties may also be provided as decimal strings.</div>
        <div>The possible properties in this dictionary are the properties defined as writeable in the data model for CPC resources.</div>
    </td>
    </tr>

    <tr>
    <td>state<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td><ul><li>set</li><li>facts</li></ul></td>
    <td>
        <div>The desired state for the attachment:</div>
        <div>* <code>set</code>: Ensures that the CPC has the specified properties.</div>
        <div>* <code>facts</code>: Does not change anything on the CPC and returns the CPC properties including its child resources.</div>
    </td>
    </tr>

    </table>
    </br>



Examples
--------

 ::

    
    ---
    # Note: The following examples assume that some variables named 'my_*' are set.

    - name: Gather facts about the CPC
      zhmc_cpc:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        name: "{{ my_cpc_name }}"
        state: facts
      register: cpc1

    - name: Ensure the CPC has the desired property values
      zhmc_cpc:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        name: "{{ my_cpc_name }}"
        state: set
        properties:
          acceptable_status:
           - active
          description: "This is CPC {{ my_cpc_name }}"



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
    <td>cpc</td>
    <td>
        <div>For <code>state=set|facts</code>, a dictionary with the properties of the CPC. The properties contain these additional artificial properties for listing its child resources: - 'partitions': The defined partitions of the CPC, as a dict of key: partition name, value: dict of a subset of the partition properties (name, status, object_uri). - 'adapters': The adapters of the CPC, as a dict of key: adapter name, value: dict of a subset of the adapter properties (name, status, object_uri).</div>
    </td>
    <td align=center>success</td>
    <td align=center>dict</td>
    <td align=center><code>{
      "name": "CPCA",
      "description": "CPC A",
      "status": "active",
      "acceptable_status": [ "active" ],
      ...
      "partitions": [
        {
          "name": "part-1",
          ...
        },
        ...
      ],
      "adapters": [
        {
          "name": "adapter-1",
          ...
        },
        ...
      ],
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


