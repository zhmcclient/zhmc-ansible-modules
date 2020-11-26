.. Copyright 2017-2020 IBM Corp. All Rights Reserved.
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..    http://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.
..


.. _`Playbooks`:

Playbooks
=========

An `Ansible playbook`_ consists of organized instructions that define work for
a managed node (hosts) to be managed with Ansible. In case of
**IBM Z HMC Collection**, the managed node is the local host, and the IP address
of the HMC is specified as an input parameter to the Ansible modules.

Playbook Documentation
----------------------

After having installed **IBM Z HMC Collection**, you find the
sample playbooks in folder ``ibm/zhmc/playbooks/`` of your local Ansible
collection directory (e.g. ``$HOME/.ansible/collections/ansible_collections/``).
Alternatively, you can download the sample playbooks from the
`playbooks directory`_ of the Git repository.

All sample playbooks include two files for defining credentials and other
input parameters:

* ``vars.yml`` defines variables such as CPC name, partition name, etc. It does
  not exist in that directory but can be copied from ``vars_example.yml``,
  changing the variables to your needs.

* ``vault.yml`` is a password vault file defining variables for authenticating
  with the HMC. It does not exist in that directory but can be copied from
  ``vault_example.yml``, changing the variables to your needs.

Run the Playbooks
-----------------

Two of the sample playbooks are:

* ``sample_create_partition_full.yml`` creates a partition with a NIC, HBA and
  virtual function to an accelerator adapter.

* ``sample_delete_partition.yml`` deletes a partition.

The following examples assume that you have the playbook files in the current
directory.
You can use the `ansible-playbook`_ command to run these two playbooks as follows:

.. code-block:: sh

    $ ansible-playbook sample_create_partition_full.yml

    PLAY [localhost] **********************************************************

    TASK [Gathering Facts] ****************************************************
    ok: [127.0.0.1]

    TASK [Ensure partition exists and is stopped] *****************************
    changed: [127.0.0.1]

    TASK [Ensure HBA exists in the partition] *********************************
    changed: [127.0.0.1]

    TASK [Ensure NIC exists in the partition] *********************************
    changed: [127.0.0.1]

    TASK [Ensure virtual function exists in the partition] ********************
    changed: [127.0.0.1]

    TASK [Configure partition for booting via HBA] ****************************
    changed: [127.0.0.1]

    PLAY RECAP ****************************************************************
    127.0.0.1                  : ok=6    changed=5    unreachable=0    failed=0

    $ ansible-playbook sample_delete_partition.yml

    PLAY [localhost] **********************************************************

    TASK [Gathering Facts] ****************************************************
    ok: [127.0.0.1]

    TASK [Ensure partition does not exist] ************************************
    changed: [127.0.0.1]

    PLAY RECAP ****************************************************************
    127.0.0.1                  : ok=2    changed=1    unreachable=0    failed=0


.. _playbooks directory:
   https://github.com/zhmcclient/zhmc-ansible-modules/tree/master/playbooks/
.. _Ansible playbook:
   https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html#playbooks-intro
.. _ansible-playbook:
   https://docs.ansible.com/ansible/latest/cli/ansible-playbook.html
