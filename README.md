<!---
Copyright 2017-2020 IBM Corp. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->


# IBM Z HMC Collection

[![Github Releases](https://img.shields.io/github/v/release/zhmcclient/zhmc-ansible-modules)](https://github.com/zhmcclient/zhmc-ansible-modules/releases "Github Releases")
[![Ansible Galaxy](https://img.shields.io/badge/galaxy-ibm.zhmc-660198.svg?style=flat)](https://galaxy.ansible.com/ibm/zhmc/ "Ansible Galaxy")
[![Test status (master)](https://github.com/zhmcclient/zhmc-ansible-modules/workflows/test/badge.svg?branch=master)](https://github.com/zhmcclient/zhmc-ansible-modules/actions?query=workflow%3Atest "Test status (master)")
[![Docs status (master)](https://github.com/zhmcclient/zhmc-ansible-modules/workflows/pages/badge.svg?branch=master)](https://github.com/zhmcclient/zhmc-ansible-modules/actions?query=workflow%3Apages "Docs status (master)")
[![Coveralls result](https://img.shields.io/coveralls/zhmcclient/zhmc-ansible-modules.svg)](https://coveralls.io/github/zhmcclient/zhmc-ansible-modules "Coveralls result")


## Overview

**IBM Z HMC Collection** provides [Ansible](https://www.ansible.com/) modules
that can manage platform resources on [IBM Z](http://www.ibm.com/it-infrastructure/z/) and
[LinuxONE](http://www.ibm.com/it-infrastructure/linuxone/) machines.

The goal of this collection is to be able to utilize the power and ease of use
of Ansible for the management of IBM Z platform resources.

The IBM Z resources that can be managed include for example partitions, adapters,
the Z system itself, or various resources on its Hardware Management Console
(HMC).

The Ansible modules in this collection are fully
[idempotent](http://docs.ansible.com/ansible/latest/glossary.html#term-idempotency),
following an important principle for Ansible modules.
The idempotency of a module allows Ansible playbooks to specify the desired end
state for a resource, regardless of what the current state is. For example, an
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

The Ansible modules in this collection are written in Python
and interact with the Web Services API of the Hardware Management Console (HMC)
of the machines to be managed, by using the API of the
[zhmcclient](https://github.com/zhmcclient/python-zhmcclient)
Python package.

Note: Before version 1.0.0, the Ansible modules in this collection have been
distributed as the
[zhmc-ansible-modules package on Pypi](https://pypi.org/project/zhmc-ansible-modules/).
Starting with version 1.0.0, the Ansible modules are no longer distributed on
Pypi, but as the
[ibm.zhmc collection on Galaxy](https://galaxy.ansible.com/ibm/zhmc/).

Note that at this point, version 1.0.0 has not been released yet, so please
continue using the latest released version on Pypi.

## Documentation

* [Documentation](https://zhmcclient.github.io/zhmc-ansible-modules/)
* [Releases (change log)](https://zhmcclient.github.io/zhmc-ansible-modules/release_notes.html)

## Playbook examples

Here are some examples for using the Ansible modules in this project:

### Create a stopped partition

This task ensures that a partition with this name exists, is in the
stopped status and has certain property values.

``` {.sourceCode .yaml}
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
```

### Start a partition

If this task is run after the previous one shown above, no properties
need to be specified. If it is possible that the partition first needs
to be created, then properties would be specified, as above.

``` {.sourceCode .yaml}
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
```

### Delete a partition

This task ensures that a partition with this name does not exist. If it
currently exists, it is stopped (if needed) and deleted.

``` {.sourceCode .yaml}
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
```

### Create a NIC in a partition

``` {.sourceCode .yaml}
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
```

### Configure partition for booting from FCP LUN

``` {.sourceCode .yaml}
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
```

### Configure crypto config of a partition

``` {.sourceCode .yaml}
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
```

## Quick start

For installation instructions, see
[Installation](https://zhmcclient.github.io/zhmc-ansible-modules/installation.html).

After having installed the ibm.zhmc Ansible Galaxy collection, you find the
sample playbooks in folder ``ibm/zhmc/playbooks/`` of your local Ansible
collection directory (e.g. ``$HOME/.ansible/collections/ansible_collections/``),
for example:

- `sample_create_partition_full.yml` creates a partition with a NIC, HBA and
  virtual function to an accelerator adapter.

- `sample_delete_partition.yml` deletes a partition.

These example playbooks include two other files for defining credentials
and other variables:

- `vars.yml` defines variables such as CPC name, partition name, etc. It
  does not exist in that directory but can be copied from `vars_example.yml`,
  changing the variables to your needs.

- `vault_example.yml` is a password vault file defining variables for
  authenticating with the HMC. It does not exist in that directory but can be
  copied from `vault_example.yml`, changing the variables to your needs.

Then, run the example playbooks:

``` {.sourceCode .text}
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
```
