#!/usr/bin/env python
# Copyright 2017 IBM Corp. All Rights Reserved.
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
Setup script for zhmc-ansible-modules project.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
import setuptools

# The following disables the version normalization that setuptools otherwise
# performs:
from setuptools.extern.packaging import version
version.Version = version.LegacyVersion


def get_version(galaxy_file):
    """
    Get the version from the collection manifest file (galaxy.yml).

    In order to avoid the dependency to a yaml package, this is done by
    parsing the file with a regular expression.
    """
    with open(galaxy_file, 'r') as fp:
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


def get_requirements(requirements_file):
    """
    Parse the specified requirements file and return a list of its non-empty,
    non-comment lines. The returned lines are without any trailing newline
    characters.
    """
    with open(requirements_file, 'r') as f_p:
        lines = f_p.readlines()
    reqs = []
    for line in lines:
        line = line.strip('\n')
        if not line.startswith('#') and line != '':
            reqs.append(line)
    return reqs


def read_file(a_file):
    """
    Read the specified file and return its content as one string.
    """
    with open(a_file, 'r') as f_p:
        content = f_p.read()
    return content


# pylint: disable=invalid-name
requirements = get_requirements('requirements.txt')
install_requires = [req for req in requirements
                    if req and not re.match(r'[^:]+://', req)]
dependency_links = [req for req in requirements
                    if req and re.match(r'[^:]+://', req)]
package_version = get_version('galaxy.yml')

# Docs on setup():
# * https://docs.python.org/2.7/distutils/apiref.html?
#   highlight=setup#distutils.core.setup
# * https://setuptools.readthedocs.io/en/latest/setuptools.html#
#   new-and-changed-setup-keywords
# Explanations for the behavior of package_data, include_package_data, and
# MANIFEST files:
# * https://setuptools.readthedocs.io/en/latest/setuptools.html#
#   including-data-files
# * https://stackoverflow.com/a/11848281/1424462
# * https://stackoverflow.com/a/14159430/1424462
setuptools.setup(
    name='zhmc-ansible-modules',
    version=package_version,
    package_dir={'zhmc-ansible-modules': 'plugins'},
    packages=[
        'zhmc-ansible-modules',
        'zhmc-ansible-modules.module_utils',
        'zhmc-ansible-modules.modules'
    ],
    install_requires=install_requires,
    dependency_links=dependency_links,

    description=''
    'Ansible modules managing a IBM Z via the HMC Web Services API.',
    long_description=read_file('README.md'),
    long_description_content_type='text/x-rst',
    license='Apache License, Version 2.0',
    author='Andreas Scheuring, Juergen Leopold, Andreas Maier',
    author_email='scheuran@de.ibm.com, leopoldj@de.ibm.com, maiera@de.ibm.com',
    maintainer='Andreas Maier',
    maintainer_email='maiera@de.ibm.com',
    url='https://github.com/zhmcclient/zhmc-ansible-modules',
    project_urls={
        'Bug Tracker':
            'https://github.com/zhmcclient/zhmc-ansible-modules/issues',
        'Documentation':
            'https://zhmc-ansible-modules.readthedocs.io/en/stable/',
        'Source Code':
            'https://github.com/zhmcclient/zhmc-ansible-modules',
    },

    options={'bdist_wheel': {'universal': True}},
    zip_safe=True,  # This package can safely be installed from a zip file
    platforms='any',

    # This is the only place specifying supported Python versions.
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
