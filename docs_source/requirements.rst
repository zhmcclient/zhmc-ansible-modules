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


.. _`Requirements`:

Requirements
============

For **IBM Z HMC Collection**, the managed node is the control node, i.e. the
playbook has its ``hosts`` and ``connection`` properties set accordingly:

.. code-block:: text

   - hosts: localhost
     connection: local

The location of the HMC is defined with input parameters to the modules.

Control node
============

Besides having Ansible and **IBM Z HMC Collection** installed, there are no
additional requirements for the control node.

.. toctree::
   :maxdepth: 3

   requirements_managed
