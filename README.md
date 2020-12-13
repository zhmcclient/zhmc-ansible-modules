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


IBM Z HMC collection
====================

[![Version on Galaxy](https://img.shields.io/badge/dynamic/json?style=flat&label=galaxy&prefix=v&url=https://galaxy.ansible.com/api/v2/collections/ibm/ibm_zhmc/&query=latest_version.version)](https://galaxy.ansible.com/ibm/ibm_zhmc/ "Version on Galaxy")
[![Test status (master)](https://github.com/zhmcclient/zhmc-ansible-modules/workflows/test/badge.svg?branch=master)](https://github.com/zhmcclient/zhmc-ansible-modules/actions?query=workflow%3Atest "Test status (master)")
[![Docs status (master)](https://github.com/zhmcclient/zhmc-ansible-modules/workflows/docs/badge.svg?branch=master)](https://github.com/zhmcclient/zhmc-ansible-modules/actions?query=workflow%3Adocs "Docs status (master)")
[![Test coverage (master)](https://img.shields.io/coveralls/zhmcclient/zhmc-ansible-modules.svg)](https://coveralls.io/github/zhmcclient/zhmc-ansible-modules "Test coverage (master)")

The **IBM Z HMC collection** is part of the broader initiative to bring Ansible
Automation to IBM Z®. At this point, the collection is made available as the
[ibm.ibm_zhmc collection on Ansible Galaxy](https://galaxy.ansible.com/ibm/ibm_zhmc/).
In the future, the collection is in addition intended to become part of the
**Red Hat® Ansible Certified Content for IBM Z®** offering.

Note: Before version 0.9.0, this collection has been distributed as the
[zhmc-ansible-modules package on Pypi](https://pypi.org/project/zhmc-ansible-modules/).

Features
========

The **IBM Z HMC collection** provides Ansible modules for automating management
tasks on the Hardware Management Console (HMC) of
[IBM Z](http://www.ibm.com/it-infrastructure/z/) and
[LinuxONE](http://www.ibm.com/it-infrastructure/linuxone/) machines, such as
creating, updating or deleting partitions and other resources.
For guides and reference, please review the
[IBM Z HMC Collection Documentation](https://zhmcclient.github.io/zhmc-ansible-modules/).

The **IBM Z HMC collection** provides sample Ansible playbooks in the
[IBM Z Ansible Collection Samples](https://github.com/IBM/z_ansible_collections_samples/)
repository.
The starting point for reading about them is
[IBM Z HMC Collection Sample Playbooks](https://github.com/IBM/z_ansible_collections_samples/tree/master/zhmc).

Copyright
=========
© Copyright IBM Corporation, 2016-2020.

License
=======
This collection is licensed under
[Apache License, Version 2.0](https://opensource.org/licenses/Apache-2.0).
