<!---
Copyright 2017,2020,2024 IBM Corp. All Rights Reserved.

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
        "version": "1.0.0",
    }
}

Ansible AutomationHub returns the latest version of a collection using an HTTP GET on
https://console.redhat.com/api/automation-hub/v3/collections/<NS>/<COLL>/ as follows:

{
    . . .
    "highest_version": {
        "version": "1.0.0",
    }
}

That would result in the following markup:

[![Version on AutomationHub](https://img.shields.io/badge/dynamic/json?style=flat&label=hub&prefix=v&url=https://console.redhat.com/api/automation-hub/v3/collections/ibm/ibm_zhmc/&query=highest_version.version)](https://console.redhat.com/ansible/automation-hub/repo/published/ibm/ibm_zhmc/ "Version on AutomationHub")

However, for now this does not work, so it has been removed again from the README page.
For details, see the discussion at https://github.com/ansible-collections/overview/discussions/202
-->

[![Version on Galaxy](https://img.shields.io/badge/dynamic/json?style=flat&label=galaxy&prefix=v&url=https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/index/ibm/ibm_zhmc/versions/%3Fis_highest=true&query=data[0].version)](https://galaxy.ansible.com/ui/repo/published/ibm/ibm_zhmc/ "Version on Galaxy")
[![Test status (master)](https://github.com/zhmcclient/zhmc-ansible-modules/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/zhmcclient/zhmc-ansible-modules/actions/workflows/test.yml?query=branch%3Amaster "Test status (master)")
[![Docs status (master)](https://github.com/zhmcclient/zhmc-ansible-modules/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/zhmcclient/zhmc-ansible-modules/actions/workflows/pages/pages-build-deployment "Docs status (master)")
[![Test coverage (master)](https://img.shields.io/coveralls/zhmcclient/zhmc-ansible-modules.svg)](https://coveralls.io/github/zhmcclient/zhmc-ansible-modules "Test coverage (master)")

# IBM® Z HMC collection

The **IBM Z HMC** collection enables automation with the IBM Z Hardware
Management Console (HMC) to manage platform resources on
[IBM Z](https://www.ibm.com/it-infrastructure/z) and
[IBM LinuxONE](https://www.ibm.com/it-infrastructure/linuxone/) machines.

## Description

The **IBM Z HMC** collection is part of the
**Red Hat® Ansible Certified Content for IBM Z®** offering that brings Ansible
automation to IBM Z®.

This collection supports automation tasks on the IBM Z HMC such as creating,
updating or deleting partitions, accesssing operating system messages,
configuring adapters, managing HMC users, upgrading the SE and HMC firmware,
and many more. It supports CPCs in classic mode and in DPM mode.

The IBM Z HMC collection uses the Web Services API of the HMC and therefore its
modules run on the Ansible control node (there is no separate Ansible managed
node in this case).

For guides and reference, please review the
[documentation](https://zhmcclient.github.io/zhmc-ansible-modules/)
or the Z HMC section in the
[unified documentation](https://ibm.github.io/z_ansible_collections_doc/).

## Requirements

Before you install the IBM Z HMC collection, you must have a minimum Python
version and Ansible version on the Ansible control node. The documentation section
[Support matrix](https://zhmcclient.github.io/zhmc-ansible-modules/installation.html#support-matrix)
details the specific version requirements.

## Installation

Before using this collection, you need to install it with the Ansible Galaxy
command-line tool:

```sh
ansible-galaxy collection install ibm.ibm_zhmc
```

You can also include it in a requirements.yml file and install it with
`ansible-galaxy collection install -r requirements.yml`, using the format:

```sh
collections:
  - name: ibm.ibm_zhmc
```

The installation of the collection will not cause any required Python packages
to be installed. They need to be installed separately, either as OS-level
packages or as Python packages, depending on how you manage the Python packages
on your system. A `requirements.txt` file is provided in the installation
directory of the ibm.ibm_zhmc collection for that purpose, either for direct use
with `pip install -r requirements.txt`, or for manually checking and installing
the corresponding OS-level packages.

Note that if you install the collection from Ansible Galaxy, it will not be
upgraded automatically when you upgrade the Ansible (OS-level or Python) package.

To upgrade the collection to the latest available version, run the following
command:

```sh
ansible-galaxy collection install ibm.ibm_zhmc --upgrade
```

You can also install a specific version of the collection, for example, if you
need to downgrade for some reason. For example, the following command installs
version 1.0.0:

```sh
ansible-galaxy collection install ibm.ibm_zhmc:1.0.0
```

## Use Cases

* Use Case Name: Create partition (DPM mode)
  * Actors:
    * System Programmer
  * Description:
    * The system programmer can automate the creation of a partition on a Z
      system (that is in DPM mode).
  * Flow:
    * If the partition does not exist, create it.
    * Update properties of the partition, including boot mode.
    * Bring the partition into the specified status (active, stopped).

* Use Case Name: Adjust workload related LPAR properties (classic mode)
  * Actors:
    * System Programmer
  * Description:
    * The system programmer can automate the adjustment of workload related
      LPAR properties in order to optimize the performance of applications
      running in the LPAR.
  * Flow:
    * Verify LPAR exists on the HMC
    * Update the specified LPAR properties.

* Use Case Name: Update password of HMC user
  * Actors:
    * System Programmer
  * Description:
    * The system programmer can automate the password update for their userid on
      the HMC.
  * Flow:
    * Verify user exists on the HMC
    * Update password of the user

## Testing

All releases will meet the following test criteria:

* 100% success for [Unit](https://github.com/zhmcclient/zhmc-ansible-modules/tree/master/tests/unit) tests.
* 100% success for [Function](https://github.com/zhmcclient/zhmc-ansible-modules/tree/master/tests/function) tests.
* 100% success for [End2end](https://github.com/zhmcclient/zhmc-ansible-modules/tree/master/tests/end2end) tests.
* 100% success for [Ansible sanity](https://docs.ansible.com/ansible/latest/dev_guide/testing/sanity/index.html#all-sanity-tests) tests as part of [ansible-test](https://docs.ansible.com/ansible/latest/dev_guide/testing.html#run-sanity-tests).
* 100% success for [flake8](https://flake8.pycqa.org).
* 100% success for [pylint](https://pylint.readthedocs.io/en/stable/).
* 100% success for [ansible-lint](https://ansible.readthedocs.io/projects/lint/) allowing only false positives.
* 100% success for [safety](https://docs.safetycli.com/safety-docs) vulnerability checks.
* 100% success for [pip-missing-reqs](https://github.com/adamtheturtle/pip-check-reqs/blob/master/README.rst) checks for missing dependencies.

For more details on testing the IBM Z HMC collection, including the specific version
combinations that were tested, refer to documentation section
[Testing](https://zhmcclient.github.io/zhmc-ansible-modules/development.html#testing).

## Contributing

This community is not currently accepting contributions. However, we encourage
you to open [git issues](https://github.com/zhmcclient/zhmc-ansible-modules/issues)
for bugs, comments or feature requests and check back periodically for when
community contributions will be accepted in the near future.

Review the [development docs](https://zhmcclient.github.io/zhmc-ansible-modules/development.html)
to learn how you can create an environment and test the collections modules.

## Communication

If you would like to communicate with this community, you can do so through the
following options:

* GitHub [IBM Z HMC issues](https://github.com/zhmcclient/zhmc-ansible-modules/issues).
* Discord [ansible in System Z Enthusiasts](https://discord.com/channels/880322471608344597/1195381184360894595)
  - Invitation link for server [System Z Enthusiasts](https://discord.gg/Kmy5QaUGbB)
  - Invitation link for channel [ansible](https://discord.gg/nHrDdRTC)

## Support

As Red Hat Ansible
[Certified Content](https://catalog.redhat.com/software/search?target_platforms=Red%20Hat%20Ansible%20Automation%20Platform),
this collection is entitled to [support](https://access.redhat.com/support/) through
[Ansible Automation Platform](https://www.redhat.com/en/technologies/management/ansible)
(AAP). After creating a Red Hat support case, if it is determined the issue
belongs to IBM, Red Hat will instruct you to create an
[IBM support case](https://www.ibm.com/mysupport/s/createrecord/NewCase) and
share the case number with Red Hat so that a collaboration can begin between
Red Hat and IBM.

If a support case cannot be opened with Red Hat and the collection has been
obtained either from [Galaxy](https://galaxy.ansible.com/ui/) or its
[GitHub repo](https://github.com/zhmcclient/zhmc-ansible-modules), there is
community support available at no charge. Community support is limited to the
collection; community support does not include any of the Ansible Automation
Platform components or Ansible.

The current supported versions of this collection can be found listed in the
following section.

## Release Notes and Roadmap

The collection's cumulative release notes can be reviewed
[here](https://zhmcclient.github.io/zhmc-ansible-modules/release_notes.html).
Note, some collection versions release before an ansible-core version reaches
End of Life (EOL), thus the version of ansible-core that is supported must be a
version that is currently supported.

For AAP users, to see the supported ansible-core versions, review the
[AAP Life Cycle](https://access.redhat.com/support/policy/updates/ansible-automation-platform).

For Galaxy and GitHub users, to see the supported ansible-core versions, review the
[ansible-core support matrix](https://docs.ansible.com/ansible/latest/reference_appendices/release_and_maintenance.html#ansible-core-support-matrix).

The collection's changelogs can be reviewed in the following table:

| Version  | Status         | Release notes & change log |
|----------|----------------|----------------------------|
| 1.10.0   | In development | unreleased                 |
| 1.9.4    | Released       | [Release notes & change log](https://zhmcclient.github.io/zhmc-ansible-modules/1.9.4/release_notes.html) |
| 1.8.3    | Released       | [Release notes & change log](https://zhmcclient.github.io/zhmc-ansible-modules/1.8.3/release_notes.html) |
| 1.7.4    | Released       | [Release notes & change log](https://zhmcclient.github.io/zhmc-ansible-modules/1.7.4/release_notes.html) |
| 1.6.1    | Released       | [Release notes & change log](https://zhmcclient.github.io/zhmc-ansible-modules/1.6.1/release_notes.html) |
| 1.5.0    | Released       | [Release notes & change log](https://zhmcclient.github.io/zhmc-ansible-modules/1.5.0/release_notes.html) |
| 1.4.1    | Released       | [Release notes & change log](https://zhmcclient.github.io/zhmc-ansible-modules/1.4.1/release_notes.html) |
| 1.3.1    | Released       | [Release notes & change log](https://zhmcclient.github.io/zhmc-ansible-modules/1.3.1/release_notes.html) |
| 1.2.1    | Released       | [Release notes & change log](https://zhmcclient.github.io/zhmc-ansible-modules/1.2.1/release_notes.html) |
| 1.1.1    | Released       | [Release notes & change log](https://zhmcclient.github.io/zhmc-ansible-modules/1.1.1/release_notes.html) |
| 1.0.3    | Released       | [Release notes & change log](https://zhmcclient.github.io/zhmc-ansible-modules/1.0.3/release_notes.html) |

## Related Information

Example playbooks and use cases can be be found in the
[IBM Z HMC sample playbooks](https://github.com/IBM/z_ansible_collections_samples/tree/master/z_systems_administration/zhmc)
repo.

Supplemental content on getting started with Ansible, architecture and use cases
is available [here](https://ibm.github.io/z_ansible_collections_doc/reference/helpful_links.html).

## License Information

This collection is licensed under
[Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).
