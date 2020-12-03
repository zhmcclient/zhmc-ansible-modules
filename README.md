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


<!---
Note: Details on the "Version on Galaxy" badge, below:

Shields.io allows defining dynamic badge creation using data in the result of
an HTTP GET on a JSON based REST API, as follows:

https://img.shields.io/badge/dynamic/json?
  url=<URL>&
  label=<LABEL>&
  query=<$.DATA.SUBDATA>&
  color=<COLOR>&
  prefix=<PREFIX>&
  suffix=<SUFFIX>
plus the standard query parameters (style, color, ...)

Ansible Galaxy returns the latest version of a collection using an HTTP GET on
https://galaxy.ansible.com/api/v2/collections/<NS>/<COLL>/ as follows:

{
    . . .
    "latest_version": {
        "version": "1.0.0-dev1",
    }
}
-->


# IBM Z HMC collection

[![Version on Galaxy](https://img.shields.io/badge/dynamic/json?style=flat&label=galaxy&prefix=v&url=https://galaxy.ansible.com/api/v2/collections/ibm/ibm_zhmc/&query=latest_version.version)](https://galaxy.ansible.com/ibm/ibm_zhmc/ "Version on Galaxy")
[![Test status (master)](https://github.com/zhmcclient/zhmc-ansible-modules/workflows/test/badge.svg?branch=master)](https://github.com/zhmcclient/zhmc-ansible-modules/actions?query=workflow%3Atest "Test status (master)")
[![Docs status (master)](https://github.com/zhmcclient/zhmc-ansible-modules/workflows/docs/badge.svg?branch=master)](https://github.com/zhmcclient/zhmc-ansible-modules/actions?query=workflow%3Adocs "Docs status (master)")
[![Test coverage (master)](https://img.shields.io/coveralls/zhmcclient/zhmc-ansible-modules.svg)](https://coveralls.io/github/zhmcclient/zhmc-ansible-modules "Test coverage (master)")


## Overview

The **IBM Z HMC collection** provides [Ansible](https://www.ansible.com/) modules
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
[ibm.ibm_zhmc collection on Galaxy](https://galaxy.ansible.com/ibm/ibm_zhmc/).

Note that at this point, version 1.0.0 has not been released yet, so please
continue using the latest released version on Pypi.

## Documentation

* [Documentation](https://zhmcclient.github.io/zhmc-ansible-modules/)
* [Releases (change log)](https://zhmcclient.github.io/zhmc-ansible-modules/release_notes.html)

## Sample playbooks

The **IBM Z HMC collection** provides sample playbooks in the
[IBM Z Ansible Collection Samples](https://github.com/IBM/z_ansible_collections_samples/)
repository.

The starting point for reading about them is:
[IBM Z HMC Sample Playbooks](https://github.com/IBM/z_ansible_collections_samples/tree/master/zhmc).
