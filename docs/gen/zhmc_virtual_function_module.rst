:source: zhmc_virtual_function.py

:orphan:

.. _zhmc_virtual_function_module:


zhmc_virtual_function -- Manages virtual functions in existing partitions
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Creates, updates, and deletes virtual functions in existing partitions of a CPC.
- The targeted CPC must be in the Dynamic Partition Manager (DPM) operational mode.



Requirements
------------
The below requirements are needed on the host that executes this module.

- Network access to HMC
- zhmcclient >=0.14.0
- ansible >=2.2.0.0


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
                                            <div>The name of the CPC with the partition containing the virtual function.</div>
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
                                                                                                                                                            </td>
                                                                <td>
                                            <div>A <code>zhmcclient_mock.FakedSession</code> object that has a mocked HMC set up. If provided, it will be used instead of connecting to a real HMC. This is used for testing purposes only.</div>
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
                                            <div>The authentication credentials for the HMC.</div>
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
                                            <div>The name of the target virtual function that is managed. If the virtual function needs to be created, this value becomes its name.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-partition_name"></div>
                    <b>partition_name</b>
                    <a class="ansibleOptionLink" href="#parameter-partition_name" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                 / <span style="color: red">required</span>                    </div>
                                    </td>
                                <td>
                                                                                                                                                            </td>
                                                                <td>
                                            <div>The name of the partition containing the virtual function.</div>
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
                                            <div>Dictionary with input properties for the virtual function, for <code>state=present</code>. Key is the property name with underscores instead of hyphens, and value is the property value in YAML syntax. Integer properties may also be provided as decimal strings. Will be ignored for <code>state=absent</code>.</div>
                                            <div>The possible input properties in this dictionary are the properties defined as writeable in the data model for Virtual Function resources (where the property names contain underscores instead of hyphens), with the following exceptions:</div>
                                            <div>* <code>name</code>: Cannot be specified because the name has already been specified in the <code>name</code> module parameter.</div>
                                            <div>* <code>adapter_uri</code>: Cannot be specified because this information is specified using the artificial property <code>adapter_name</code>.</div>
                                            <div>* <code>adapter_name</code>: The name of the adapter that backs the target virtual function.</div>
                                            <div>Properties omitted in this dictionary will remain unchanged when the virtual function already exists, and will get the default value defined in the data model for virtual functions when the virtual function is being created.</div>
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
                                                                                                                                                                <li>absent</li>
                                                                                                                                                                                                <li>present</li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                            <div>The desired state for the target virtual function:</div>
                                            <div><code>absent</code>: Ensures that the virtual function does not exist in the specified partition.</div>
                                            <div><code>present</code>: Ensures that the virtual function exists in the specified partition and has the specified properties.</div>
                                                        </td>
            </tr>
                        </table>
    <br/>


Notes
-----

.. note::
   - See also Ansible module zhmc_partition.



Examples
--------

.. code-block:: yaml+jinja

    
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
                    <div class="ansibleOptionAnchor" id="return-virtual_function"></div>
                    <b>virtual_function</b>
                    <a class="ansibleOptionLink" href="#return-virtual_function" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                                          </div>
                                    </td>
                <td>success</td>
                <td>
                                                                        <div>For <code>state=absent</code>, an empty dictionary.</div>
                                                    <div>For <code>state=present</code>, a dictionary with the resource properties of the virtual function (after changes, if any). The dictionary keys are the exact property names as described in the data model for the resource, i.e. they contain hyphens (-), not underscores (_). The dictionary values are the property values using the Python representations described in the documentation of the zhmcclient Python package.</div>
                                                                <br/>
                                            <div style="font-size: smaller"><b>Sample:</b></div>
                                                <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;"><code>{
      &quot;name&quot;: &quot;vfunction-1&quot;,
      &quot;description&quot;: &quot;virtual function #1&quot;,
      &quot;adapter-uri&#x27;: &quot;/api/adapters/...&quot;,
      ...
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
- Juergen Leopold (@leopoldjuergen)


.. hint::
    If you notice any issues in this documentation, you can `edit this document <https://github.com/ansible/ansible/edit/devel/lib/ansible/modules/zhmc_virtual_function.py?description=%23%23%23%23%23%20SUMMARY%0A%3C!---%20Your%20description%20here%20--%3E%0A%0A%0A%23%23%23%23%23%20ISSUE%20TYPE%0A-%20Docs%20Pull%20Request%0A%0A%2Blabel:%20docsite_pr>`_ to improve it.
