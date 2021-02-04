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

Modules
=======

Ansible® modules can be used from the command line, in a playbook or in
an role.

The **IBM Z® HMC collection** provides several modules. Reference material for
each module contains documentation on what parameters the module accepts and
what will returned.

You can also access the documentation of each module from the command line by
using the `ansible-doc`_ command, for example:

.. code-block:: sh

   $ ansible-doc ibm.ibm_zhmc.zhmc_adapter

.. _ansible-doc:
   https://docs.ansible.com/ansible/latest/cli/ansible-doc.html#ansible-doc

.. toctree::
   :maxdepth: 1
   :glob:

   modules/*
