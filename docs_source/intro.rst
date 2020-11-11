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

.. _`Introduction`:

Introduction
============


.. _`What this package provides`:

What this package provides
--------------------------

The `ibm.zhmc collection on Galaxy`_ provides Ansible modules that
can manage platform resources on `IBM Z`_ and `LinuxONE`_ machines.

The goal of this collection is to be able to utilize the power and ease of use
of Ansible for the management of IBM Z platform resources.

The IBM Z resources that can be managed include for example partitions, adapters,
the Z system itself, or various resources on its Hardware Management Console
(HMC).

The Ansible modules in this collection are fully
`idempotent <http://docs.ansible.com/ansible/latest/glossary.html#term-idempotency>`_,
following an important principle for Ansible modules.
The idempotency of a module allows Ansible playbooks to specify the desired end
state for a resource, regardless of what the current state is. For example, an
IBM Z partition can be specified to have ``state=active`` which means that
it must exist and be in the active operational status. Depending on the current
state of the partition, actions will be taken by the module to reach this
desired end state: If the partition does not exist, it will be created and
started. If it exists but is not active, it will be started. If it is already
active, nothing will be done. Other initial states including transitional
states such as starting or stopping also will be taken care of.
The idempotency of modules makes Ansible playbooks restartable: If an error
happens and some things have been changed already, the playbook can simply be
re-run and will automatically do the right thing, because the initial state
does not matter for reaching the desired end state.

The Ansible modules in this collection are written in Python
and interact with the Web Services API of the Hardware Management Console (HMC)
of the machines to be managed, by using the API of the `zhmcclient`_ Python
package.

Note: Before version 1.0.0, the Ansible modules in this collection have been
distributed as the `zhmc-ansible-modules package on Pypi`_.
Starting with version 1.0.0, the Ansible modules are no longer distributed on
Pypi, but as the `ibm.zhmc collection on Galaxy`_.

.. _ibm.zhmc collection on Galaxy: https://galaxy.ansible.com/ibm/zhmc/
.. _zhmc-ansible-modules package on Pypi: https://pypi.org/project/zhmc-ansible-modules/
.. _Ansible: https://www.ansible.com/
.. _Galaxy: https://galaxy.ansible.com/
.. _IBM Z: http://www.ibm.com/systems/z/
.. _LinuxONE: http://www.ibm.com/systems/linuxone/
.. _zhmcclient: http://python-zhmcclient.readthedocs.io/en/stable/


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


.. _`Installation`:

Installation
------------

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All commands shown are to be executed in a terminal or command prompt on the
control system. The instructions are written for a bash shell.

.. _`Installing the Control Machine`: http://docs.ansible.com/ansible/latest/intro_installation.html#installing-the-control-machine


1.  Install Ansible as an operating system package on the control system.

    For details, see `Installing the Control Machine`_.

2.  Install the ibm.zhmc Ansible Galaxy collection:

    .. code-block:: bash

        $ ansible-galaxy collection install ibm.zhmc

    This will install the collection to your local Ansible collections tree,
    which is by default ``$HOME/.ansible/collections/ansible_collections``.
    It does not install any dependent Python packages.

3.  Install the dependent Python packages into your system Python:

    Double check where the ibm.zhmc Ansible Galaxy collection got installed:

    .. code-block:: bash

        $ ansible-galaxy collection list ibm.zhmc
        # /Users/johndoe/.ansible/collections/ansible_collections
        Collection Version
        ---------- -------
        ibm.zhmc   1.0.0

        $ anco_dir=/Users/johndoe/.ansible/collections/ansible_collections

    Using the provided requirements.txt file in the installation of the
    ibm.zhmc Ansible Galaxy collection, install dependent Python packages
    into your system Python:

    .. code-block:: bash

        $ sudo pip install -r $anco_dir/ibm/zhmc/requirements.txt


Alternative installation with virtual Python environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

    .. code-block:: bash

        $ mkvirtualenv myenv

    Note: Using the command shown requires the ``virtualenvwrapper`` package.

    For details, see `virtualenv`_.

2.  Install Ansible as a Python package on the control system:

    .. code-block:: bash

        $ pip install ansible

    This will install Ansible into the active Python, i.e. into the virtual
    Python environment. Note that an OS-level Ansible and a Python-level
    Ansible have shared configuration files, e.g. in ``/etc/ansible``.

3.  Create a shell script that invokes the active Python.

    Adjust the file name and path for the shell script in the ``python_script``
    variable as needed, the only requirement is that the shell script must be
    found in the PATH:

    .. code-block:: bash

        $ python_script=$HOME/local/bin/env_python

        $ cat >$python_script <<'EOT'
        #!/bin/bash
        py=$(which python)
        $py "$@"
        EOT

        $ chmod 755 $python_script

4.  Configure Ansible to invoke Python via the new shell script (using the
    ``python_script`` variable from the previous step):

    .. code-block:: bash

        $ sudo tee -a /etc/ansible/hosts >/dev/null <<EOT
        [local:vars]
        ansible_python_interpreter=$python_script
        EOT

5.  Install the ibm.zhmc Ansible Galaxy collection:

    .. code-block:: bash

        $ ansible-galaxy collection install ibm.zhmc

    This will install the collection to your local Ansible collections tree,
    which is by default ``$HOME/.ansible/collections/ansible_collections``.
    It does not install any dependent Python packages.

6.  Install the dependent Python packages into the active Python:

    Double check where the ibm.zhmc Ansible Galaxy collection got installed:

    .. code-block:: bash

        $ ansible-galaxy collection list ibm.zhmc
        # /Users/johndoe/.ansible/collections/ansible_collections
        Collection Version
        ---------- -------
        ibm.zhmc   1.0.0

        $ anco_dir=/Users/johndoe/.ansible/collections/ansible_collections

    Using the provided requirements.txt file in the installation of the
    ibm.zhmc Ansible Galaxy collection, install dependent Python packages
    into your system Python:

    .. code-block:: bash

        $ sudo pip install -r $anco_dir/ibm/zhmc/requirements.txt


Verification of the installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can verify that the ibm.zhmc Ansible Galaxy collection and its dependent
Python packages are installed correctly by running an example playbook in
check mode:

.. code-block:: bash

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


.. _`Example playbooks`:

Example playbooks
-----------------

After having installed the ibm.zhmc Ansible Galaxy collection, you find the
example playbooks in folder ``ibm/zhmc/playbooks/`` of your local Ansible
collection directory (e.g. ``$HOME/.ansible/collections/ansible_collections/``),
for example:

* ``create_partition.yml`` creates a partition with a NIC, HBA and virtual
  function to an accelerator adapter.

* ``delete_partition.yml`` deletes a partition.

These example playbooks include two other files for defining credentials and
other variables:

* ``vars.yml`` defines variables such as CPC name, partition name, etc. It does
  not exist in that directory but can be copied from ``vars_example.yml``,
  changing the variables to your needs.

* ``vault.yml`` is a password vault file defining variables for authenticating
  with the HMC. It does not exist in that directory but can be copied from
  ``vault_example.yml``, changing the variables to your needs.

Then, run the playbooks:

.. code-block:: text

    $ ansible-playbook $anco_dir/ibm/zhmc/playbooks/create_partition.yml

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

    $ ansible-playbook $anco_dir/ibm/zhmc/playbooks/delete_partition.yml

    PLAY [localhost] **********************************************************

    TASK [Gathering Facts] ****************************************************
    ok: [127.0.0.1]

    TASK [Ensure partition does not exist] ************************************
    changed: [127.0.0.1]

    PLAY RECAP ****************************************************************
    127.0.0.1                  : ok=2    changed=1    unreachable=0    failed=0


.. _`Versioning`:

Versioning
----------

This documentation applies to version |release| of the ibm.zhmc
Ansible Galaxy collection.

This collection uses the rules of `Semantic Versioning 2.0.0`_ for its version.

.. _Semantic Versioning 2.0.0: http://semver.org/spec/v2.0.0.html

This documentation may have been built from a development level of the
package. You can recognize a development version of this package by the
presence of a ".devD" suffix in the version string.


.. _`Compatibility`:

Compatibility
-------------

For Ansible modules, compatibility is always seen from the perspective of an
Ansible playbook using it. Thus, a backwards compatible new version of an
Ansible Galaxy collection means that the user can safely upgrade to that new
version without encountering compatibility issues in any Ansible playbooks
using the modules in the collection.

This collection uses the rules of `Semantic Versioning 2.0.0`_ for compatibility
between package versions, and for :ref:`deprecations <Deprecations>`.

The public interface of the collection that is subject to the semantic
versioning rules (and specificically to its compatibility rules) are the Ansible
module interfaces described in this documentation.

Violations of these compatibility rules are described in section
:ref:`Change log`.


.. _`Deprecations`:

Deprecations
------------

Deprecated functionality is marked accordingly in this documentation and in the
:ref:`Change log`.


.. _`Reporting issues`:

Reporting issues
----------------

If you encounter any problem with this collection, or if you have questions of
any kind related to this collection (even when they are not about a problem),
please open an issue in the `ibm.zhmc collection issue tracker`_.

.. _`ibm.zhmc collection issue tracker`: https://github.com/zhmcclient/zhmc-ansible-modules/issues


.. _`License`:

License
-------

This package is licensed under the `Apache 2.0 License`_.

.. _Apache 2.0 License: https://raw.githubusercontent.com/zhmcclient/zhmc-ansible-modules/master/LICENSE
