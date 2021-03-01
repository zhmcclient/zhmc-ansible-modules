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

The **IBM Z HMC collection** runs on the control node and communicates with the
targeted HMC via the IP or host name input parameters of the Ansible modules.

In playbooks, this looks as follows:

.. code-block:: text

   - hosts: localhost  # required: target host
     connection: local  # required
     collections:
       - ibm.ibm_zhmc
     tasks:
       - zhmc_adapter:
           hmc_host: 9.10.11.12
           hmc_auth: "{{ hmc_auth }}"
           . . .

Control node
============

Requirements for the Ansible control node are:

* The control node must have network connectivity to the targeted HMC.

.. toctree::
   :maxdepth: 3

   requirements_managed
