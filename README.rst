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

.. code-block:: text

    $ git clone git@github.ibm.com:LEOPOLDJ/zhmc-ansible-modules.git
    $ cd zhmc-ansible-modules
    $ sudo pip install .
    $ pip show zhmc-ansible-modules | grep Location
    Location: /usr/local/lib/python2.7/dist-packages
    $ export ANSIBLE_LIBRARY=/usr/local/lib/python2.7/dist-packages/ansible/modules

The sequence above installs this Python package and its dependent packages
into your system Python. If you prefer using virtual Python environments instead,
see `Using virtual Python environments`_.

Quickstart
===========

Then you can run the example playbook play1.yml in the folder 'playbooks'
which retrieves information about the HMC. Before you run the playbook, copy
vars_example.yml to vars.yml and fill out the variables with proper values.


.. code-block:: text

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

Using virtual Python environments
=================================

It is possible to use this Python package in a virtual Python environment
set up using ``virtualenv``, by configuring Ansible to use the Python that
is found in the PATH, for the local target system.

This is based on the fact that when using ``virtualenv``, the PATH is set
up to use the desired virtual Python, and on the fact that this Python
package uses Ansible to target the local system (which then talks to
the desired HMC).

To set up your local Ansible installation to use the currently active
Python, issue these commands in a bash shell on the system you plan to
invoke Ansible from (e.g. your workstation), after possibly adjusting
the shell variables that are shown:

.. code-block:: bash

    # Adjust this if needed: File path to a shell script that invokes
    # the current Python in PATH:
    set env_python=$HOME/local/bin/env_python

    # Create a shell script that invokes the currently active Python:
    cat >$env_python <<'EOT'
    #!/bin/bash
    py=$(which python)
    $py "$@"
    EOT
    chmod 755 $env_python

    # Configure Ansible to invoke Python via the new shell script when
    # targeting the local system:
    sudo tee -a /etc/ansible/hosts >/dev/null <<EOT

    [local:vars]
    ansible_python_interpreter=$env_python
    EOT

To work with this Python package in a virtual Python environment, issue:

.. code-block:: text

    $ git clone git@github.ibm.com:LEOPOLDJ/zhmc-ansible-modules.git
    $ cd zhmc-ansible-modules
    $ workon {venv}
    $ pip install .
    $ pip show zhmc-ansible-modules | grep Location
    Location: /home/{user}/virtualenvs/{venv}/lib/python2.7/site-packages
    $ export ANSIBLE_LIBRARY=/home/{user}/virtualenvs/{venv}/lib/python2.7/site-packages/ansible/modules
