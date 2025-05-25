.. Copyright 2017,2020 IBM Corp. All Rights Reserved.
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

.. _`virtual Python environment`: https://docs.python-guide.org/dev/virtualenvs/

The following sections describe these two installation methods.


Standard installation with system Python
----------------------------------------

All commands shown are to be executed in a terminal or command prompt on the
control system. The instructions are written for a bash shell.

.. _`Installing Ansible on specific operating systems`: https://docs.ansible.com/ansible/latest/installation_guide/installation_distros.html

1.  Install Ansible as an operating system package on the control system.

    For details, see `Installing Ansible on specific operating systems`_.

2.  Install the **IBM Z HMC collection** from Ansible Galaxy:

    .. code-block:: sh

        $ ansible-galaxy collection install ibm.ibm_zhmc

    This will install the collection to your local Ansible collections tree,
    which is by default ``$HOME/.ansible/collections/ansible_collections``.
    It does not install any dependent Python packages.

3.  Install the dependent Python packages into your system Python:

    Double check where the ``ibm.ibm_zhmc`` collection got installed:

    .. code-block:: sh

        $ ansible-galaxy collection list ibm.ibm_zhmc
        # /Users/johndoe/.ansible/collections/ansible_collections
        Collection   Version
        ------------ -------
        ibm.ibm_zhmc 1.0.0

    Set a variable to the installation directory shown in the command output:

    .. code-block:: sh

        $ anco_dir=/Users/johndoe/.ansible/collections/ansible_collections

    Using the ``requirements.txt`` file in the installation directory of the
    ``ibm.ibm_zhmc`` collection, install dependent Python packages into your
    system Python:

    .. code-block:: sh

        $ sudo pip install -r $anco_dir/ibm/ibm_zhmc/requirements.txt


Alternative installation with virtual Python environment
--------------------------------------------------------

.. _virtualenv: https://virtualenv.pypa.io/

This section describes the installation of Ansible and the ibm.ibm_zhmc Ansible
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

        $ cat >$python_script \<\<'EOT'
        #!/bin/bash
        py=$(which python)
        $py "$@"
        EOT

        $ chmod 755 $python_script

4.  Configure Ansible to invoke Python via the new shell script (using the
    ``python_script`` variable from the previous step):

    .. code-block:: sh

        $ sudo tee -a /etc/ansible/hosts >/dev/null \<\<EOT
        [local:vars]
        ansible_python_interpreter=$python_script
        EOT

5.  Install the **IBM Z HMC collection** from Ansible Galaxy:

    .. code-block:: sh

        $ ansible-galaxy collection install ibm.ibm_zhmc

    This will install the collection to your local Ansible collections tree,
    which is by default ``$HOME/.ansible/collections/ansible_collections``.
    It does not install any dependent Python packages.

6.  Install the dependent Python packages into the active Python:

    Double check where the ``ibm.ibm_zhmc`` collection got installed:

    .. code-block:: sh

        $ ansible-galaxy collection list ibm.ibm_zhmc
        # /Users/johndoe/.ansible/collections/ansible_collections
        Collection   Version
        ------------ -------
        ibm.ibm_zhmc 1.0.0

    Set a variable to the installation directory shown in the command output:

    .. code-block:: sh

        $ anco_dir=/Users/johndoe/.ansible/collections/ansible_collections

    Using the ``requirements.txt`` file in the installation directory of the
    ``ibm.ibm_zhmc`` collection, install dependent Python packages into your
    active Python:

    .. code-block:: sh

        $ pip install -r $anco_dir/ibm/ibm_zhmc/requirements.txt


Installing a development version
--------------------------------

This section describes how to install a development version of the
ibm.ibm_zhmc collection. Because the procedure installs the Python packages
needed for the collection using "pip", it is recommended to do that in a virtual
Python environment.

Follow the steps described for the alternative installation into a virtual
Python environment until step 4 and then perform these remaining steps:

5.  Clone the repo and checkout the desired branch:

    .. code-block:: sh

        $ git clone https://github.com/zhmcclient/zhmc-ansible-modules
        $ cd zhmc-ansible-modules
        $ git checkout master   # or your desired branch

6.  Build and install the collection:

    .. code-block:: sh

        $ make install

    This make command will build the collection from the checked out branch,
    install the collection to your local Ansible collections tree
    (which is by default ``$HOME/.ansible/collections/ansible_collections``),
    and install any dependent Python packages into the active Python
    environment using ``pip``.


.. _`Setting up the HMC`:

Setting up the HMC
------------------

Usage of this collection requires that the HMC in question is prepared
accordingly:

* The Web Services API must be enabled on the HMC.

  You can do that in the HMC GUI by selecting "HMC Management" in the left pane,
  then opening the "Configure API Settings" icon on the pain pane,
  then selecting the "Web Services" tab on the page that comes up, and
  finally enabling the Web Services API on that page.

  The above is on a z16 HMC, it may be different on older HMCs.

  If you cannot find this icon, then your userid does not have permission
  for the respective task on the HMC. In that case, there should be some
  other HMC admin you can go to to get the Web Services API enabled.


.. _`HMC userid requirements`:

HMC userid requirements
-----------------------

The HMC userid used for running the modules of this collection must have the
following task permissions:

  * Use of the Web Services API

The HMC userid used for running the modules of this collection must in
addition have the permissions documented in the description of each module
(see :ref:`Modules`). These descriptions document the complete set of
permissions needed for all operations of the module.


.. _`Setting up firewalls or proxies`:

Setting up firewalls or proxies
-------------------------------

If you have to configure firewalls or proxies between the system where you
run the ``zhmc_prometheus_exporter`` command and the HMC, the following ports
need to be opened:

* 6794 (TCP) - for the HMC API HTTP server
* 61612 (TCP) - for the HMC API message broker via JMS over STOMP

For details, see sections "Connecting to the API HTTP server" and
"Connecting to the API message broker" in the :ref:`HMC API <HMC API>` book.


.. _`Supported environments`:

Supported environments
----------------------

The following Z and LinuxONE machine generations are supported by the IBM Z HMC
collection:

- z196 / z114
- zEC12 / zBC12
- z13 / z13s / Emperor / Rockhopper
- z14 / Emperor II / Rockhopper II
- z15 / LinuxONE III
- z16 / LinuxONE 4


.. _`Support matrix`:

Support matrix
--------------

The following table shows for each released version of the IBM Z HMC collection
the Ansible and ansible-core versions supported on the control node, the
supported Z HMC versions and the support timeframe.

The general strategy is to support the latest released minor version until the
next minor version is released. See :ref:`Compatibility` for the rules this
collection applies regarding compatibility.

+------------+-----------+--------------+------------+-------------+-------------+
| Collection | Ansible   | ansible-core | Z HMC      | GA          | End of Life |
+============+===========+==============+============+=============+=============+
| 1.9.x      | >= 8.0.x  | >= 2.15.x    | >= 2.11    | 2024-07-18  |             |
+------------+-----------+--------------+------------+-------------+-------------+
| 1.8.x      | >= 8.0.x  | >= 2.15.x    | >= 2.11    | 2024-01-15  | 2024-07-18  |
+------------+-----------+--------------+------------+-------------+-------------+
| 1.7.x      | >= 7.0.x  | >= 2.14.x    | >= 2.11    | 2023-10-09  | 2024-01-15  |
+------------+-----------+--------------+------------+-------------+-------------+
| 1.6.x      | >= 2.9.x  | >= 2.9.x     | >= 2.11    | 2023-08-04  | 2023-10-09  |
+------------+-----------+--------------+------------+-------------+-------------+
| 1.5.x      | >= 2.9.x  | >= 2.9.x     | >= 2.11    | 2023-07-18  | 2023-08-04  |
+------------+-----------+--------------+------------+-------------+-------------+
| 1.4.x      | >= 2.9.x  | >= 2.9.x     | >= 2.11    | 2023-06-22  | 2023-07-18  |
+------------+-----------+--------------+------------+-------------+-------------+
| 1.3.x      | >= 2.9.x  | >= 2.9.x     | >= 2.11    | 2023-03-03  | 2023-06-22  |
+------------+-----------+--------------+------------+-------------+-------------+
| 1.2.x      | >= 2.9.x  | >= 2.9.x     | >= 2.11    | 2022-12-06  | 2023-03-03  |
+------------+-----------+--------------+------------+-------------+-------------+
| 1.1.x      | >= 2.9.x  | >= 2.9.x     | >= 2.11    | 2022-06-01  | 2022-12-06  |
+------------+-----------+--------------+------------+-------------+-------------+
| 1.0.x      | >= 2.9.x  | >= 2.9.x     | >= 2.11    | 2022-04-08  | 2022-06-01  |
+------------+-----------+--------------+------------+-------------+-------------+

The `Ansible-core Support Matrix <https://docs.ansible.com/ansible/latest/reference_appendices/release_and_maintenance.html#ansible-core-support-matrix>`_
shows for each ansible-core version the supported Python versions and the
support timeframe.

The `Red Hat Ansible Automation Platform Life Cycle <https://access.redhat.com/support/policy/updates/ansible-automation-platform>`_
shows for each AAP version the ansible-core version it includes and the
support timeframe.
