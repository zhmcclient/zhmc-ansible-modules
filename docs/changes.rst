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
