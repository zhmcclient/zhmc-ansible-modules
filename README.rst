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

zhmc_ansible_modules - Ansible modules for the z Systems HMC Web Services API
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

    $ git clone git@github.ibm.com:zhmcclient/zhmc-ansible-modules.git
    $ cd zhmc-ansible-modules
    $ sudo pip install .
    $ pip show zhmc-ansible-modules | grep Location
    Location: /usr/lib/python2.7/site-packages
    $ export ANSIBLE_LIBRARY=/usr/local/lib/python2.7/site-packages/zhmc_ansible_modules

The sequence above installs this Python package and its dependent packages
into your system Python, from the master branch of its Git repository.
If you prefer using virtual Python environments instead, see
`Using virtual Python environments`_.

If you want to use one of the released versions of this project, check out
the desired release. For example, to check out release 0.1.0, issue before
the `pip install`:

.. code-block:: text

    $ git checkout 0.1.0


Quickstart
===========

Then you can run the example playbooks in folder ``playbooks``:

* ``create_partition.yml`` creates a partition with a NIC, HBA and virtual
  function to an accelerator adapter.

* ``delete_partition.yml`` deletes a partition.

Before you run a playbook, copy ``vars_example.yml`` to ``vars.yml`` and
``vault_example.yml`` to ``vault.yml`` and change the variables in those files
as needed:

.. code-block:: text

    $ cd playbooks
    $ cp vars_example.yml vars.yml
    $ vim vars.yml
    # Edit variables in vars.yml
    $ cp vault_example.yml vault.yml
    $ vim vault.yml
    # Edit variables in vault.yml

Then, run the playbooks:

.. code-block:: text

    $ ansible-playbook create_partition.yml

    PLAY [localhost] **********************************************************

    TASK [Gathering Facts] ****************************************************
    ok: [127.0.0.1]

    TASK [Ensure partition exists and is stopped] *****************************
    changed: [127.0.0.1]

    TASK [Ensure HBA exists in the partition] *********************************
    changed: [127.0.0.1]

    TASK [Ensure NIC exists in the partition] *********************************
    changed: [127.0.0.1]

    TASK [Ensure virtual function exists in the partition] ********************
    changed: [127.0.0.1]

    TASK [Configure partition for booting via HBA] ****************************
    changed: [127.0.0.1]

    PLAY RECAP ****************************************************************
    127.0.0.1                  : ok=6    changed=5    unreachable=0    failed=0

    $ ansible-playbook delete_partition.yml

    PLAY [localhost] **********************************************************

    TASK [Gathering Facts] ****************************************************
    ok: [127.0.0.1]

    TASK [Ensure partition does not exist] ************************************
    changed: [127.0.0.1]

    PLAY RECAP ****************************************************************
    127.0.0.1                  : ok=2    changed=1    unreachable=0    failed=0


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

    $ git clone git@github.ibm.com:zhmcclient/zhmc-ansible-modules.git
    $ cd zhmc-ansible-modules
    $ workon {venv}
    $ pip install .
    $ pip show zhmc-ansible-modules | grep Location
    Location: /home/{user}/virtualenvs/{venv}/lib/python2.7/site-packages
    $ export ANSIBLE_LIBRARY=/home/{user}/virtualenvs/{venv}/lib/python2.7/site-packages/zhmc_ansible_modules
