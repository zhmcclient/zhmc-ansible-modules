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


.. _`Installation`:

Installation
============

The system Ansible is installed on is called the "control system". This is
where Ansible commands (such as ``ansible-playbook``) are invoked.

Ansible is written in Python but invokes Ansible modules always as executables,
even when they are also written in Python. Therefore, Ansible modules
implemented in Python are run as Python scripts and are not imported as Python
modules.

The standard installation is that Ansible is installed as an operating system
package and uses the existing system Python. The Ansible modules then also use
the system Python.

As an alternative to the standard installation, it is possible to use a
`virtual Python environment`_ for Ansible itself and for Ansible modules
written in Python. Using a virtual Python environment has the main advantages
that it minimizes the risk of incompatibilities between Python packages because
the virtual environment contains only the packages that are needed for the
specific use case, and that it does not pollute your system Python installation
with other Python packages, keeping the risk of incompatibilities away from
your system Python.

.. _`virtual Python environment`: http://docs.python-guide.org/en/latest/dev/virtualenvs/

The following sections describe these two installation methods.


Standard installation with system Python
----------------------------------------

All commands shown are to be executed in a terminal or command prompt on the
control system. The instructions are written for a bash shell.

.. _`Installing the Control Machine`: http://docs.ansible.com/ansible/latest/intro_installation.html#installing-the-control-machine


1.  Install Ansible as an operating system package on the control system.

    For details, see `Installing the Control Machine`_.

2.  Install the ``ibm.zhmc`` collection from Ansible Galaxy:

    .. code-block:: sh

        $ ansible-galaxy collection install ibm.zhmc

    This will install the collection to your local Ansible collections tree,
    which is by default ``$HOME/.ansible/collections/ansible_collections``.
    It does not install any dependent Python packages.

3.  Install the dependent Python packages into your system Python:

    Double check where the ``ibm.zhmc`` collection got installed:

    .. code-block:: sh

        $ ansible-galaxy collection list ibm.zhmc
        # /Users/johndoe/.ansible/collections/ansible_collections
        Collection Version
        ---------- -------
        ibm.zhmc   1.0.0

    Set a variable to the installation directory shown in the command output:

    .. code-block:: sh

        $ anco_dir=/Users/johndoe/.ansible/collections/ansible_collections

    Using the ``requirements.txt`` file in the installation directory of the
    ``ibm.zhmc`` collection, install dependent Python packages into your
    system Python:

    .. code-block:: sh

        $ sudo pip install -r $anco_dir/ibm/zhmc/requirements.txt


Alternative installation with virtual Python environment
--------------------------------------------------------

.. _virtualenv: https://virtualenv.pypa.io/

This section describes the installation of Ansible and the ibm.zhmc Ansible
Galaxy collection into a virtual Python environment that is set
up using `virtualenv`_.

This installation method utilizes the ability of Ansible to configure the
Python environment it uses, and configures it to use the active Python (which
can be a virtual Python environment or the system Python).

All commands shown are to be executed in a terminal or command prompt on the
control system. The instructions are written for a bash shell.

1.  Create a virtual Python environment and activate it:

    .. code-block:: sh

        $ mkvirtualenv myenv

    Note: Using the command shown requires the ``virtualenvwrapper`` package.

    For details, see `virtualenv`_.

2.  Install Ansible as a Python package on the control system:

    .. code-block:: sh

        $ pip install ansible

    This will install Ansible into the active Python, i.e. into the virtual
    Python environment. Note that an OS-level Ansible and a Python-level
    Ansible have shared configuration files, e.g. in ``/etc/ansible``.

3.  Create a shell script that invokes the active Python.

    Adjust the file name and path for the shell script in the ``python_script``
    variable as needed, the only requirement is that the shell script must be
    found in the PATH:

    .. code-block:: sh

        $ python_script=$HOME/local/bin/env_python

        $ cat >$python_script <<'EOT'
        #!/bin/bash
        py=$(which python)
        $py "$@"
        EOT

        $ chmod 755 $python_script

4.  Configure Ansible to invoke Python via the new shell script (using the
    ``python_script`` variable from the previous step):

    .. code-block:: sh

        $ sudo tee -a /etc/ansible/hosts >/dev/null <<EOT
        [local:vars]
        ansible_python_interpreter=$python_script
        EOT

5.  Install the ``ibm.zhmc`` collection from Ansible Galaxy:

    .. code-block:: sh

        $ ansible-galaxy collection install ibm.zhmc

    This will install the collection to your local Ansible collections tree,
    which is by default ``$HOME/.ansible/collections/ansible_collections``.
    It does not install any dependent Python packages.

6.  Install the dependent Python packages into the active Python:

    Double check where the ``ibm.zhmc`` collection got installed:

    .. code-block:: sh

        $ ansible-galaxy collection list ibm.zhmc
        # /Users/johndoe/.ansible/collections/ansible_collections
        Collection Version
        ---------- -------
        ibm.zhmc   1.0.0

    Set a variable to the installation directory shown in the command output:

    .. code-block:: sh

        $ anco_dir=/Users/johndoe/.ansible/collections/ansible_collections

    Using the ``requirements.txt`` file in the installation directory of the
    ``ibm.zhmc`` collection, install dependent Python packages into your
    active Python:

    .. code-block:: sh

        $ pip install -r $anco_dir/ibm/zhmc/requirements.txt


Verification of the installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can verify that **IBM Z HMC Collection** and its dependent
Python packages are installed correctly by running an example playbook in
check mode:

.. code-block:: sh

    $ ansible-playbook $anco_dir/ibm/zhmc/playbooks/create_partition.yml --check

    PLAY [localhost] ***********************************************************

    TASK [Gathering Facts] *****************************************************
    ok: [127.0.0.1]

    TASK [Ensure partition exists and is stopped] ******************************
    changed: [127.0.0.1]

    TASK [Ensure HBA exists in the partition] **********************************
    changed: [127.0.0.1]

    TASK [Ensure NIC exists in the partition] **********************************
    changed: [127.0.0.1]

    TASK [Ensure virtual function exists in the partition] *********************
    changed: [127.0.0.1]

    TASK [Configure partition for booting via HBA] *****************************
    changed: [127.0.0.1]

    PLAY RECAP *****************************************************************
    127.0.0.1                  : ok=6    changed=5    unreachable=0    failed=0


.. _`Supported environments`:

Supported environments
----------------------

The following versions of Python are currently supported:

- Python 2.7
- Python 3.5
- Python 3.6
- Python 3.7
- Python 3.8
- Python 3.9

Higher versions of Python 3.x have not been tested at this point, but are
expected to work.

The following operating systems are supported:

- Linux
- macOS (OS-X)
- Windows

The following versions of Ansible are supported:

- Ansible 2.9
- Ansible 2.10

The following Z and LinuxONE machine generations are supported:

- z13 / z13s / Emperor / Rockhopper
- z14 / Emperor II / Rockhopper II
- z15 / LinuxONE III
