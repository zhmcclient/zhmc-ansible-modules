.. _zhmc_adapter:


zhmc_adapter - Manages an adapter in a CPC.
+++++++++++++++++++++++++++++++++++++++++++



.. contents::
   :local:
   :depth: 2


Synopsis
--------

* Gathers facts about the adapter including its ports.
* Updates the properties of an adapter.


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
    <td>match<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>No match properties</td>
    <td></td>
    <td>
        <div>Only for <code>state=set</code>: Match properties for identifying the target adapter in the set of adapters in the CPC, if an adapter with the name specified in the <code>name</code> module parameter does not exist in that set. This parameter will be ignored otherwise.</div>
        <div>Use of this parameter allows renaming an adapter: The <code>name</code> module parameter specifies the new name of the target adapter, and the <code>match</code> module parameter identifies the adapter to be renamed. This can be combined with other property updates by using the <code>properties</code> module parameter.</div>
        <div>The parameter is a dictionary. The key of each dictionary item is the property name as specified in the data model for adapter resources, with underscores instead of hyphens. The value of each dictionary item is the match value for the property (in YAML syntax). Integer properties may also be provided as decimal strings.</div>
        <div>The specified match properties follow the rules of filtering for the zhmcclient library as described in https://python-zhmcclient.readthedocs.io/en/stable/concepts.html#filtering</div>
        <div>The possible match properties are all properties in the data model for adapter resources, including <code>name</code>.</div>
    </td>
    </tr>

    <tr>
    <td>name<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td></td>
    <td>
        <div>The name of the target adapter. In case of renaming an adapter, this is the new name of the adapter.</div>
    </td>
    </tr>

    <tr>
    <td>properties<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>No property changes (other than possibly C(name)).</td>
    <td></td>
    <td>
        <div>Only for <code>state=set|present</code>: New values for the properties of the adapter. Properties omitted in this dictionary will remain unchanged. This parameter will be ignored for other states.</div>
        <div>The parameter is a dictionary. The key of each dictionary item is the property name as specified in the data model for adapter resources, with underscores instead of hyphens. The value of each dictionary item is the property value (in YAML syntax). Integer properties may also be provided as decimal strings.</div>
        <div>The possible properties in this dictionary are the properties defined as writeable in the data model for adapter resources, with the following exceptions:</div>
        <div>* <code>name</code>: Cannot be specified as a property because the name has already been specified in the <code>name</code> module parameter.</div>
        <div>* <code>type</code>: The desired adapter type can be specified in order to support adapters that can change their type (e.g. the FICON Express adapter can change its type between 'not-configured', 'fcp' and 'fc').</div>
        <div>* <code>crypto_type</code>: The crypto type can be specified in order to support the ability of the Crypto Express adapters to change their crypto type. Valid values are 'ep11', 'cca' and 'acc'. Changing to 'acc' will zeroize the crypto adapter.</div>
    </td>
    </tr>

    <tr>
    <td>state<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td><ul><li>set</li><li>present</li><li>absent</li><li>facts</li></ul></td>
    <td>
        <div>The desired state for the attachment:</div>
        <div>* <code>set</code>: Ensures that an existing adapter has the specified properties.</div>
        <div>* <code>present</code>: Ensures that a Hipersockets adapter exists and has the specified properties.</div>
        <div>* <code>absent</code>: Ensures that a Hipersockets adapter does not exist.</div>
        <div>* <code>facts</code>: Does not change anything on the adapter and returns the adapter properties including its ports.</div>
    </td>
    </tr>

    </table>
    </br>



Examples
--------

 ::

    
    ---
    # Note: The following examples assume that some variables named 'my_*' are set.

    - name: Gather facts about an existing adapter
      zhmc_adapter:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_adapter_name }}"
        state: facts
      register: adapter1

    - name: Ensure an existing adapter has the desired property values
      zhmc_adapter:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_adapter_name }}"
        state: set
        properties:
          description: "This is adapter {{ my_adapter_name }}"
      register: adapter1

    - name: "Ensure the existing adapter identified by its name or adapter ID has
             the desired name and property values"
      zhmc_adapter:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_adapter_name }}"
        match:
          adapter_id: "12C"
        state: set
        properties:
          description: "This is adapter {{ my_adapter_name }}"
      register: adapter1

    - name: "Ensure a Hipersockets adapter exists and has the desired property
             values"
      zhmc_adapter:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_adapter_name }}"
        state: present
        properties:
          type: hipersockets
          description: "This is Hipersockets adapter {{ my_adapter_name }}"
      register: adapter1

    - name: "Ensure a Hipersockets adapter does not exist"
      zhmc_adapter:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        name: "{{ my_adapter_name }}"
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
    <td>cpc</td>
    <td>
        <div>For <code>state=absent</code>, an empty dictionary.</div>
        <div>For <code>state=set|present|facts</code>, a dictionary with the properties of the adapter. The properties contain these additional artificial properties for listing its child resources: - 'ports': The ports of the adapter, as a dict of key: port name, value: dict of a subset of the port properties (name, status, element_uri).</div>
    </td>
    <td align=center>success</td>
    <td align=center>dict</td>
    <td align=center><code>{
      "name": "adapter-1",
      "description": "Adapter 1",
      "status": "active",
      "acceptable_status": [ "active" ],
      ...
      "ports": [
        {
          "name": "Port 0",
          ...
        },
        ...
      ]
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


