# Copyright 2020,2026 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Script that prints the collection version based on git tags.

If the 'git' module cannot be imported, the script falls back to printing the
version defined in the galaxy.yml file.
"""

MY_CMD = 'tools/version.py'

import sys
import os
import re

# Release version 'M.N.U' or start version 'M.N.U-a0'
RELEASE_START_PATTERN = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+(-a0)?$')


def get_git_version():
    """
    Return the collection version based on git tags.

    The version is based on the most recent tag in the git history of the HEAD
    branch. That tag must have one of the following formats:

    - M.N.U      - release version
    - M.N.U-a0   - start version

    The returned version string is suitable as an Ansible collection version
    and will have one of these formats:

    - M.N.U-a0.devD.gC.dirty  - if repo directory is dirty
    - M.N.U-a0.devD.gC        - if repo directory is not dirty but has
                                commits since the start tag
    - M.N.U-a0                - if on the start tag
    - M.N.U                   - if on the release tag

    In the initial 'make install' in the test workflow, the GitPython package
    providing the 'git' module is not yet installed. In that case, ImportError
    is raised to indicate that.

    In case of any other issue, RuntimeError is raised.
    """
    import git  # pylint: disable=import-outside-toplevel

    try:
        repo = git.Repo(search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError as exc:
        raise RuntimeError(f"Not in a git repo: {exc}")

    try:
        latest_tag = repo.git.describe(tags=True, abbrev="0")
    except git.exc.GitCommandError as exc:
        if "No names found" in exc.stderr:
            raise RuntimeError("No git tag found in history of HEAD branch")
        git_command = ' '.join(exc.command)
        git_msg = exc.stderr.replace("stderr: ", "").strip("\n '")
        raise RuntimeError(f"git command '{git_command}' failed: {git_msg}")

    if RELEASE_START_PATTERN.match(latest_tag) is None:
        raise RuntimeError(
            "Incorrect format for most recent git tag in history of HEAD "
            f"branch: {latest_tag} - must be M.N.U-a0 or M.N.U")

    git_version = repo.git.describe(tags=True, dirty=".dirty")
    # The above has one of these formats:
    # - M.N.U-a0-D-gC.dirty     - if repo directory is dirty
    # - M.N.U-a0-D-gC           - if repo directory is not dirty but has
    #                             commits since the start tag
    # - M.N.U-a0                - if on the start tag
    # - M.N.U                   - if on the release tag

    # Translate '-D-gC' to '.devD.gC', if present
    coll_version = re.sub(r'-([0-9]+)-g([0-9a-f]+)', r'.dev\1.g\2', git_version)

    return coll_version


def get_galaxy_version():
    """
    Return the collection version defined in the galaxy.yml file.

    In case of any issue, RuntimeError is raised.

    In order to avoid the dependency to a yaml package, this is done by
    parsing the file with a regular expression.
    """
    galaxy_file = '../galaxy.yml'  # relative to the dir of this file
    galaxy_file = os.path.relpath(os.path.join(
        os.path.dirname(__file__), galaxy_file))

    with open(galaxy_file, encoding='utf-8') as fp:
        ftext = fp.read()
    m = re.search(r"^version: *(.+) *$", ftext, re.MULTILINE)
    if not m:
        raise RuntimeError(
            "No 'version' parameter found in collection manifest file: "
            f"{galaxy_file}")
    coll_version = m.group(1)
    return coll_version


def main():
    "main function"

    try:
        try:
            coll_version = get_git_version()
        except ImportError:
            coll_version = get_galaxy_version()
    except RuntimeError as exc:
        print(f"{MY_CMD}: Error: {exc}", file=sys.stderr, flush=True)
        return 1

    print(coll_version)
    return 0


if __name__ == '__main__':
    sys.exit(main())
