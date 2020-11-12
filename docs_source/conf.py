# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import os
import re


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


# -- Project information -----------------------------------------------------

_galaxy_file = '../galaxy.yml'  # relative to the dir of this file
_galaxy_file = os.path.relpath(os.path.join(
    os.path.dirname(__file__), _galaxy_file))

# The full version, including alpha/beta/rc tags
release = get_version(_galaxy_file)

project = 'ibm.zhmc Ansible Galaxy collection {0}'.format(release)
copyright = '2016-2020, IBM'
author = 'IBM'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_rtd_theme",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# do not copy the source RST files into the generated content
html_copy_source = False

# and do not show the links to the originals
html_show_sourcelink = False
