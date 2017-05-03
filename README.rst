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

zhmc-ansible-modules - Ansible modules for the z Systems HMC Web Services API
=============================================================================


Overview
========

The zhmc-ansible-modules Python package contains `Ansible`_ modules
written in Python that interacts with the Web Services API of the Hardware
Management Console (HMC) of `z Systems`_ or `LinuxONE`_ machines using
the `zhmcclient`_ Python library. The goal of this package is to make
the HMC Web Services API easily consumable for administrators writing
Ansible playbooks to manage their `z Systems`_ infrastructure.

.. _Ansible: https://www.ansible.com/
.. _z Systems: http://www.ibm.com/systems/z/
.. _LinuxONE: http://www.ibm.com/systems/linuxone/
.. _zhmcclient: https://github.com/zhmcclient/python-zhmcclient


Installation
============

The quick way:

a) `Install Ansible`_

.. _Install Ansible: http://docs.ansible.com/ansible/intro_installation.html

b) Then ...

.. code-block:: bash

    $ git clone git@github.ibm.com:LEOPOLDJ/zhmc-ansible-modules.git
    $ cd zhmc-ansible-modules
    $ sudo pip install .
    $ pip show zhmc-ansible-modules | grep Location
    Location: /usr/local/lib/python2.7/dist-packages
    $ export ANSIBLE_LIBRARY=/usr/local/lib/python2.7/dist-packages/ansible/modules


Quickstart
===========

Then you can run the example playbook play1.yml in the folder 'playbooks'
which retrieves information about the HMC. Before you run the playbook, copy
vars_example.yml to vars.yml and fill out the variables with proper values.


.. code-block:: bash

    $ cp vars_example.yml vars.yml
    $ vim vars.yml
    $ ansible-playbook play1.yml

    PLAY [localhost] **********************************************************

    TASK [Gathering Facts] ****************************************************
    ok: [localhost]

    TASK [Get HMC Webservice API info.] ***************************************
    ok: [localhost]

    TASK [debug] **************************************************************
    ok: [localhost] => {
        "changed": false,
        "result": {
            "changed": false,
            "meta": {
                "response": {
                    "api-features": [
                        "internal-get-files-from-se"
                    ],
                    "api-major-version": 2,
                    "api-minor-version": 1,
                    "hmc-name": "HMCpS67b",
                    "hmc-version": "2.13.1"
                }
            }
        }
    }

    PLAY RECAP ****************************************************************
    localhost                  : ok=3    changed=0    unreachable=0    failed=0
