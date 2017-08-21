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

zhmc-ansible-modules - Ansible modules for the IBM Z HMC Web Services API
=========================================================================

.. image:: https://img.shields.io/pypi/v/zhmc-ansible-modules.svg
    :target: https://pypi.python.org/pypi/zhmc-ansible-modules/
    :alt: Version on Pypi

.. image:: https://travis-ci.org/zhmcclient/zhmc-ansible-modules.svg?branch=master
    :target: https://travis-ci.org/zhmcclient/zhmc-ansible-modules
    :alt: Travis test status (master)

.. image:: https://readthedocs.org/projects/zhmc-ansible-modules/badge/?version=latest
    :target: http://zhmc-ansible-modules.readthedocs.io/en/latest/
    :alt: Docs build status (latest)

.. image:: https://img.shields.io/coveralls/zhmcclient/zhmc-ansible-modules.svg
    :target: https://coveralls.io/r/zhmcclient/zhmc-ansible-modules
    :alt: Test coverage (master)

.. contents:: Contents:
   :local:

Overview
========

The zhmc-ansible-modules Python package contains `Ansible`_ modules that can
manage platform resources on `IBM Z`_ and `LinuxONE`_ machines that are in
the Dynamic Partition Manager (DPM) operational mode.

The goal of this package is to be able to utilize the power and ease of use
of Ansible for the management of IBM Z platform resources.

The IBM Z resources that can be managed include Partitions, HBAs, NICs, and
Virtual Functions.

The Ansible modules in the zhmc-ansible-modules package are fully
`idempotent <http://docs.ansible.com/ansible/latest/glossary.html#term-idempotency>`_,
following an important principle for Ansible modules.

The idempotency of a module allows Ansible playbooks to specify the desired end
state for a resource, regardless of what the current state is. For example, a
IBM Z partition can be specified to have ``state=active`` which means that
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
.. _IBM Z: http://www.ibm.com/systems/z/
.. _LinuxONE: http://www.ibm.com/systems/linuxone/
.. _zhmcclient: https://github.com/zhmcclient/python-zhmcclient


Documentation
=============

The full documentation for this project is on RTD:
http://zhmc-ansible-modules.readthedocs.io/en/stable/

Playbook examples
=================

Here are some examples for using the Ansible modules in this project:

Create a stopped partition
--------------------------

This task ensures that a partition with this name exists, is in the stopped
status and has certain property values.

.. code-block:: yaml

    ---
    - hosts: localhost
      tasks:
      - name: Ensure a partition exists and is stopped
        zhmc_partition:
          hmc_host: "10.11.12.13"
          hmc_auth: "{{ hmc_auth }}"
          cpc_name: P000S67B
          name: "my partition 1"
          state: stopped
          properties:
            description: "zhmc Ansible modules: partition 1"
            ifl_processors: 2
            initial_memory: 1024
            maximum_memory: 1024
            minimum_ifl_processing_weight: 50
            maximum_ifl_processing_weight: 800
            initial_ifl_processing_weight: 200
            ... # all partition properties are supported

Start a partition
-----------------

If this task is run after the previous one shown above, no properties need to
be specified. If it is possible that the partition first needs to be created,
then properties would be specified, as above.

.. code-block:: yaml

    ---
    - hosts: localhost
      tasks:
      - name: Ensure a partition exists and is active
        zhmc_partition:
          hmc_host: "10.11.12.13"
          hmc_auth: "{{ hmc_auth }}"
          cpc_name: P000S67B
          name: "my partition 1"
          state: active
          properties:
            ... # see above

Delete a partition
------------------

This task ensures that a partition with this name does not exist. If it
currently exists, it is stopped (if needed) and deleted.

.. code-block:: yaml

    ---
    - hosts: localhost
      tasks:
      - name: Ensure a partition does not exist
        zhmc_partition:
          hmc_host: "10.11.12.13"
          hmc_auth: "{{ hmc_auth }}"
          cpc_name: P000S67B
          name: "my partition 1"
          state: absent

Create an HBA in a partition
----------------------------

.. code-block:: yaml

    ---
    - hosts: localhost
      tasks:
      - name: Ensure HBA exists in the partition
        zhmc_hba:
          hmc_host: "10.11.12.13"
          hmc_auth: "{{ hmc_auth }}"
          cpc_name: P000S67B
          partition_name: "my partition 1"
          name: "hba 1"
          state: present
          properties:
            adapter_name: "fcp 1"
            adapter_port: 0
            description: The HBA to our storage
            device_number: "023F"
            ... # all HBA properties are supported

Create a NIC in a partition
---------------------------

.. code-block:: yaml

    ---
    - hosts: localhost
      tasks:
      - name: Ensure NIC exists in the partition
        zhmc_nic:
          hmc_host: "10.11.12.13"
          hmc_auth: "{{ hmc_auth }}"
          cpc_name: P000S67B
          partition_name: "my partition 1"
          name: "nic 1"
          state: present
          properties:
            adapter_name: "osa 1"
            adapter_port: 1
            description: The NIC to our data network
            device_number: "013F"
            ... # all NIC properties are supported

Create a Virtual Function in a partition
----------------------------------------

.. code-block:: yaml

    ---
    - hosts: localhost
      tasks:
      - name: Ensure virtual function for zEDC adapter exists in the partition
        zhmc_virtual_function:
          hmc_host: "10.11.12.13"
          hmc_auth: "{{ hmc_auth }}"
          cpc_name: P000S67B
          partition_name: "my partition 1"
          name: "vf 1"
          state: present
          properties:
            adapter_name: "zedc 1"
            description: The virtual function for our accelerator adapter
            device_number: "043F"
            ... # all VF properties are supported

Configure partition for booting from FCP LUN
--------------------------------------------

.. code-block:: yaml

    ---
    - hosts: localhost
      tasks:
      - name: Configure partition for booting via HBA
        zhmc_partition:
          hmc_host: "10.11.12.13"
          hmc_auth: "{{ hmc_auth }}"
          cpc_name: P000S67B
          name: "my partition 1"
          state: stopped
          properties:
            boot_device: storage-adapter
            boot_storage_hba_name: "hba 1"
            boot_logical_unit_number: "0001"
            boot_world_wide_port_name: "00cdef01abcdef01"

Configure crypto config of a partition
--------------------------------------

.. code-block:: yaml

    ---
    - hosts: localhost
      tasks:
      - name: Ensure crypto config for partition
        zhmc_partition:
          hmc_host: "10.11.12.13"
          hmc_auth: "{{ hmc_auth }}"
          cpc_name: P000S67B
          name: "my partition 1"
          state: stopped
          properties:
            crypto_configuration:
              crypto_adapter_names:
                - "crypto 1"
              crypto_domain_configurations:
                - domain_index: 17
                  access_mode: "control-usage"
                - domain_index: 19
                  access_mode: "control"


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
