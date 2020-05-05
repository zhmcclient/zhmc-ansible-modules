:source: zhmc_partition.py

:orphan:

.. _zhmc_partition_module:


zhmc_partition -- Manages partitions of Z systems
+++++++++++++++++++++++++++++++++++++++++++++++++


.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gather facts about a partition of a CPC (Z system), including its HBAs, NICs, and virtual functions.
- Create, update, or delete a partition. The HBAs, NICs, and virtual functions of the partition are are managed by separate Ansible modules.
- Start or stop a partition.



Requirements
------------
The below requirements are needed on the host that executes this module.

- Access to the WS API of the HMC of the targeted Z system. The targeted Z system must be in the Dynamic Partition Manager (DPM) operational mode.
- Python package zhmcclient >=0.14.0


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
                                            <div>The name of the CPC with the target partition.</div>
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
                                            <div>The authentication credentials for the HMC, as a dictionary of userid, password.</div>
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
                                            <div>The name of the target partition.</div>
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
                                                                                                                                                                                                <li>stopped</li>
                                                                                                                                                                                                <li>active</li>
                                                                                                                                                                                                <li>facts</li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                            <div>The desired state for the target partition:</div>
                                            <div><code>absent</code>: Ensures that the partition does not exist in the specified CPC.</div>
                                            <div><code>stopped</code>: Ensures that the partition exists in the specified CPC, has the specified properties, and is in the &#x27;stopped&#x27; status.</div>
                                            <div><code>active</code>: Ensures that the partition exists in the specified CPC, has the specified properties, and is in the &#x27;active&#x27; or &#x27;degraded&#x27; status.</div>
                                            <div><code>facts</code>: Does not change anything on the partition and returns the partition properties and the properties of its child resources (HBAs, NICs, and virtual functions).</div>
                                                        </td>
            </tr>
                        </table>
    <br/>



See Also
--------

.. seealso::



Examples
--------

.. code-block:: yaml+jinja

    
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
                    <div class="ansibleOptionAnchor" id="return-partition"></div>
                    <b>partition</b>
                    <a class="ansibleOptionLink" href="#return-partition" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                                          </div>
                                    </td>
                <td>success</td>
                <td>
                                                                        <div>For <code>state=absent</code>, an empty dictionary.</div>
                                                    <div>For <code>state=stopped</code> and <code>state=active</code>, a dictionary with the resource properties of the partition (after changes, if any). The dictionary keys are the exact property names as described in the data model for the resource, i.e. they contain hyphens (-), not underscores (_). The dictionary values are the property values using the Python representations described in the documentation of the zhmcclient Python package.</div>
                                                    <div>For <code>state=facts</code>, a dictionary with the resource properties of the partition, including its child resources (HBAs, NICs, and virtual functions). The dictionary keys are the exact property names as described in the data model for the resource, i.e. they contain hyphens (-), not underscores (_). The dictionary values are the property values using the Python representations described in the documentation of the zhmcclient Python package. The properties of the child resources are represented in partition properties named &#x27;hbas&#x27;, &#x27;nics&#x27;, and &#x27;virtual-functions&#x27;, respectively.</div>
                                                                <br/>
                                            <div style="font-size: smaller"><b>Sample:</b></div>
                                                <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;"><code>{
      &quot;name&quot;: &quot;part-1&quot;,
      &quot;description&quot;: &quot;partition #1&quot;,
      &quot;status&quot;: &quot;active&quot;,
      &quot;boot-device&quot;: &quot;storage-adapter&quot;,
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
    If you notice any issues in this documentation, you can `edit this document <https://github.com/ansible/ansible/edit/devel/lib/ansible/modules/zhmc_partition.py?description=%23%23%23%23%23%20SUMMARY%0A%3C!---%20Your%20description%20here%20--%3E%0A%0A%0A%23%23%23%23%23%20ISSUE%20TYPE%0A-%20Docs%20Pull%20Request%0A%0A%2Blabel:%20docsite_pr>`_ to improve it.
