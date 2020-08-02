:source: zhmc_storage_group.py

:orphan:

.. _zhmc_storage_group_module:


zhmc_storage_group -- Manages DPM storage groups (with "dpm-storage-management" feature)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gathers facts about a storage group associated with a CPC, including its storage volumes and virtual storage resources.
- Creates, deletes and updates a storage group associated with a CPC.



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
                                            <div>The name of the CPC associated with the target storage group.</div>
                                                        </td>
            </tr>
                                <tr>
                                                                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-expand"></div>
                    <b>expand</b>
                    <a class="ansibleOptionLink" href="#parameter-expand" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                                                                    </div>
                                    </td>
                                <td>
                                                                                                                                                                                                                    <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                                                                                                                                                <li><div style="color: blue"><b>no</b>&nbsp;&larr;</div></li>
                                                                                                                                                                                                <li>yes</li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                            <div>Boolean that controls whether the returned storage group contains additional artificial properties that expand certain URI or name properties to the full set of resource properties (see description of return values of this module).</div>
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
                                            <div>The name of the target storage group.</div>
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
                                            <div>Dictionary with desired properties for the storage group. Used for <code>state=present</code>; ignored for <code>state=absent|facts</code>. Dictionary key is the property name with underscores instead of hyphens, and dictionary value is the property value in YAML syntax. Integer properties may also be provided as decimal strings.</div>
                                            <div>The possible input properties in this dictionary are the properties defined as writeable in the data model for Storage Group resources (where the property names contain underscores instead of hyphens), with the following exceptions:</div>
                                            <div>* <code>name</code>: Cannot be specified because the name has already been specified in the <code>name</code> module parameter.</div>
                                            <div>* <code>type</code>: Cannot be changed once the storage group exists.</div>
                                            <div>Properties omitted in this dictionary will remain unchanged when the storage group already exists, and will get the default value defined in the data model for storage groups in the HMC API book when the storage group is being created.</div>
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
                                                                                                                                                                                                <li>facts</li>
                                                                                    </ul>
                                                                            </td>
                                                                <td>
                                            <div>The desired state for the target storage group:</div>
                                            <div>* <code>absent</code>: Ensures that the storage group does not exist. If the storage group is currently attached to any partitions, the module will fail.</div>
                                            <div>* <code>present</code>: Ensures that the storage group exists and is associated with the specified CPC, and has the specified properties. The attachment state of the storage group to a partition is not changed.</div>
                                            <div>* <code>facts</code>: Does not change anything on the storage group and returns the storage group properties.</div>
                                                        </td>
            </tr>
                        </table>
    <br/>


Notes
-----

.. note::
   - The CPC that is associated with the target storage group must be in the Dynamic Partition Manager (DPM) operational mode and must have the "dpm-storage-management" firmware feature enabled. That feature has been introduced with the z14-ZR1 / Rockhopper II machine generation.
   - This module performs actions only against the Z HMC regarding the definition of storage group objects and their attachment to partitions. This module does not perform any actions against storage subsystems or SAN switches.
   - Attachment of a storage group to and from partitions is managed by the Ansible module zhmc_storage_group_attachment.
   - The Ansible module zhmc_hba is no longer used on CPCs that have the "dpm-storage-management" feature enabled.



Examples
--------

.. code-block:: yaml+jinja

    
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
                    <div class="ansibleOptionAnchor" id="return-storage_group"></div>
                    <b>storage_group</b>
                    <a class="ansibleOptionLink" href="#return-storage_group" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                                          </div>
                                    </td>
                <td>success</td>
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
                                                                <br/>
                                            <div style="font-size: smaller"><b>Sample:</b></div>
                                                <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;"><code>{
      &quot;name&quot;: &quot;sg-1&quot;,
      &quot;description&quot;: &quot;storage group #1&quot;,
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
    If you notice any issues in this documentation, you can `edit this document <https://github.com/ansible/ansible/edit/devel/lib/ansible/modules/zhmc_storage_group.py?description=%23%23%23%23%23%20SUMMARY%0A%3C!---%20Your%20description%20here%20--%3E%0A%0A%0A%23%23%23%23%23%20ISSUE%20TYPE%0A-%20Docs%20Pull%20Request%0A%0A%2Blabel:%20docsite_pr>`_ to improve it.
