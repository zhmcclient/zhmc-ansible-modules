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


Releasing a version to PyPI
---------------------------

This section shows the steps for releasing a version to PyPI.

Switch to your work directory of the zhmc-ansible-modules Git repo (this is
where the ``Makefile`` is), and perform the following steps in that directory:

1.  Set a shell variable for the version to be released, e.g.:

    .. code-block:: text

        MNU='0.11.0'

2.  Verify that your working directory is in a Git-wise clean state:

    .. code-block:: text

        git status

3.  Check out the ``master`` branch, and update it from upstream:

    .. code-block:: text

        git checkout master
        git pull

4.  Create a topic branch for the release:

    .. code-block:: text

        git checkout -b release-$MNU
        git branch --set-upstream-to origin/release-$MNU release-$MNU

5.  Edit the change log (``docs/changes.rst``) and perform the following
    changes in the top-most section (that is the section for the version to be
    released):

    * If needed, change the version in the section heading to the version to be
      released, e.g.:

      .. code-block:: text

          Version 0.11.0
          ^^^^^^^^^^^^^^

    * Change the release date to today's date, e.g.:

      .. code-block:: text

          Released: 2017-03-16

    * Make sure that the change log entries reflect all changes since the
      previous version, and make sure they are relevant for and
      understandable by users.

    * In the "Known issues" list item, remove the link to the issue tracker
      and add any known issues you want users to know about. Just linking
      to the issue tracker quickly becomes incorrect for released versions:

      .. code-block:: text

          **Known issues:**

          * ....

    * Remove all empty list items in the change log section for this release.

6.  Commit your changes and push them upstream:

    .. code-block:: text

        git add docs/changes.rst
        git commit -sm "Updated change log for $MNU release."
        git push

7.  On GitHub, create a pull request for branch release-$MNU.

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

9.  Once the CI tests on GitHub are complete, merge the pull request.

10. Update your local ``master`` branch:

    .. code-block:: text

        git checkout master
        git pull

11. Tag the ``master`` branch with the release label and push the tag
    upstream:

    .. code-block:: text

        git tag $MNU
        git push --tags

12. On GitHub, edit the new tag, and create a release description on it. This
    will cause it to appear in the Release tab.

    You can see the tags in GitHub via Code -> Releases -> Tags.

13. Upload the package to PyPI:

    .. code-block:: text

        make upload

    This will show the package version and will ask for confirmation.

    **Attention!!** This only works once for each version. You cannot
    release the same version twice to PyPI.

14. Verify that the released version is shown on PyPI:

    https://pypi.python.org/pypi/zhmc-ansible-modules/

15. Verify that RTD shows the released version as its stable version:

    https://zhmc-ansible-modules.readthedocs.io/en/stable/intro.html#versioning

    Note: RTD builds the documentation automatically, but it may take a few
    minutes to do so.

16. On GitHub, close milestone `M.N.U`.


Starting a new release
----------------------

This section shows the steps for starting development of a new version.

These steps may be performed right after the steps for releasing to PyPI,
or independently.

This description works for releases that are direct successors of the previous
release. It does not cover starting a new version that is a fix release to a
version that was released earlier.

Switch to your work directory of the zhmc-ansible-modules Git repo (this is
where the ``Makefile`` is), and perform the following steps in that directory:

1.  Set a shell variable for the new version to be started:

    .. code-block:: text

        MNU='0.12.0'

2.  Verify that your working directory is in a git-wise clean state:

    .. code-block:: text

        git status

3.  Check out the ``master`` branch, and update it from upstream:

    .. code-block:: text

        git checkout master
        git pull

4.  Create a topic branch for the release:

    .. code-block:: text

        git checkout -b start-$MNU
        git branch --set-upstream-to origin/start-$MNU start-$MNU

5.  Edit the change log (``docs/changes.rst``) and insert the following section
    before the top-most section (which is the section about the latest released
    version):

    .. code-block:: text

        Version 0.12.0
        ^^^^^^^^^^^^^^

        Released: not yet

        **Incompatible changes:**

        **Deprecations:**

        **Bug fixes:**

        **Enhancements:**

        **Known issues:**

        * See `list of open issues`_.

        .. _`list of open issues`: https://github.com/zhmcclient/zhmc-ansible-modules/issues

6.  Commit your changes and push them upstream:

    .. code-block:: text

        git add docs/changes.rst
        git commit -sm "Started $MNU release."
        git push

7.  On GitHub, create a pull request for branch start-$MNU.

8.  On GitHub, create a new milestone for development of the next release,
    e.g. `M.N.U`.

    You can create a milestone in GitHub via Issues -> Milestones -> New
    Milestone.

9.  On GitHub, go through all open issues and pull requests that still have
    milestones for previous releases set, and either set them to the new
    milestone, or to have no milestone.

10. Once the CI tests on GitHub are complete, merge the pull request.

11. Update your local ``master`` branch:

    .. code-block:: text

        git checkout master
        git pull
