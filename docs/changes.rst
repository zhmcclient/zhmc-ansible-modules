.. Copyright 2017-2018 IBM Corp. All Rights Reserved.
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

.. _`Change log`:

Change log
----------


Version 0.7.0
^^^^^^^^^^^^^

Released: 2019-02-20

**Incompatible changes:**

* Temporarily disabled the retrieval of full properties in the result data
  of the zhmc_adapter module.

**Bug fixes:**

* Docs: Fixed change log of 0.6.0 (see the 0.6.0 section below).

**Enhancements:**

* Renovated the logging:
  - Added support for the log_file parameter to all modules.
  - Changed the format of the log lines.
  - Set log level also when no log_file is specified, causing
    the logs to be propagated to the root logger.


Version 0.6.0
^^^^^^^^^^^^^

Released: 2019-01-07

Fixed this change log in 0.6.1 and 0.7.0

**Bug fixes:**

* Fixed dependency to zhmcclient package to be >=0.20.0, instead
  of using its master branch from the github repo.

* Updated the 'requests' package to 2.20.0 to fix the following vulnerability:
  https://nvd.nist.gov/vuln/detail/CVE-2018-18074

* Added support for Python 3.7. This required increasing the minimum version
  of Ansible from 2.2.0.0 to 2.4.0.0.
  This also removes the dependency on the 'pycrypto' package, which has
  vulnerabilities and is no longer maintained since 2013. Ansible uses the
  'cryptography' package, instead.  See issue #66.

* The `crypto_number` property of Adapter is an integer property, and thus the
  Ansible module `zhmc_adapter` needs to change the string passed by Ansible
  back to an integer. It did that correctly but only for the `properties`
  input parameter, and not for the `match` input parameter. The type conversions
  are now applied for all properties of Adapter also for the `match` parameter.

* The dictionary to check input properties for the `zhmc_cpc` module had the
  `acceptable_status` property written with a hyphen instead of underscore.
  This had the effect that it was rejected as non-writeable when specifying
  it as input.

**Enhancements:**

* Added support for managing CPCs by adding a `zhmc_cpc` Ansible module.
  The module allows setting writeable properties of a CPC in an idempotent way,
  and to gather facts for a CPC (i.e. all of its properties including a few
  artificial ones). See issue #82.

* Added support for managing adapters by adding a `zhmc_adapter` Ansible
  module. The module allows setting writeable properties of an adapter,
  changing the adapter type for FICON Express adapters, and changing the
  crypto type for Crypto Express adapters, all in an idempotent way.
  It also allows gathering facts for an adapter (i.e. all of its properties#
  including a few artificial ones).
  See issue #83.

* Added a `zhmc_crypto_attachment` Ansible module, which manages the attachment
  of crypto adapters and of crypto domains to partitions in an idempotent way.
  This was already supported in a less flexible and non-idempotent way by the
  `zhmc_partition` Ansible module.

* Added support for adjusting the value of the `ssc_ipv4_gateway` input property
  for the `zhmc_partition` module to `None` if specified as the empty string.
  This allows defaulting the value more easily in playbooks.

* Docs: Improved and fixed the documentation how to release a version
  and how to start a new version.


Version 0.5.0
^^^^^^^^^^^^^

Released: 2018-10-24

**Incompatible changes:**

* Changed 'make setup' back to 'make develop' for consistency with the other
  zhmcclient projects.

**Bug fixes:**

* Several fixes in the make process and package dependencies.

* Synced package dependencies with zhmcclient project.

**Enhancements:**

* Added support for DPM storage groups, attachments and volumes, by adding
  new modules 'zhmc_storage_group', 'zhmc_storage_group_attachment', and
  'zhmc_storage_volume'. Added several playbooks as examples.


Version 0.4.0
^^^^^^^^^^^^^

Released: 2018-03-15

**Bug fixes:**

* Fixed the bug that a TypeError was raised when setting the 'ssc_dns_servers'
  property for a Partition. The property value is a list of strings, and
  lists of values were not supported previously. Extended the function test
  cases for partitions accordingly. (Issue #34).

* Fixed that the "type" property for Partitions could not be specified.
  It is valid for Partition creation, and the only restriction is that
  its value cannot be changed once the Partition exists. Along with fixing
  the logic for such create-only properties, the same issue was also fixed
  for the adapter port related properties of HBAs. (Issue #31).

* Improved the logic for handling create+update properties in case
  the resource does not exist, such that they are no longer updated
  in addition to being set during creation. The logic still supports
  updating as an alternative if the resource does not exist, for
  update-only properties (e.g. several properties in Partitions).
  (Fixed as part of issue #31).

* Fixed the issue that a partition in "terminated" or "paused" status
  could not be made absent (i.e. deleted). Now, the partition is
  stopped which should bring it into "stopped" status, and then
  deleted. (Issue #29).

**Enhancements:**

* Added get_facts.py script to examine usage of the Ansible 2.0 API.

* Added support for gathering partition and child facts.
  The fact support is invoked by specifying state=facts.
  The fact support is implemented by returning the partition properties
  in the result. The returned partition properties are enriched by adding
  properties 'hbas', 'nics', 'virtual-functions' that are a list
  of the properties of the respective child elements of that partition.
  (Issue #32).


Version 0.3.0
^^^^^^^^^^^^^

Released: 2017-08-16

**Incompatible changes:**

**Deprecations:**

**Bug fixes:**

**Enhancements:**

* Added support for specifying integer-typed and float-typed
  properties of Partitions, NICs, HBAs, and VFs also as decimal
  strings in the module input.

* Specifying string typed properties of Partitions, NICs, HBAs,
  and VFs with Unicode characters no longer performs an unnecessary
  property update.

**Dependencies:**

* Increased minimum Ansible release from 2.0.0.1 to 2.2.0.0.

* Upgraded zhmcclient requirement to 0.15.0


Version 0.2.0
^^^^^^^^^^^^^^

Released: 2017-07-20

This is the initial release.
