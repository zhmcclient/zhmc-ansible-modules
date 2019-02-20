.. _zhmc_crypto_attachment:


zhmc_crypto_attachment - Manages the attachment of crypto adapters and domains to partitions.
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



.. contents::
   :local:
   :depth: 2


Synopsis
--------

* Gathers facts about the attachment of crypto adapters and domains to a partition.
* Attaches a range of crypto domains and a number of crypto adapters to a partition.
* Detaches all crypto domains and all crypto adapters from a partition.


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
    <td>access_mode<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>usage</td>
    <td><ul><li>usage</li><li>control</li></ul></td>
    <td>
        <div>Only for <code>state=attach</code>: The access mode in which the crypto domains specified in <code>domain_range</code> need to be attached.</div>
    </td>
    </tr>

    <tr>
    <td>adapter_count<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>-1</td>
    <td></td>
    <td>
        <div>Only for <code>state=attach</code>: The number of crypto adapters the partition needs to have attached. The special value -1 means all adapters of the desired crypto type in the CPC.</div>
    </td>
    </tr>

    <tr>
    <td>cpc_name<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td></td>
    <td>
        <div>The name of the CPC that has the partition and the crypto adapters.</div>
    </td>
    </tr>

    <tr>
    <td>crypto_type<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>ep11</td>
    <td><ul><li>ep11</li><li>cca</li><li>acc</li></ul></td>
    <td>
        <div>Only for <code>state=attach</code>: The crypto type of the crypto adapters that will be considered for attaching.</div>
    </td>
    </tr>

    <tr>
    <td>domain_range<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>(0, -1)</td>
    <td></td>
    <td>
        <div>Only for <code>state=attach</code>: The domain range the partition needs to have attached, as a tuple of integers (min, max) that specify the inclusive range of domain index numbers. Other domains attached to the partition remain unchanged. The special value -1 for the max item means the maximum supported domain index number.</div>
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
    <td>partition_name<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td></td>
    <td>
        <div>The name of the partition to which the crypto domains and crypto adapters are attached.</div>
    </td>
    </tr>

    <tr>
    <td>state<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td><ul><li>attached</li><li>detached</li><li>facts</li></ul></td>
    <td>
        <div>The desired state for the attachment:</div>
        <div>* <code>attached</code>: Ensures that the specified number of crypto adapters of the specified crypto type, and the specified range of domain index numbers in the specified access mode are attached to the partition.</div>
        <div>* <code>detached</code>: Ensures that no crypto adapter and no crypto domains are attached to the partition.</div>
        <div>* <code>facts</code>: Does not change anything on the attachment and returns the crypto configuration of the partition.</div>
    </td>
    </tr>

    </table>
    </br>



Examples
--------

 ::

    
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
    <td>crypto_configuration</td>
    <td>
        <div>For <code>state=detached|attached|facts</code>, a dictionary with the crypto configuration of the partition after the changes applied by the module. Key is the partition name, and value is a dictionary with keys: - 'adapters': attached adapters, as a dict of key: adapter name, value: dict of adapter properties; - 'domain_config': attached domains, as a dict of key: domain index, value: access mode ('control' or 'usage'); - 'usage_domains': domains attached in usage mode, as a list of domain index numbers; - 'control_domains': domains attached in control mode, as a list of domain index numbers.</div>
    </td>
    <td align=center>success</td>
    <td align=center>dict</td>
    <td align=center><code>{
      "part-1": {
        "adapters": {
          "adapter 1": {
            "type": "crypto",
            ...
          }
        },
        "domain_config": {
          "0": "usage",
          "1": "control",
          "2": "control"
        }
        "usage_domains": [0],
        "control_domains": [1, 2]
      }
    }</code>
    </td>
    </tr>

    <tr>
    <td>changes</td>
    <td>
        <div>For <code>state=detached|attached|facts</code>, a dictionary with the changes performed.</div>
    </td>
    <td align=center>success</td>
    <td align=center>dict</td>
    <td align=center><code>{
      "added-adapters": ["adapter 1", "adapter 2"],
      "added-domains": ["0", "1"]
    }</code>
    </td>
    </tr>

    </table>
    </br>
    </br>

Notes
-----

.. note::
    - The CPC of the target partition must be in the Dynamic Partition Manager (DPM) operational mode.



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


