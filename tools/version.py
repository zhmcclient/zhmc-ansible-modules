# Copyright 2020 IBM Corp. All Rights Reserved.
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
Script that prints the version defined in the galaxy.yml file.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import io
import re


def get_version(galaxy_file):
    """
    Get the version from the collection manifest file (galaxy.yml).

    In order to avoid the dependency to a yaml package, this is done by
    parsing the file with a regular expression.
    """
    with io.open(galaxy_file, 'r', encoding='utf-8') as fp:
        ftext = fp.read()
    m = re.search(r"^version: *(.+) *$", ftext, re.MULTILINE)
    if not m:
        raise ValueError(
            "No 'version' parameter found in collection manifest file: {0}".
            format(galaxy_file))
    version_str = m.group(1)
    m = re.search(r"^([0-9]+\.[0-9]+\.[0-9]+(-[a-z.0-9]+)?)$", version_str)
    if not m:
        raise ValueError(
            "Invalid version found in collection manifest file {0}: {1}".
            format(galaxy_file, version_str))
    version = m.group(1)
    return version


def get_galaxy_version():
    """
    Return the version defined in the galaxy.yml file as a string.
    """
    _galaxy_file = '../galaxy.yml'  # relative to the dir of this file
    _galaxy_file = os.path.relpath(os.path.join(
        os.path.dirname(__file__), _galaxy_file))

    # The full version, including alpha/beta/rc tags
    version = get_version(_galaxy_file)
    return version


if __name__ == '__main__':
    print(get_galaxy_version())
