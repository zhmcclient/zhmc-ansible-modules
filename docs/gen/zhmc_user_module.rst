:source: zhmc_user.py

:orphan:

.. _zhmc_user_module:


zhmc_user -- Manages users defined on the HMC of Z systems
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Gather facts about a user on an HMC of a Z system.
- Create, delete, or update a user on an HMC.



Requirements
------------
The below requirements are needed on the host that executes this module.

- Access to the WS API of the HMC of the targeted Z system. The targeted Z system can be in any operational mode (classic, DPM)
- Python package zhmcclient >=0.23.0


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
                                            <div>Boolean that controls whether the returned user contains additional artificial properties that expand certain URI or name properties to the full set of resource properties (see description of return values of this module).</div>
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
                                            <div>The userid of the target user (i.e. the &#x27;name&#x27; property of the User object).</div>
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
                                            <div>Dictionary with desired properties for the user. Used for <code>state=present</code>; ignored for <code>state=absent|facts</code>. Dictionary key is the property name with underscores instead of hyphens, and dictionary value is the property value in YAML syntax. Integer properties may also be provided as decimal strings.</div>
                                            <div>The possible input properties in this dictionary are the properties defined as writeable in the data model for User resources (where the property names contain underscores instead of hyphens), with the following exceptions:</div>
                                            <div>* <code>name</code>: Cannot be specified because the name has already been specified in the <code>name</code> module parameter.</div>
                                            <div>* <code>type</code>: Cannot be changed once the user exists.</div>
                                            <div>* <code>user-pattern-uri</code>: Cannot be set directly, but indirectly via the artificial property <code>user-pattern-name</code>.</div>
                                            <div>* <code>password-rule-uri</code>: Cannot be set directly, but indirectly via the artificial property <code>password-rule-name</code>.</div>
                                            <div>* <code>ldap-server-definition-uri</code>: Cannot be set directly, but indirectly via the artificial property <code>ldap-server-definition-name</code>.</div>
                                            <div>* <code>default-group-uri</code>: Cannot be set directly, but indirectly via the artificial property <code>default-group-name</code>.</div>
                                            <div>Properties omitted in this dictionary will remain unchanged when the user already exists, and will get the default value defined in the data model for users in the HMC API book when the user is being created.</div>
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
                                            <div>The desired state for the target user:</div>
                                            <div>* <code>absent</code>: Ensures that the user does not exist.</div>
                                            <div>* <code>present</code>: Ensures that the user exists and has the specified properties.</div>
                                            <div>* <code>facts</code>: Does not change anything on the user and returns the user properties.</div>
                                                        </td>
            </tr>
                        </table>
    <br/>




Examples
--------

.. code-block:: yaml+jinja

    
    ---
    # Note: The following examples assume that some variables named 'my_*' are set.

    - name: Gather facts about a user
      zhmc_user:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        name: "{{ my_user_name }}"
        state: facts
        expand: true
      register: user1

    - name: Ensure the user does not exist
      zhmc_user:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        name: "{{ my_user_name }}"
        state: absent

    - name: Ensure the user exists
      zhmc_user:
        hmc_host: "{{ my_hmc_host }}"
        hmc_auth: "{{ my_hmc_auth }}"
        name: "{{ my_user_name }}"
        state: present
        expand: true
        properties:
          description: "Example user 1"
          type: standard
      register: user1





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
                    <div class="ansibleOptionAnchor" id="return-user"></div>
                    <b>user</b>
                    <a class="ansibleOptionLink" href="#return-user" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">dictionary</span>
                                          </div>
                                    </td>
                <td>success</td>
                <td>
                                                                        <div>For <code>state=absent</code>, an empty dictionary.</div>
                                                    <div>For <code>state=present|facts</code>, a dictionary with the resource properties of the target user, plus additional artificial properties as described in the following list items. The dictionary keys are the exact property names as described in the data model for the resource, i.e. they contain hyphens (-), not underscores (_). The dictionary values are the property values using the Python representations described in the documentation of the zhmcclient Python package. The additional artificial properties are:</div>
                                                    <div>* <code>user-pattern-name</code>: Name of the user pattern referenced by property <code>user-pattern-uri</code>.</div>
                                                    <div>* <code>password-rule-name</code>: Name of the password rule referenced by property <code>password-rule-uri</code>.</div>
                                                    <div>* <code>ldap-server-definition-name</code>: Name of the LDAP server definition referenced by property <code>ldap-server-definition-uri</code>.</div>
                                                    <div>* <code>default-group-name</code>: Name of the group referenced by property <code>default-group-uri</code>.</div>
                                                                <br/>
                                            <div style="font-size: smaller"><b>Sample:</b></div>
                                                <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;"><code>{
      &quot;name&quot;: &quot;user-1&quot;,
      &quot;description&quot;: &quot;user #1&quot;,
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


.. hint::
    If you notice any issues in this documentation, you can `edit this document <https://github.com/ansible/ansible/edit/devel/lib/ansible/modules/zhmc_user.py?description=%23%23%23%23%23%20SUMMARY%0A%3C!---%20Your%20description%20here%20--%3E%0A%0A%0A%23%23%23%23%23%20ISSUE%20TYPE%0A-%20Docs%20Pull%20Request%0A%0A%2Blabel:%20docsite_pr>`_ to improve it.
