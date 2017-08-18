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

.. _`Introduction`:

Introduction
============


.. _`What this package provides`:

What this package provides
--------------------------

The zhmc-ansible-modules Python package contains `Ansible`_ modules that can
manage platform resources on `IBM Z`_ and `LinuxONE`_ machines that are in
the Dynamic Partition Manager (DPM) operational mode.

The goal of this package is to be able to utilize the power and ease of use
of Ansible for the management of IBM Z platform resources.

The IBM Z resources that can be managed include Partitions, HBAs, NICs, and
Virtual Functions.

The Ansible modules in the zhmc-ansible-modules package are fully
`idempotent <http://docs.ansible.com/ansible/latest/glossary.html#term-idempotency>`_,
following an important principle for Ansible modules.

The idempotency of a module allows Ansible playbooks to specify the desired end
state for a resource, regardless of what the current state is. For example, a
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

The Ansible modules in the zhmc-ansible-modules package are written in Python
and interact with the Web Services API of the Hardware Management Console (HMC)
of the machines to be managed, by using the API of the `zhmcclient`_ Python
package.

.. _Ansible: https://www.ansible.com/
.. _IBM Z: http://www.ibm.com/systems/z/
.. _LinuxONE: http://www.ibm.com/systems/linuxone/
.. _zhmcclient: http://python-zhmcclient.readthedocs.io/en/stable/


.. _`Supported environments`:

Supported environments
----------------------

The Ansible modules in the zhmc-ansible-modules package are supported in these
environments:

* Ansible versions: 2.0 or higher

* Operating systems running Ansible: Linux, OS-X

* Machine generations: z13/z13s/Emperor/Rockhopper or higher


.. _`Installation`:

Installation
------------

The system Ansible is installed on is called the "control system". This is
where Ansible commands (such as ``ansible-playbook``) are invoked.

Ansible is written in Python and invokes Ansible modules always as executables,
even when they are also written in Python. Therefore, Ansible modules
implemented in Python are run as Python scripts and are not imported as Python
modules.

The standard installation is that Ansible is installed as an operating system
package and uses the existing system Python (version 2). The Ansible modules
then also use the system Python.

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

All commands shown are to be executed in a bash shell on the control system.

.. _`Installing the Control Machine`: http://docs.ansible.com/ansible/latest/intro_installation.html#installing-the-control-machine


1. Install Ansible as an operating system package on the control system.

   For details, see `Installing the Control Machine`_.

2. Install the zhmc-ansible-modules package into the system Python:

   .. code-block:: bash

      $ sudo pip install zhmc-ansible-modules

   This will also install its dependent Python packages.

3. Set up the Ansible module search path

   Find out the install location of the zhmc-ansible-modules package:

   .. code-block:: bash

      $ pip show zhmc-ansible-modules | grep Location
      Location: /usr/local/lib/python2.7/dist-packages

   The Ansible module search path is the ``zhmc_ansible_modules`` directory in
   the location shown:

   .. code-block:: text

      /usr/local/lib/python2.7/dist-packages/zhmc_ansible_modules

   Note that the Python package name is ``zhmc-ansible-modules`` while the
   package directory is ``zhmc_ansible_modules``.

   Set the Ansible module search path using one of these options:

   a) via the Ansible config file:

      Edit the Ansible config file ``/etc/ansible/ansible.cfg`` to contain the
      following line:

      .. code-block:: text

         library = /usr/local/lib/python2.7/dist-packages/zhmc_ansible_modules

   b) via an environment variable:

      Edit your ``~/.bashrc`` file to contain the following line:

      .. code-block:: text

         export ANSIBLE_LIBRARY=/usr/local/lib/python2.7/dist-packages/zhmc_ansible_modules

      and source the file to set it in your current shell:

      .. code-block:: bash

         $ . ~/.bashrc


Alternative installation with virtual Python environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _virtualenv: https://virtualenv.pypa.io/

This section describes the installation of Ansible and the Ansible modules in
the zhmc-ansible-modules package into a virtual Python environment that is set
up using `virtualenv`_.

This installation method utilizes the ability of Ansible to configure the
Python environment it uses, and configures it to use the active Python (which
can be a virtual Python environment or the system Python).

All commands shown are to be executed in a bash shell on the control system.

1. Install Ansible as an operating system package on the control system.

   For details, see `Installing the Control Machine`_.

2. Create a shell script that invokes the active Python.

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

3. Configure Ansible to invoke Python via the new shell script (using the
   ``python_script`` variable from the previous step):

   .. code-block:: bash

      $ sudo tee -a /etc/ansible/hosts >/dev/null <<EOT
      [local:vars]
      ansible_python_interpreter=$python_script
      EOT

4. Create a shell script that sets the ``ANSIBLE_LIBRARY`` environment
   variable to the location of the zhmc-ansible-modules package found in the
   active Python environment.

   Adjust the file name and path for the shell script in the ``library_script``
   variable as needed, the only requirement is that the shell script must be
   found in the PATH:

   .. code-block:: bash

      $ library_script=$HOME/local/bin/setup_ansible_library

      $ cat >$library_script <<'EOT'
      #!/bin/bash
      zhmc_dir=$(dirname $(python -c "import zhmc_ansible_modules as m; print(m.__file__)"))
      export ANSIBLE_LIBRARY=$zhmc_dir
      EOT

      $ chmod 755 $library_script

5. Create a virtual Python environment for Python 2.7 and activate it.

   .. code-block:: bash

      $ mkvirtualenv myenv

   Note: Using the command shown requires the ``virtualenvwrapper`` package.

6. Install the zhmc-ansible-modules Python package into the active virtual
   Python environment:

   .. code-block:: bash

      (myenv)$ pip install zhmc-ansible-modules

   This will also install its dependent Python packages.

5. Set the ANSIBLE_LIBRARY environment variable by sourcing the script created
   in step 4:

   .. code-block:: bash

      $ . setup_ansible_library

   This must be done after each switch (or deactivation) of the active Python
   environment and before any Ansible command (that uses these modules) is
   invoked.


Verification of the installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can verify that the zhmc-ansible-modules package and its dependent packages
are installed correctly by running an example playbook in check mode:

.. code-block:: bash

    $ ansible-playbook playbooks/create_partition.yml --check

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

After having installed the zhmc-ansible-modules package, you can download and
run the example playbooks in `folder ``playbooks`` of the Git repository
<https://github.com/zhmcclient/zhmc-ansible-modules/tree/master/playbooks>`_:

* ``create_partition.yml`` creates a partition with a NIC, HBA and virtual
  function to an accelerator adapter.

* ``delete_partition.yml`` deletes a partition.

* ``vars_example.yml`` is an example variable file defining variables such as
  CPC name, partition name, etc.

* ``vault_example.yml`` is an example password vault file defining variables
  for authenticating with the HMC.

Before you run a playbook, copy ``vars_example.yml`` to ``vars.yml`` and
``vault_example.yml`` to ``vault.yml`` and change the variables in those files
as needed.

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


.. _`Versioning`:

Versioning
----------

This documentation applies to version |release| of the zhmc-ansible-modules
package. You can also see that version in the top left corner of this page.

The zhmc-ansible-modules package uses the rules of `Semantic Versioning 2.0.0`_
for its version.

.. _Semantic Versioning 2.0.0: http://semver.org/spec/v2.0.0.html

This documentation may have been built from a development level of the
package. You can recognize a development version of this package by the
presence of a ".devD" suffix in the version string.


.. _`Compatibility`:

Compatibility
-------------

For Ansible modules, compatibility is always seen from the perspective of an
Ansible playbook using it. Thus, a backwards compatible new version of the
zhmc-ansible-modules package means that the user can safely upgrade to that new
version without encountering compatibility issues in any Ansible playbooks
using these modules.

This package uses the rules of `Semantic Versioning 2.0.0`_ for compatibility
between package versions, and for :ref:`deprecations <Deprecations>`.

The public interface of this package that is subject to the semantic versioning
rules (and specificically to its compatibility rules) are the Ansible module
interfaces described in this documentation.

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

If you encounter any problem with this package, or if you have questions of any
kind related to this package (even when they are not about a problem), please
open an issue in the `zhmc-ansible-modules issue tracker`_.

.. _`zhmc-ansible-modules issue tracker`: https://github.com/zhmcclient/zhmc-ansible-modules/issues


.. _`License`:

License
-------

This package is licensed under the `Apache 2.0 License`_.

.. _Apache 2.0 License: https://raw.githubusercontent.com/zhmcclient/zhmc-ansible-modules/master/LICENSE
