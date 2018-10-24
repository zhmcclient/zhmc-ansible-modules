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

.. _`Development`:

Development
===========

This section only needs to be read by developers of the zhmc-ansible-modules
project. People that want to make a fix or develop some extension, and people
that want to test the project are also considered developers for the purpose of
this section.


.. _`Repository`:

Repository
----------

The repository for the zhmc-ansible-modules project is on GitHub:

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
project and prepare the development environment with ``make setup``:

.. code-block:: text

    $ git clone git@github.com:zhmcclient/zhmc-ansible-modules.git
    $ cd zhmc-ansible-modules
    $ make setup

This will install all prerequisites the project needs for its development.

Generally, this project uses Make to do things in the currently active
Python environment. The command ``make help`` (or just ``make``) displays a
list of valid Make targets and a short description of what each target does.


.. _`Building the documentation`:

Building the documentation
--------------------------

The ReadTheDocs (RTD) site is used to publish the documentation for the
zhmc-ansible-modules project at http://zhmc-ansible-modules.readthedocs.io/

This page automatically gets updated whenever the ``master`` branch of the
Git repo for this package changes.

In order to build the documentation locally from the Git work directory, issue:

.. code-block:: text

    $ make docs

The top-level document to open with a web browser will be
``build/docs/html/index.html``.


.. _`Testing`:

Testing
-------

To run unit tests in the currently active Python environment, issue one of
these example variants of ``make test``:

.. code-block:: text

    $ make test                                  # Run all unit tests
    $ TESTCASES=test_resource.py make test       # Run only this test source file
    $ TESTCASES=TestInit make test               # Run only this test class
    $ TESTCASES="TestInit or TestSet" make test  # py.test -k expressions are possible

To run the unit tests and some more commands that verify the project is in good
shape in all supported Python environments, use Tox:

.. code-block:: text

    $ tox                              # Run all tests on all supported Python versions
    $ tox -e py27                      # Run all tests on Python 2.7
    $ tox -e py27 test_resource.py     # Run only this test source file on Python 2.7
    $ tox -e py27 TestInit             # Run only this test class on Python 2.7
    $ tox -e py27 TestInit or TestSet  # py.test -k expressions are possible

The positional arguments of the ``tox`` command are passed to ``py.test`` using
its ``-k`` option. Invoke ``py.test --help`` for details on the expression
syntax of its ``-k`` option.


.. _`Contributing`:

.. include:: CONTRIBUTING.rst


.. _`Releasing a version`:

Releasing a version
-------------------

This section shows the steps for releasing a version to `PyPI
<https://pypi.python.org/>`_.

It covers all variants of versions that can be released:

* Releasing the master branch as a new major or minor version (M+1.0.0 or M.N+1.0)
* Releasing a stable branch as a new update version (M.N.U+1)

This description assumes that you are authorized to push to the upstream repo
at https://github.com/zhmcclient/zhmc-ansible-modules and that the upstream repo
has the remote name ``origin`` in your local clone.

1.  Switch to your work directory of your local clone of the
    zhmc-ansible-modules Git repo and perform the following steps in that
    directory.

2.  Set shell variables for the version and branch to be released:

    * ``MNU`` - Full version number M.N.U this release should have
    * ``MN`` - Major and minor version numbers M.N of that full version
    * ``BRANCH`` - Name of the branch to be released

    When releasing the master branch (e.g. as version ``0.6.0``):

    .. code-block:: text

        MNU=0.6.0
        MN=0.6
        BRANCH=master

    When releasing a stable branch (e.g. as version ``0.5.1``):

    .. code-block:: text

        MNU=0.5.1
        MN=0.5
        BRANCH=stable_$MN

3.  Check out the branch to be released, make sure it is up to date with upstream, and
    create a topic branch for the version to be released:

    .. code-block:: text

        git status  # Double check the work directory is clean
        git checkout $BRANCH
        git pull
        git checkout -b release_$MNU

4.  Edit the change log:

    .. code-block:: text

        vi docs/changes.rst

    and make the following changes in the section of the version to be released:

    * Finalize the version to the version to be released.
    * Remove the statement that the version is in development.
    * Change the release date to today´s date.
    * Make sure that all changes are described.
    * Make sure the items shown in the change log are relevant for and understandable
      by users.
    * In the "Known issues" list item, remove the link to the issue tracker and add
      text for any known issues you want users to know about.
    * Remove all empty list items in that section.

5.  Commit your changes and push them upstream:

    .. code-block:: text

        git add docs/changes.rst
        git commit -sm "Release $MNU"
        git push --set-upstream origin release_$MNU

6.  On GitHub, create a Pull Request for branch ``release_$MNU``. This will trigger the
    CI runs in Travis and Appveyor.

    Important: When creating Pull Requests, GitHub by default targets the ``master``
    branch. If you are releasing a stable branch, you need to change the target branch
    of the Pull Request to ``stable_M.N``.

7.  On GitHub, close milestone ``M.N.U``.

8.  Perform a complete test:

    .. code-block:: text

        tox

    This should not fail because the same tests have already been run in the
    Travis CI. However, run it for additional safety before the release.

    * If this test fails, fix any issues until the test succeeds. Commit the
      changes and push them upstream:

      .. code-block:: text

          git add <changed-files>
          git commit -sm "<change description with details>"
          git push

      Wait for the automatic tests to show success for this change.

9.  On GitHub, once the checks for this Pull Request succeed:

    * Merge the Pull Request (no review is needed).

      Because this updates the ``stable_M.N`` branch, it triggers an RTD docs build of
      its stable version. However, because the git tag for this version is not assigned
      yet, this RTD build will show an incorrect version (a dev version based on the
      previous version tag). This will be fixed in a subsequent step.

    * Delete the branch of the Pull Request (``release_M.N.U``)

10. Checkout the branch you are releasing, update it from upstream, and delete the local
    topic branch you created:

    .. code-block:: text

        git checkout $BRANCH
        git pull
        git branch -d release_$MNU

11. Tag the version:

    Important: This is the basis on which 'pbr' determines the package version. The tag
    string must be exactly the version string ``M.N.U``.

    Create a tag for the new version and push the tag addition upstream:

    .. code-block:: text

        git status    # Double check the branch to be released is checked out
        git tag $MNU
        git push --tags

    The pushing of the tag triggers another RTD docs build of its stable version, this time
    with the correct version as defined in the tag.

    If the previous commands fail because this tag already exists for some reason, delete
    the tag locally and remotely:

    .. code-block:: text

        git tag --delete $MNU
        git push --delete origin $MNU

    and try again.

12. On RTD, verify that it shows the correct version for its stable version:

    RTD stable version: https://zhmc-ansible-modules.readthedocs.io/en/stable.

    If it does not, trigger a build of RTD version "stable" on the RTD project
    page:

    RTD build page: https://readthedocs.org/projects/zhmc-ansible-modules/builds/

    Once that build is complete, verify again.

13. On GitHub, edit the new tag ``M.N.U``, and create a release description on it. This
    will cause it to appear in the Release tab.

    You can see the tags in GitHub via Code -> Releases -> Tags.

14. Do a fresh install of this version in your active Python environment. This ensures
    that 'pbr' determines the correct version. Otherwise, it may determine some development
    version.

    .. code-block:: text

        make clobber install
        make help    # Double check that it shows version ``M.N.U``

15. Upload the package to PyPI:

    .. code-block:: text

        make upload

    This will show the package version and will ask for confirmation.

    **Important:** Double check that the correct package version (``M.N.U``,
    without any development suffix) is shown.

    **Attention!!** This only works once for each version. You cannot
    re-release the same version to PyPI, or otherwise update it.

    Verify that the released version arrived on PyPI:
    https://pypi.python.org/pypi/zhmc-ansible-modules/

16. If you released the master branch, it needs a new fix stream.

    Create a branch for its fix stream and push it upstream:

    .. code-block:: text

        git status    # Double check the branch to be released is checked out
        git checkout -b stable_$MN
        git push --set-upstream origin stable_$MN

    Log on to the
    `RTD project zhmc-ansible-modules <https://readthedocs.org/projects/zhmc-ansible-modules/versions>`_
    and activate the new version (=branch) ``stable_M.N`` as a version to be
    built.


.. _`Starting a new version`:

Starting a new version
----------------------

This section shows the steps for starting development of a new version.

These steps may be performed right after the steps for
:ref:`releasing a version`, or independently.

This section covers all variants of new versions:

* A new major or minor version for new development based upon the master branch.
* A new update (=fix) version based on a stable branch.

This description assumes that you are authorized to push to the upstream repo
at https://github.com/zhmcclient/zhmc-ansible-modules and that the upstream repo
has the remote name ``origin`` in your local clone.

1.  Switch to your work directory of your local clone of the zhmc-ansible-modules Git
    repo and perform the following steps in that directory.

2.  Set shell variables for the version to be started and its base branch:

    * ``MNU`` - Full version number M.N.U of the new version to be started
    * ``MN`` - Major and minor version numbers M.N of that full version
    * ``BRANCH`` - Name of the branch the new version is based upon

    When starting a (major or minor) version (e.g. ``0.6.0``) based on the master branch:

    .. code-block:: text

        MNU=0.6.0
        MN=0.6
        BRANCH=master

    When starting an update (=fix) version (e.g. ``0.5.1``) based on a stable branch:

    .. code-block:: text

        MNU=0.5.1
        MN=0.5
        BRANCH=stable_$MN

3.  Check out the branch the new version is based on, make sure it is up to
    date with upstream, and create a topic branch for the new version:

    .. code-block:: text

        git status  # Double check the work directory is clean
        git checkout $BRANCH
        git pull
        git checkout -b start_$MNU

4.  Edit the change log:

    .. code-block:: text

        vi docs/changes.rst

    and insert the following section before the top-most section:

    .. code-block:: text

        Version 0.6.0
        ^^^^^^^^^^^^^

        Released: not yet

        **Incompatible changes:**

        **Deprecations:**

        **Bug fixes:**

        **Enhancements:**

        **Known issues:**

        * See `list of open issues`_.

        .. _`list of open issues`: https://github.com/zhmcclient/zhmc-ansible-modules/issues

5.  Commit your changes and push them upstream:

    .. code-block:: text

        git add docs/changes.rst
        git commit -sm "Start $MNU"
        git push --set-upstream origin start_$MNU

6.  On GitHub, create a Pull Request for branch ``start_M.N.U``.

    Important: When creating Pull Requests, GitHub by default targets the ``master``
    branch. If you are starting based on a stable branch, you need to change the
    target branch of the Pull Request to ``stable_M.N``.

7.  On GitHub, create a milestone for the new version ``M.N.U``.

    You can create a milestone in GitHub via Issues -> Milestones -> New
    Milestone.

8.  On GitHub, go through all open issues and pull requests that still have
    milestones for previous releases set, and either set them to the new
    milestone, or to have no milestone.

9.  On GitHub, once the checks for this Pull Request succeed:

    * Merge the Pull Request (no review is needed)
    * Delete the branch of the Pull Request (``start_M.N.U``)

10. Checkout the branch the new version is based on, update it from upstream, and
    delete the local topic branch you created:

    .. code-block:: text

        git checkout $BRANCH
        git pull
        git branch -d start_$MNU
