:source: zhmc_adapter.py

:orphan:

.. _zhmc_adapter_module:


zhmc_adapter -- Manages adapters of Z systems
+++++++++++++++++++++++++++++++++++++++++++++


.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gather facts about an adapter of a CPC (Z system), including its ports.
- Update the properties of an adapter.



Requirements
------------
The below requirements are needed on the host that executes this module.

- Access to the WS API of the HMC of the targeted Z system. The targeted Z system must be in the Dynamic Partition Manager (DPM) operational mode.
- Python package zhmcclient >=0.20.0


Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="2">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
                        <th width="100%">Comments</th>
        </tr>
                    <tr>
                                                                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-cpc_name"></div>
                    <b>cpc_name</b>
                    <a class="ansibleOptionLink" href="#parameter-cpc_name" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                 / <span style="color: red">required</span>                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                            <div>The name of the target CPC.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-faked_session"></div>
                    <b>faked_session</b>
                    <a class="ansibleOptionLink" href="#parameter-faked_session" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">raw</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                                    <b>Default:</b><br/><div style="color: blue">null</div>
                                    </td>
                                                                <td>
                                            <div>A <code>zhmcclient_mock.FakedSession</code> object that has a mocked HMC set up. If not null, this session will be used instead of connecting to the HMC specified in <code>hmc_host</code>. This is used for testing purposes only.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-hmc_auth"></div>
                    <b>hmc_auth</b>
                    <a class="ansibleOptionLink" href="#parameter-hmc_auth" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">dictionary</span>
                                                 / <span style="color: red">required</span>                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                            <div>The authentication credentials for the HMC, as a dictionary of <code>userid</code>, <code>password</code>.</div>
                                                        </td>
            </tr>
                                                            <tr>
                                                    <td class="elbow-placeholder"></td>
                                                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-hmc_auth/password"></div>
                    <b>password</b>
                    <a class="ansibleOptionLink" href="#parameter-hmc_auth/password" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                 / <span style="color: red">required</span>                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                            <div>The password for authenticating with the HMC.</div>
                                                        </td>
            </tr>
                                <tr>
                                                    <td class="elbow-placeholder"></td>
                                                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-hmc_auth/userid"></div>
                    <b>userid</b>
                    <a class="ansibleOptionLink" href="#parameter-hmc_auth/userid" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                 / <span style="color: red">required</span>                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                            <div>The userid (username) for authenticating with the HMC.</div>
                                                        </td>
            </tr>
                    
                                                <tr>
                                                                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-hmc_host"></div>
                    <b>hmc_host</b>
                    <a class="ansibleOptionLink" href="#parameter-hmc_host" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                 / <span style="color: red">required</span>                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                            <div>The hostname or IP address of the HMC.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-log_file"></div>
                    <b>log_file</b>
                    <a class="ansibleOptionLink" href="#parameter-log_file" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                                    <b>Default:</b><br/><div style="color: blue">null</div>
                                    </td>
                                                                <td>
                                            <div>File path of a log file to which the logic flow of this module as well as interactions with the HMC are logged. If null, logging will be propagated to the Python root logger.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-match"></div>
                    <b>match</b>
                    <a class="ansibleOptionLink" href="#parameter-match" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">dictionary</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                                    <b>Default:</b><br/><div style="color: blue">null</div>
                                    </td>
                                                                <td>
                                            <div>Only for <code>state=set</code>: Match properties for identifying the target adapter in the set of adapters in the CPC, if an adapter with the name specified in the <code>name</code> module parameter does not exist in that set. This parameter will be ignored otherwise.</div>
                                            <div>Use of this parameter allows renaming an adapter: The <code>name</code> module parameter specifies the new name of the target adapter, and the <code>match</code> module parameter identifies the adapter to be renamed. This can be combined with other property updates by using the <code>properties</code> module parameter.</div>
                                            <div>The parameter is a dictionary. The key of each dictionary item is the property name as specified in the data model for adapter resources, with underscores instead of hyphens. The value of each dictionary item is the match value for the property (in YAML syntax). Integer properties may also be provided as decimal strings.</div>
                                            <div>The specified match properties follow the rules of filtering for the zhmcclient library as described in https://python-zhmcclient.readthedocs.io/en/stable/concepts.html#filtering</div>
                                            <div>The possible match properties are all properties in the data model for adapter resources, including <code>name</code>.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-name"></div>
                    <b>name</b>
                    <a class="ansibleOptionLink" href="#parameter-name" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                 / <span style="color: red">required</span>                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                            <div>The name of the target adapter. In case of renaming an adapter, this is the new name of the adapter.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-properties"></div>
                    <b>properties</b>
                    <a class="ansibleOptionLink" href="#parameter-properties" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">dictionary</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                                    <b>Default:</b><br/><div style="color: blue">null</div>
                                    </td>
                                                                <td>
                                            <div>Only for <code>state=set|present</code>: New values for the properties of the adapter. Properties omitted in this dictionary will remain unchanged. This parameter will be ignored for other states.</div>
                                            <div>The parameter is a dictionary. The key of each dictionary item is the property name as specified in the data model for adapter resources, with underscores instead of hyphens. The value of each dictionary item is the property value (in YAML syntax). Integer properties may also be provided as decimal strings.</div>
                                            <div>The possible properties in this dictionary are the properties defined as writeable in the data model for adapter resources, with the following exceptions:</div>
                                            <div>* <code>name</code>: Cannot be specified as a property because the name has already been specified in the <code>name</code> module parameter.</div>
                                            <div>* <code>type</code>: The desired adapter type can be specified in order to support adapters that can change their type (e.g. the FICON Express adapter can change its type between &#x27;not-configured&#x27;, &#x27;fcp&#x27; and &#x27;fc&#x27;).</div>
                                            <div>* <code>crypto_type</code>: The crypto type can be specified in order to support the ability of the Crypto Express adapters to change their crypto type. Valid values are &#x27;ep11&#x27;, &#x27;cca&#x27; and &#x27;acc&#x27;. Changing to &#x27;acc&#x27; will zeroize the crypto adapter.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-state"></div>
                    <b>state</b>
                    <a class="ansibleOptionLink" href="#parameter-state" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                 / <span style="color: red">required</span>                    </div>
                                    </td>
                                <td>
                                                                                                                            <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                                                                                                                                                <li>set</li>
                                                                                                                                                                                                <li>present</li>
                                                                                                                                                                                                <li>absent</li>
                                                                                                                                                                                                <li>facts</li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                            <div>The desired state for the attachment:</div>
                                            <div>* <code>set</code>: Ensures that an existing adapter has the specified properties.</div>
                                            <div>* <code>present</code>: Ensures that a Hipersockets adapter exists and has the specified properties.</div>
                                            <div>* <code>absent</code>: Ensures that a Hipersockets adapter does not exist.</div>
                                            <div>* <code>facts</code>: Does not change anything on the adapter and returns the adapter properties including its ports.</div>
                                                        </td>
            </tr>
                        </table>
    <br/>




Examples
--------

.. code-block:: yaml+jinja

    
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
Common return values are documented :ref:`here <common_return_values>`, the following are the fields unique to this module:

.. raw:: html

    <table border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Key</th>
            <th>Returned</th>
            <th width="100%">Description</th>
        </tr>
                    <tr>
                                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-cpc"></div>
                    <b>cpc</b>
                    <a class="ansibleOptionLink" href="#return-cpc" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                                          </div>
                                    </td>
                <td>success</td>
                <td>
                                                                        <div>For <code>state=absent</code>, an empty dictionary.</div>
                                                    <div>For <code>state=set|present|facts</code>, a dictionary with the properties of the adapter. The properties contain these additional artificial properties for listing its child resources: - &#x27;ports&#x27;: The ports of the adapter, as a dict of key: port name, value: dict of a subset of the port properties (name, status, element_uri).</div>
                                                                <br/>
                                            <div style="font-size: smaller"><b>Sample:</b></div>
                                                <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;"><code>{
      &quot;name&quot;: &quot;adapter-1&quot;,
      &quot;description&quot;: &quot;Adapter 1&quot;,
      &quot;status&quot;: &quot;active&quot;,
      &quot;acceptable_status&quot;: [ &quot;active&quot; ],
      ...
      &quot;ports&quot;: [
        {
          &quot;name&quot;: &quot;Port 0&quot;,
          ...
        },
        ...
      ]
    }</code></div>
                                    </td>
            </tr>
                        </table>
    <br/><br/>


Status
------




- This module is guaranteed to have backward compatible interface changes going forward. *[stableinterface]*


- This module is :ref:`maintained by the Ansible Community <modules_support>`. *[community]*





Authors
~~~~~~~

- Andreas Maier (@andy-maier)
- Andreas Scheuring (@scheuran)


.. hint::
    If you notice any issues in this documentation, you can `edit this document <https://github.com/ansible/ansible/edit/devel/lib/ansible/modules/zhmc_adapter.py?description=%23%23%23%23%23%20SUMMARY%0A%3C!---%20Your%20description%20here%20--%3E%0A%0A%0A%23%23%23%23%23%20ISSUE%20TYPE%0A-%20Docs%20Pull%20Request%0A%0A%2Blabel:%20docsite_pr>`_ to improve it.
