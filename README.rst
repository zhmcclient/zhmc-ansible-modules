.. Copyright 2017 IBM Corp. All Rights Reserved.
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

zhmc-ansible-modules - Ansible modules for the z Systems HMC Web Services API
=============================================================================


Overview
========

The zhmc-ansible-modules Python package contains `Ansible`_ modules that can
manage platform resources on `z Systems`_ and `LinuxONE`_ machines that are in
the Dynamic Partition Manager (DPM) operational mode.

The goal of this package is to be able to utilize the power and ease of use
of Ansible for the management of z Systems platform resources.

The z Systems resources that can be managed include Partitions, HBAs, NICs, and
Virtual Functions.

The Ansible modules in the zhmc-ansible-modules package are fully
`idempotent <http://docs.ansible.com/ansible/latest/glossary.html#term-idempotency>`_,
following an important principle for Ansible modules.

The idempotency of a module allows Ansible playbooks to specify the desired end
state for a resource, regardless of what the current state is. For example, a
z Systems partition can be specified to have ``state=active`` which means that
it must exist and be in the active operational status. Depending on the current
state of the partition, actions will be taken by the module to reach this
desired end state: If the partition does not exist, it will be created and
started. If it exists but is not active, it will be started. If it is already
active, nothing will be done. Other initial states including transitional
states such as starting or stopping also will be taken care of.

The idempotency of modules makes Ansible playbooks restartable: If an error
happens and some things have been changed already, the playbook can simply be
re-run and will automatically do the right thing, because the initial state
does not matter for reaching the desired end state.

The Ansible modules in the zhmc-ansible-modules package are written in Python
and interact with the Web Services API of the Hardware Management Console (HMC)
of the machines to be managed, by using the API of the `zhmcclient`_ Python
package.

.. _Ansible: https://www.ansible.com/
.. _z Systems: http://www.ibm.com/systems/z/
.. _LinuxONE: http://www.ibm.com/systems/linuxone/
.. _zhmcclient: https://github.com/zhmcclient/python-zhmcclient


Documentation
=============

The full documentation for this project is on RTD:
http://zhmc-ansible-modules.readthedocs.io/en/stable/


Quickstart
==========

For installation instructions, see `Installation of zhmc-ansible-modules package
<http://zhmc-ansible-modules.readthedocs.io/en/stable/intro.html#installation>`_.

After having installed the zhmc-ansible-modules package, you can download and
run the example playbooks in `folder 'playbooks' of the Git repository
<https://github.com/zhmcclient/zhmc-ansible-modules/tree/master/playbooks>`_:

* ``create_partition.yml`` creates a partition with a NIC, HBA and virtual
  function to an accelerator adapter.

* ``delete_partition.yml`` deletes a partition.

* ``vars_example.yml`` is an example variable file defining variables such as
  CPC name, partition name, etc.

* ``vault_example.yml`` is an example password vault file defining variables
  for authenticating with the HMC.

Before you run a playbook, copy ``vars_example.yml`` to ``vars.yml`` and
``vault_example.yml`` to ``vault.yml`` and change the variables in those files
as needed.

Then, run the example playbooks:

.. code-block:: text

    $ ansible-playbook create_partition.yml

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

    $ ansible-playbook delete_partition.yml

    PLAY [localhost] **********************************************************

    TASK [Gathering Facts] ****************************************************
    ok: [127.0.0.1]

    TASK [Ensure partition does not exist] ************************************
    changed: [127.0.0.1]

    PLAY RECAP ****************************************************************
    127.0.0.1                  : ok=2    changed=1    unreachable=0    failed=0
