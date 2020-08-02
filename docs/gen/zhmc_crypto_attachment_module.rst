:source: zhmc_crypto_attachment.py

:orphan:

.. _zhmc_crypto_attachment_module:


zhmc_crypto_attachment -- Manages the attachment of crypto adapters and domains to partitions
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gathers facts about the attachment of crypto adapters and domains to a partition.
- Attaches a range of crypto domains and a number of crypto adapters to a partition.
- Detaches all crypto domains and all crypto adapters from a partition.



Requirements
------------
The below requirements are needed on the host that executes this module.

- Network access to HMC
- zhmcclient >=0.20.0
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
                    <div class="ansibleOptionAnchor" id="parameter-access_mode"></div>
                    <b>access_mode</b>
                    <a class="ansibleOptionLink" href="#parameter-access_mode" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                            <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                                                                                                                                                <li><div style="color: blue"><b>usage</b>&nbsp;&larr;</div></li>
                                                                                                                                                                                                <li>control</li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                            <div>Only for <code>state=attach</code>: The access mode in which the crypto domains specified in <code>domain_range</code> need to be attached.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-adapter_count"></div>
                    <b>adapter_count</b>
                    <a class="ansibleOptionLink" href="#parameter-adapter_count" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                                    <b>Default:</b><br/><div style="color: blue">-1</div>
                                    </td>
                                                                <td>
                                            <div>Only for <code>state=attach</code>: The number of crypto adapters the partition needs to have attached. The special value -1 means all adapters of the desired crypto type in the CPC.</div>
                                                        </td>
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
                                            <div>The name of the CPC that has the partition and the crypto adapters.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-crypto_type"></div>
                    <b>crypto_type</b>
                    <a class="ansibleOptionLink" href="#parameter-crypto_type" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                            <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                                                                                                                                                <li><div style="color: blue"><b>ep11</b>&nbsp;&larr;</div></li>
                                                                                                                                                                                                <li>cca</li>
                                                                                                                                                                                                <li>acc</li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                            <div>Only for <code>state=attach</code>: The crypto type of the crypto adapters that will be considered for attaching.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-domain_range"></div>
                    <b>domain_range</b>
                    <a class="ansibleOptionLink" href="#parameter-domain_range" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=integer</span>                                            </div>
                                    </td>
                                <td>
                                                                                                                                                                    <b>Default:</b><br/><div style="color: blue">[0, -1]</div>
                                    </td>
                                                                <td>
                                            <div>Only for <code>state=attach</code>: The domain range the partition needs to have attached, as a tuple of integers (min, max) that specify the inclusive range of domain index numbers. Other domains attached to the partition remain unchanged. The special value -1 for the max item means the maximum supported domain index number.</div>
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
                                            <div>The name of the partition to which the crypto domains and crypto adapters are attached.</div>
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
                                                                                                                                                                <li>attached</li>
                                                                                                                                                                                                <li>detached</li>
                                                                                                                                                                                                <li>facts</li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                            <div>The desired state for the attachment:</div>
                                            <div>* <code>attached</code>: Ensures that the specified number of crypto adapters of the specified crypto type, and the specified range of domain index numbers in the specified access mode are attached to the partition.</div>
                                            <div>* <code>detached</code>: Ensures that no crypto adapter and no crypto domains are attached to the partition.</div>
                                            <div>* <code>facts</code>: Does not change anything on the attachment and returns the crypto configuration of the partition.</div>
                                                        </td>
            </tr>
                        </table>
    <br/>


Notes
-----

.. note::
   - The CPC of the target partition must be in the Dynamic Partition Manager (DPM) operational mode.



Examples
--------

.. code-block:: yaml+jinja

    
    ---
    # Note: The following examples assume that some variables named 'my_*' are set.

    - name: Gather facts about the crypto configuration of a partition
      zhmc_crypto_attachment:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        partition_name: "{{ my_partition_name }}"
        state: facts
      register: crypto1

    - name: Ensure domain 0 on all ep11 adapters is attached in usage mode
      zhmc_crypto_attachment:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        partition_name: "{{ my_first_partition_name }}"
        state: attached
        crypto_type: ep11
        adapter_count: -1
        domain_range: 0,0
        access_mode: usage

    - name: Ensure domains 1-max on all ep11 adapters are attached in control mode
      zhmc_crypto_attachment:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        partition_name: "{{ my_first_partition_name }}"
        state: attached
        crypto_type: ep11
        adapter_count: -1
        domain_range: 1,-1
        access_mode: control

    - name: Ensure domains 0-max on 1 ep11 adapter are attached to in usage mode
      zhmc_crypto_attachment:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        cpc_name: "{{ my_cpc_name }}"
        partition_name: "{{ my_second_partition_name }}"
        state: attached
        crypto_type: ep11
        adapter_count: 1
        domain_range: 0,-1
        access_mode: usage





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
                    <div class="ansibleOptionAnchor" id="return-changes"></div>
                    <b>changes</b>
                    <a class="ansibleOptionLink" href="#return-changes" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                                          </div>
                                    </td>
                <td>success</td>
                <td>
                                                                        <div>For <code>state=detached|attached|facts</code>, a dictionary with the changes performed.</div>
                                                                <br/>
                                            <div style="font-size: smaller"><b>Sample:</b></div>
                                                <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;"><code>{
      &quot;added-adapters&quot;: [&quot;adapter 1&quot;, &quot;adapter 2&quot;],
      &quot;added-domains&quot;: [&quot;0&quot;, &quot;1&quot;]
    }</code></div>
                                    </td>
            </tr>
                                <tr>
                                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-crypto_configuration"></div>
                    <b>crypto_configuration</b>
                    <a class="ansibleOptionLink" href="#return-crypto_configuration" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                                          </div>
                                    </td>
                <td>success</td>
                <td>
                                                                        <div>For <code>state=detached|attached|facts</code>, a dictionary with the crypto configuration of the partition after the changes applied by the module. Key is the partition name, and value is a dictionary with keys: - &#x27;adapters&#x27;: attached adapters, as a dict of key: adapter name, value: dict of adapter properties; - &#x27;domain_config&#x27;: attached domains, as a dict of key: domain index, value: access mode (&#x27;control&#x27; or &#x27;usage&#x27;); - &#x27;usage_domains&#x27;: domains attached in usage mode, as a list of domain index numbers; - &#x27;control_domains&#x27;: domains attached in control mode, as a list of domain index numbers.</div>
                                                                <br/>
                                            <div style="font-size: smaller"><b>Sample:</b></div>
                                                <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;"><code>{
      &quot;part-1&quot;: {
        &quot;adapters&quot;: {
          &quot;adapter 1&quot;: {
            &quot;type&quot;: &quot;crypto&quot;,
            ...
          }
        },
        &quot;domain_config&quot;: {
          &quot;0&quot;: &quot;usage&quot;,
          &quot;1&quot;: &quot;control&quot;,
          &quot;2&quot;: &quot;control&quot;
        }
        &quot;usage_domains&quot;: [0],
        &quot;control_domains&quot;: [1, 2]
      }
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
    If you notice any issues in this documentation, you can `edit this document <https://github.com/ansible/ansible/edit/devel/lib/ansible/modules/zhmc_crypto_attachment.py?description=%23%23%23%23%23%20SUMMARY%0A%3C!---%20Your%20description%20here%20--%3E%0A%0A%0A%23%23%23%23%23%20ISSUE%20TYPE%0A-%20Docs%20Pull%20Request%0A%0A%2Blabel:%20docsite_pr>`_ to improve it.
