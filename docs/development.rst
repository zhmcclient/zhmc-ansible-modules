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

The repository for **IBM Z HMC Collection** is on GitHub:

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

.. code-block:: text

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

The documentation for **IBM Z HMC Collection** is published
on GitHub pages at https://zhmcclient.github.io/zhmc-ansible-modules/.

That page represents the ``master`` branch of the Git repo for this collection
and automatically gets updated whenever the ``master`` branch of the Git repo
changes.

In order to build the documentation locally from the Git work directory, issue:

.. code-block:: text

    $ make docs

The top-level document to open with a web browser will be ``docs/index.html``.


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

.. code-block:: text

    $ make test                                      # Run all unit and function tests
    $ TESTOPTS='-vv' make test                       # Specify -vv verbosity for pytest
    $ TESTOPTS='-k test_partition.py' make test      # Run only this test source file


.. _`Releasing a version`:

Releasing a version
-------------------

This section shows the steps for releasing a version to `Ansible Galaxy
<https://galaxy.ansible.com/>`_.

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

    When releasing the master branch (e.g. as version ``1.0.0``):

    .. code-block:: text

        MNU=1.0.0
        MN=1.0
        BRANCH=master

    When releasing a stable branch (e.g. as version ``0.8.1``):

    .. code-block:: text

        MNU=0.8.1
        MN=0.8
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

        vi docs_source/changes.rst

    and make the following changes in the section of the version to be released:

    * Finalize the version to the version to be released.
    * Change the release date to today's date.
    * Make sure that all changes are described.
    * Make sure the items shown in the change log are relevant for and understandable
      by users.
    * In the "Known issues" list item, remove the link to the issue tracker and
      add text for any known issues you want users to know about.
    * Remove all empty list items in the section of the version to be released.

5.  Edit the Galaxy metadata file:

    .. code-block:: text

        vi galaxy.yml

    and set the 'version' parameter to the version to be released:

    .. code-block:: text

        version: M.N.U

6.  Commit your changes and push them upstream:

    .. code-block:: text

        git add docs_source/changes.rst
        git commit -sm "Release $MNU"
        git push --set-upstream origin release_$MNU

7.  On GitHub, create a Pull Request for branch ``release_$MNU``. This will trigger the
    CI runs in Travis.

    Important: When creating Pull Requests, GitHub by default targets the ``master``
    branch. If you are releasing a stable branch, you need to change the target branch
    of the Pull Request to ``stable_M.N``.

8.  On GitHub, close milestone ``M.N.U``.

9.  Perform a complete test in your preferred Python environment:

    .. code-block:: text

        make clobber all

    This should not fail because the same tests have already been run in the
    Travis CI. However, run it for additional safety before the release.

    * If this test fails, fix any issues until the test succeeds. Commit the
      changes and push them upstream:

      .. code-block:: text

          git add <changed-files>
          git commit -sm "<change description with details>"
          git push

      Wait for the automatic tests to show success for this change.

10. On GitHub, once the checks for this Pull Request succeed:

    * Merge the Pull Request (no review is needed).

    * Delete the branch of the Pull Request (``release_M.N.U``)

11. Checkout the branch you are releasing, update it from upstream, and delete the local
    topic branch you created:

    .. code-block:: text

        git checkout $BRANCH
        git pull
        git branch -d release_$MNU

12. Tag the version:

    Create a tag for the new version and push the tag addition upstream:

    .. code-block:: text

        git status    # Double check the branch to be released is checked out
        git tag $MNU
        git push --tags

    If the previous commands fail because this tag already exists for some reason, delete
    the tag locally and remotely:

    .. code-block:: text

        git tag --delete $MNU
        git push --delete origin $MNU

    and try again.

13. On GitHub, edit the new tag ``M.N.U``, and create a release description on it. This
    will cause it to appear in the Release tab.

    You can see the tags in GitHub via Code -> Releases -> Tags.

14. Publish the collection to Ansible Galaxy:

    .. code-block:: text

        make upload

    This will show the package version and will ask for confirmation.

    **Important:** Double check that the correct package version (``M.N.U``,
    without any development suffix) is shown.

    **Attention!!** This only works once for each version. You cannot
    re-release the same version to Ansible Galaxy, or otherwise update it.

    Verify that the released version arrived on Ansible Galaxy at
    https://galaxy.ansible.com/ibm/zhmc/

15. If you released the master branch, it needs a new fix stream.

    Create a branch for its fix stream and push it upstream:

    .. code-block:: text

        git status    # Double check the branch to be released is checked out
        git checkout -b stable_$MN
        git push --set-upstream origin stable_$MN

    On GitHub, go to "Settings" and change the branch from which the Github
    pages are built, to ``stable_$MN``.

16. The final step of the version release process is to generate the documentation
    for the new version. For that please create a new branch, then add the newly
    created tag ``M.N.U`` into the ``scv_whitelist_tags`` list in conf.py (or
    replace one of the existing ones).
    Then execute the ``docs`` make target, check that the new tag is in the
    current version (bottom left part of the page) and create a PR with the new branch.
    Once the PR is merged, the docs on the GitHub pages will be updated to include
    the new version.
    **Attention!!** This section needs to be updated as soon as the gh-pages
    branch and the supporting process to release will be ready.

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

    When starting a (major or minor) version (e.g. ``1.1.0``) based on the master branch:

    .. code-block:: text

        MNU=1.1.0
        MN=1.0
        BRANCH=master

    When starting an update (=fix) version (e.g. ``0.8.2``) based on a stable branch:

    .. code-block:: text

        MNU=0.8.2
        MN=0.8
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

        vi docs_source/changes.rst

    and insert the following section before the top-most section:

    .. code-block:: text

        Version 1.1.0
        ^^^^^^^^^^^^^

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

    .. code-block:: text

        vi galaxy.yml

    and update the version to the new version plus '-dev1' to indicate it is in
    development:

    .. code-block:: text

        version: M.N.U-dev1

    Note: The version must follow the rules for semantic versioning 2.0 including
    the description of development/alpha/etc suffixes, as described in
    https://semver.org/

6.  Commit your changes and push them upstream:

    .. code-block:: text

        git add docs/changes.rst
        git commit -sm "Start $MNU"
        git push --set-upstream origin start_$MNU

7.  On GitHub, create a Pull Request for branch ``start_M.N.U``.

    Important: When creating Pull Requests, GitHub by default targets the ``master``
    branch. If you are starting based on a stable branch, you need to change the
    target branch of the Pull Request to ``stable_M.N``.

8.  On GitHub, create a milestone for the new version ``M.N.U``.

    You can create a milestone in GitHub via Issues -> Milestones -> New
    Milestone.

9.  On GitHub, go through all open issues and pull requests that still have
    milestones for previous releases set, and either set them to the new
    milestone, or to have no milestone.

10. On GitHub, once the checks for this Pull Request succeed:

    * Merge the Pull Request (no review is needed)
    * Delete the branch of the Pull Request (``start_M.N.U``)

11. Checkout the branch the new version is based on, update it from upstream, and
    delete the local topic branch you created:

    .. code-block:: text

        git checkout $BRANCH
        git pull
        git branch -d start_$MNU
