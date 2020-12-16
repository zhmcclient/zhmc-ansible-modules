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


.. _`Development`:

Development
===========

This section only needs to be read by developers of this project. People that
want to make a fix or develop some extension, and people that want to test the
project are also considered developers for the purpose of this section.


.. _`Repository`:

Repository
----------

The repository for the **IBM Z HMC collection** is on GitHub:

https://github.com/zhmcclient/zhmc-ansible-modules


.. _`Setting up the development environment`:

Setting up the development environment
--------------------------------------

The development environment is pretty easy to set up.

Besides having a supported operating system with a supported Python version
(see :ref:`Supported environments`), it is recommended that you set up a
`virtual Python environment`_.

.. _virtual Python environment: http://docs.python-guide.org/en/latest/dev/virtualenvs/

Then, with a virtual Python environment active, clone the Git repo of this
project and prepare the development environment with ``make develop``:

.. code-block:: sh

    $ git clone git@github.com:zhmcclient/zhmc-ansible-modules.git
    $ cd zhmc-ansible-modules
    $ make develop

This will install all prerequisites the project needs for its development.

Generally, this project uses Make to do things in the currently active
Python environment. The command ``make help`` (or just ``make``) displays a
list of valid Make targets and a short description of what each target does.


.. _`Building the documentation`:

Building the documentation
--------------------------

The documentation for the **IBM Z HMC collection** is published
on GitHub Pages at https://zhmcclient.github.io/zhmc-ansible-modules/.

That web site represents a defined set of versions of this collection and
automatically gets updated whenever a pull request gets merged into the
repository branch that corresponds to the version. The automatic update
mechanism is implemented in the GitHub Actions workflow file
``.github/workflows/docs.yml``.

The versions to be represented on that site are defined in ``docs/source/conf.py``
in the section for "sphinx-versioning".

In order to build this "versioned" documentation locally, issue:

.. code-block:: sh

    $ make docs

The top-level document to open with a web browser will be
``docs_build/index.html``. Note that the versioned documentation is built from
the defined branches, so it does not include the content of your Git work
directory.

In order to see the effects of some change in your Git work directory, there
is a second documentation build that builds an "unversioned" documentation
from the content of your Git work directory:

.. code-block:: sh

    $ make docslocal

The top-level document to open with a web browser will be
``docs_local/index.html``; it is opened automatically when the documentation
has been built successfully.


.. _`Testing`:

Testing
-------

Again, an invocation of Make runs against the currently active Python environment.

There are four kinds of tests currently, available as make targets:

* ``make linkcheck`` - Check links in documentation
* ``make test`` - Run unit and function tests with test coverage
* ``make sanity`` - Run Ansible sanity tests (includes flake8, pylint, validate-modules)
* ``make end2end`` - Run end2end tests (against a real environment)

For the unit and function tests, the testcases and options for pytest
can be specified via the environment variable ``TESTOPTS``, as shown in these
examples:

.. code-block:: sh

    $ make test                                      # Run all unit and function tests
    $ TESTOPTS='-vv' make test                       # Specify -vv verbosity for pytest
    $ TESTOPTS='-k test_partition.py' make test      # Run only this test source file


.. _`Releasing a version`:

Releasing a version
-------------------

This section shows the steps for releasing a version to `Ansible Galaxy
<https://galaxy.ansible.com/>`_.

It covers all variants of versions that can be released:

* Releasing the master branch as a new major version (M+1.0.0)
* Releasing the master branch as a new minor version (M.N+1.0)
* Releasing a stable branch as a new update version (M.N.U+1)

This description assumes that you are authorized to push to the remote repo
at https://github.com/zhmcclient/zhmc-ansible-modules and that the remote repo
has the remote name ``origin`` in your local clone.

1.  Switch to your work directory of your local clone of the
    zhmc-ansible-modules Git repo and perform the following steps in that
    directory.

2.  Set shell variables for the version and branch that is being released:

    * ``MNU`` - Full version M.N.U that is being released
    * ``MN`` - Major and minor version M.N of that full version
    * ``BRANCH`` - Name of the branch that is being released

    When releasing the master branch (e.g. as version ``1.0.0``):

    .. code-block:: sh

        MNU=1.0.0
        MN=1.0
        BRANCH=master

    When releasing a stable branch (e.g. as version ``0.8.1``):

    .. code-block:: sh

        MNU=0.8.1
        MN=0.8
        BRANCH=stable_${MN}

3.  Check out the branch that is being released, make sure it is up to date with
    the remote repo, and create a topic branch for the version that is being
    released:

    .. code-block:: sh

        git status  # Double check the work directory is clean
        git checkout ${BRANCH}
        git pull
        git checkout -b release_${MNU}

4.  Edit the change log:

    .. code-block:: sh

        vi docs/source/release_notes.rst

    and make the following changes in the section of the version that is being
    released:

    * Finalize the version.
    * Change the release date to today's date.
    * Make sure that all changes are described.
    * Make sure the items shown in the change log are relevant for and
      understandable by users.
    * In the "Known issues" list item, remove the link to the issue tracker and
      add text for any known issues you want users to know about.
    * Remove all empty list items.

5.  Edit the Galaxy metadata file:

    .. code-block:: sh

        vi galaxy.yml

    and set the 'version' parameter to the version that is being released:

    .. code-block:: yaml

        version: M.N.U

6.  When releasing the master branch, edit the GitHub workflow file `test.yml`:

    .. code-block:: sh

        vi .github/workflows/test.yml

    and in the `on` section, increase the version of the stable branch to be
    the version that is being released:

    .. code-block:: yaml

        on:
          schedule:
            . . .
          push:
            branches: [ master, stable_M.N ]
          pull_request:
            branches: [ master, stable_M.N ]

7.  When releasing the master branch, edit the GitHub workflow file `docs.yml`:

    .. code-block:: sh

        vi .github/workflows/docs.yml

    and in the `on` section, increase the version of the stable branch to be
    the version that is being released:

    .. code-block:: yaml

        on:
          push:
            # PR merge to these branches triggers this workflow
            branches: [ master, stable_M.N ]

8.  Commit your changes and push them to the remote repo:

    .. code-block:: sh

        git status  # Double check the changed files
        git commit -asm "Release ${MNU}"
        git push --set-upstream origin release_${MNU}

9.  On GitHub, create a Pull Request for branch ``release_M.N.U``. This will
    trigger the CI runs.

    Important: When creating Pull Requests, GitHub by default targets the
    ``master`` branch. When releasing a stable branch, you need to change
    the target branch of the Pull Request to ``stable_M.N``.

10. On GitHub, close milestone ``M.N.U``.

11. Perform a complete test in your preferred Python environment:

    .. code-block:: sh

        make clobber all

    This should not fail because the same tests have already been run in the
    CI. However, run it for additional safety before the release.

    If this test fails, fix any issues (with new commits) until the test
    succeeds.

12. The items in this step should be performed within no more than
    1 minute, so that the documentation that is built uses the new tag.

    * Merge the Pull Request (no review is needed). This deletes the branch
      on GitHub and triggers a build of the documentation and subsequent
      publishng to Github pages.

    * Update the branch you are releasing and add a tag for the version to be
      released:

      .. code-block:: sh

          git checkout ${BRANCH}
          git pull
          git tag -f ${MNU}
          git push -f --tags

13. Delete the local branch:

    .. code-block:: sh

        git branch -d release_${MNU}

14. On GitHub, edit the new tag ``M.N.U``, and create a release description on
    it. This will cause it to appear in the Release tab.

    You can see the tags in GitHub via Code -> Releases -> Tags.

15. Publish the collection to Ansible Galaxy:

    You need to be registered on Ansible Galaxy, and your userid there needs to
    be authorized to modify the 'ibm' namespace.

    Look up your API Key on https://galaxy.ansible.com/me/preferences and upload
    to galaxy while the `GALAXY_TOKEN` environment variable is set to your API
    Key:

    .. code-block:: sh

        GALAXY_TOKEN={your-galaxy-api-key} make upload

    This will show the collection version and will ask for confirmation.

    **Important:** Double check that the correct package version (``M.N.U``,
    without any development suffix) is shown.

    **Attention!!** This only works once for each version. You cannot
    re-release the same version to Ansible Galaxy, or otherwise update it.

    Verify that the released version arrived on Ansible Galaxy at
    https://galaxy.ansible.com/ibm/ibm_zhmc/

16. When releasing the master branch, create a new stable branch and push it
    to the remote repo:

    .. code-block:: sh

        git checkout -b stable_${MN}
        git push --set-upstream origin stable_${MN}


.. _`Starting a new version`:

Starting a new version
----------------------

This section shows the steps for starting development of a new version.

These steps may be performed right after the steps for
:ref:`releasing a version`, or independently.

This section covers all variants of new versions:

* Starting a major or minor version based on the master branch.
* Starting an update version based on a stable branch.

This description assumes that you are authorized to push to the remote repo
at https://github.com/zhmcclient/zhmc-ansible-modules and that the remote repo
has the remote name ``origin`` in your local clone.

1.  Switch to your work directory of your local clone of the
    zhmc-ansible-modules Git repo and perform the following steps in that
    directory.

2.  Set shell variables for the version that is being started and the branch it
    is based on:

    * ``MNU`` - Full version M.N.U that is being started
    * ``MN`` - Major and minor version M.N of that full version
    * ``BRANCH`` - Name of the base branch for the version that is being started

    When starting a version based on the master branch (e.g. version `1.1.0`):

    .. code-block:: sh

        MNU=1.1.0
        MN=1.0
        BRANCH=master

    When starting a version based on a stable branch (e.g. version `0.8.2`):

    .. code-block:: sh

        MNU=0.8.2
        MN=0.8
        BRANCH=stable_${MN}

3.  Check out the base branch for the version that is being started, make sure
    it is up to date with the remte repo, and create a topic branch for the new
    version:

    .. code-block:: sh

        git status  # Double check the work directory is clean
        git checkout ${BRANCH}
        git pull
        git checkout -b start_${MNU}

4.  Edit the change log:

    .. code-block:: sh

        vi docs/source/release_notes.rst

    and insert the following section before the top-most section, and update
    the version to a draft version of the version that is being started:

    .. code-block:: rst

        Version M.N.U-dev1
        ------------------

        This version contains all fixes up to version M.N-1.x.

        Released: not yet

        **Incompatible changes:**

        **Deprecations:**

        **Bug fixes:**

        **Enhancements:**

        **Cleanup:**

        **Known issues:**

        * See `list of open issues`_.

        .. _`list of open issues`: https://github.com/zhmcclient/zhmc-ansible-modules/issues

5.  Edit the Galaxy metadata file:

    .. code-block:: sh

        vi galaxy.yml

    and update the version to a draft version of the version that is being
    started:

    .. code-block:: yaml

        version: M.N.U-dev1

    Note: The version must follow the rules for semantic versioning 2.0
    including the description of development/alpha/etc suffixes, as described
    in https://semver.org/

6.  Commit your changes and push them to the remote repo:

    .. code-block:: sh

        git status  # Double check the changed files
        git commit -asm "Start ${MNU}"
        git push --set-upstream origin start_${MNU}

7.  On GitHub, create a Pull Request for branch ``start_M.N.U``.

    Important: When creating Pull Requests, GitHub by default targets the
    ``master`` branch. When starting a version based on a stable branch, you
    need to change the target branch of the Pull Request to ``stable_M.N``.

8.  On GitHub, create a milestone for the new version ``M.N.U``.

    You can create a milestone in GitHub via Issues -> Milestones -> New
    Milestone.

9.  On GitHub, go through all open issues and pull requests that still have
    milestones for previous releases set, and either set them to the new
    milestone, or to have no milestone.

10. On GitHub, once the checks for this Pull Request succeed:

    * Merge the Pull Request (no review is needed). This deletes the branch
      on GitHub.

11. Checkout the base branch for the version that is being started, update it
    from remote, and delete the local topic branch you created:

    .. code-block:: sh

        git checkout ${BRANCH}
        git pull
        git branch -d start_${MNU}
