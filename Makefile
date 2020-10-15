# ------------------------------------------------------------------------------
# Makefile for zhmc-ansible-modules project
#
# Basic prerequisites for running this Makefile, to be provided manually:
#   One of these OS platforms:
#     Windows with CygWin
#     Linux (any)
#     OS-X
#   These commands on all OS platforms:
#     make (GNU make)
#     bash
#     rm, mv, find, tee, which
#   These commands on all OS platforms in the active Python environment:
#     python (or python3 on OS-X)
#     pip (or pip3 on OS-X)
#     twine
#   These commands on Linux and OS-X:
#     uname
# Environment variables:
#   PYTHON_CMD: Python command to use (OS-X needs to distinguish Python 2/3)
#   PIP_CMD: Pip command to use (OS-X needs to distinguish Python 2/3)
#   PACKAGE_LEVEL: minimum/latest - Level of Python dependent packages to use
# Additional prerequisites for running this Makefile are installed by running:
#   make develop
# ------------------------------------------------------------------------------

# Python / Pip commands
ifndef PYTHON_CMD
  PYTHON_CMD := python
endif
ifndef PIP_CMD
  PIP_CMD := pip
endif

# Package level
ifndef PACKAGE_LEVEL
  PACKAGE_LEVEL := latest
endif
ifeq ($(PACKAGE_LEVEL),minimum)
  pip_level_opts := -c minimum-constraints.txt
  pip_level_opts_new :=
else
  ifeq ($(PACKAGE_LEVEL),latest)
    pip_level_opts := --upgrade
    pip_level_opts_new := --upgrade-strategy eager
  else
    $(error Error: Invalid value for PACKAGE_LEVEL variable: $(PACKAGE_LEVEL))
  endif
endif

# Determine OS platform make runs on
ifeq ($(OS),Windows_NT)
  PLATFORM := Windows
else
  # Values: Linux, Darwin
  PLATFORM := $(shell uname -s)
endif

# Name of this package on Pypi
# Note: This must match the 'name' attribute specified in setup.py.
# Note: Underscores in package names are automatically converted to dashes in
#       the Pypi package name (see https://stackoverflow.com/q/19097057/1424462),
#       so we specify dashes for the Pypi package name right away.
package_name_pypi := zhmc-ansible-modules
package_name_pypi_under := $(subst -,_,$(package_name_pypi))

# Name of the Python package
package_name_python := zhmc_ansible_modules
package_name_python_dashes := $(subst _,-,$(package_name_python))

# Package version (full version, including any pre-release suffixes, e.g. "0.1.0.dev1")
# Note: The package version is defined in zhmc_ansible_modules/_version.py.
package_version := $(shell $(PYTHON_CMD) setup.py --version)

# Python major version
python_major_version := $(shell $(PYTHON_CMD) -c "import sys; sys.stdout.write('%s'%sys.version_info[0])")

# Python major+minor version
python_mn_version := $(shell $(PYTHON_CMD) -c "import sys; sys.stdout.write('%s%s'%(sys.version_info[0],sys.version_info[1]))")



# Build directory
build_dir = build



# Directory with the source code of our Ansible module source files
module_src_dir := plugins/modules
module_py_files := $(wildcard $(module_src_dir)/zhmc_*.py)

# Directory with test source files
test_dir = tests

# Directory with hmc_definitions.yaml file for end2end tests
default_test_hmc_dir := ../python-zhmcclient/tests
ifndef TESTHMCDIR
  TESTHMCDIR := $(default_test_hmc_dir)
endif

# Nickname of test HMC in hmc_definitions.yaml file for end2end tests
default_test_hmc := default
ifndef TESTHMC
  TESTHMC := $(default_test_hmc)
endif

# Directory for the generated distribution files
dist_build_dir := $(build_dir)/dist

# Distribution archives (as built by setup.py)
bdist_file := $(dist_build_dir)/$(package_name_python)-$(package_version)-py2.py3-none-any.whl
sdist_file := $(dist_build_dir)/$(package_name_python_dashes)-$(package_version).tar.gz

# Files the distribution archive depends upon.
dist_dependent_files := \
    setup.py \
    README.rst \
    requirements.txt \
    $(wildcard *.py) \
    $(wildcard $(module_src_dir)/*.py) \
    $(wildcard $(module_src_dir)/*/*.py) \
    $(wildcard $(module_src_dir)/*/*/*.py) \

# Directory for documentation (with Makefile)
doc_dir := docs
doc_gen_dir := $(doc_dir)/source
doc_check_dir := doc_check

# Directory for generated documentation
doc_build_dir := $(doc_dir)/build

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = $(doc_gen_dir)
BUILDDIR      = $(doc_build_dir)

# Flake8 config file
flake8_rc_file := .flake8

# FLake8 log file
flake8_log_file := flake8_$(python_mn_version).log

# Source files for check (with Flake8)
check_py_files := \
    setup.py \
    $(wildcard $(module_src_dir)/*.py) \
    $(wildcard $(module_src_dir)/*/*.py) \
    $(wildcard $(module_src_dir)/*/*/*.py) \
    $(wildcard $(test_dir)/*.py) \
    $(wildcard $(test_dir)/*/*.py) \
    $(wildcard $(test_dir)/*/*/*.py) \
    $(wildcard tools/*.py) \

# Test log file
test_log_file := test_$(python_mn_version).log

pytest_opts := $(TESTOPTS)

# Location of local clone of Ansible project's Git repository, with the
# 'devel' branch checked out. Will be cloned automatically.
ansible_repo_dir := ../ansible

# Documentation-related directories from Ansible project
ansible_repo_template_dir := $(ansible_repo_dir)/docs/templates
ansible_repo_lib_dir := $(ansible_repo_dir)/lib
ansible_repo_rst_dir := $(ansible_repo_dir)/docs/docsite/rst

# plugin_formatter tool from Ansible project
plugin_formatter := $(ansible_repo_dir)/hacking/build-ansible.py document-plugins
plugin_formatter_template_file := $(ansible_repo_template_dir)/plugin.rst.j2
plugin_formatter_template_dir := $(shell dirname $(plugin_formatter_template_file))

# validate-modules tool from Ansible project
validate_modules := $(ansible_repo_dir)/bin/ansible-test sanity --test validate-modules
validate_modules_log_file := validate.log
validate_modules_exclude_pattern := (E101|E105|E106|DeprecationWarning)

# Documentation files from Ansible repo to copy to $(doc_gen_dir)
doc_copy_files := \
    $(ansible_repo_rst_dir)/reference_appendices/common_return_values.rst \
    $(ansible_repo_rst_dir)/user_guide/modules_support.rst \

# No built-in rules needed:
.SUFFIXES:

.PHONY: help
help:
	@echo 'Makefile for $(package_name_pypi) project'
	@echo 'Package version will be: $(package_version)'
	@echo 'Currently active Python environment: Python $(python_mn_version)'
	@echo 'Valid targets are:'
	@echo '  install    - Install package (as editable) and its reqs into active Python environment'
	@echo '  develop    - Set up the development environment'
	@echo '  docs       - Build the documentation in: $(doc_build_dir)'
	@echo '  check      - Run all checks (flake8, validate-modules)'
	@echo '  test       - Run unit tests (and test coverage) and save results in: $(test_log_file)'
	@echo '               Env.var TESTCASES can be used to specify a py.test expression for its -k option'
	@echo '  all        - Do all of the above'
	@echo '  end2end    - Run end2end tests'
	@echo '  sanity     - Run ansible sanity tests'
	@echo '  upload     - Upload the package to PyPI'
	@echo '  uninstall  - Uninstall package from active Python environment'
	@echo '  clobber    - Remove any produced files'
	@echo '  doccheck   - Run check whether generated module docs are up to date'
	@echo '  linkcheck  - Check links in documentation (does not work)'
	@echo '  dist       - Build the distribution files in: $(dist_build_dir) (not used)'
	@echo 'Environment variables:'
	@echo '  TESTHMC=... - Nickname of HMC to be used in end2end tests. Default: $(default_test_hmc)'
	@echo '  TESTHMCDIR=... - Path name of directory with hmc_definitions.yaml file. Default: $(default_test_hmc_dir)'
	@echo '  TESTOPTS=... - Additional options for py.test (e.g. "-k test_module.py")'
	@echo '  PACKAGE_LEVEL="minimum" - Install minimum version of dependent Python packages'
	@echo '  PACKAGE_LEVEL="latest" - Default: Install latest version of dependent Python packages'
	@echo '  PYTHON_CMD=... - Name of python command. Default: python'
	@echo '  PIP_CMD=... - Name of pip command. Default: pip'
	@echo 'Invocation of ansible commands from within repo main directory:'
	@echo '  export ANSIBLE_LIBRARY="$$(pwd)/$(module_src_dir);$$ANSIBLE_LIBRARY"'
	@echo '  # currently: ANSIBLE_LIBRARY=$(ANSIBLE_LIBRARY)'
	@echo '  ansible-playbook playbooks/....'

.PHONY: install
install: _pip requirements.txt setup.py
	@echo 'Installing package (as editable) and its reqs with PACKAGE_LEVEL=$(PACKAGE_LEVEL) into current Python environment'
	$(PIP_CMD) install $(pip_level_opts) $(pip_level_opts_new) -r requirements.txt
	$(PIP_CMD) install -e .
	@echo 'Done: Installed package and its reqs into current Python environment.'

.PHONY: develop
develop: _pip requirements.txt dev-requirements.txt os_setup.sh $(ansible_repo_dir) develop_ansible
	@echo 'Setting up the development environment with PACKAGE_LEVEL=$(PACKAGE_LEVEL)'
	bash -c './os_setup.sh'
	$(PIP_CMD) install $(pip_level_opts) $(pip_level_opts_new) -r dev-requirements.txt
	@echo '$@ done.'

.PHONY: develop_ansible
develop_ansible: _pip $(ansible_repo_dir) $(ansible_repo_dir)/docs/docsite/requirements.txt
	@echo 'Setting up the development environment for Ansible tools'
	$(PIP_CMD) install $(pip_level_opts) $(pip_level_opts_new) -r $(ansible_repo_dir)/docs/docsite/requirements.txt
	@echo '$@ done.'

.PHONY: docs
docs: $(doc_build_dir)/html/index.html 
	@echo '$@ done.'

.PHONY: check
check: $(flake8_log_file)  # $(validate_modules_log_file)
	@echo '$@ done.'

.PHONY: test
test: $(test_log_file)
	@echo '$@ done.'

.PHONY: all
all: install develop docs check test
	@echo '$@ done.'

.PHONY: upload
upload: _check_version $(bdist_file) $(sdist_file)
ifeq (,$(findstring .dev,$(package_version)))
	@echo '==> This will upload $(package_name_pypi) version $(package_version) to PyPI!'
	@echo -n '==> Continue? [yN] '
	@bash -c 'read answer; if [[ "$$answer" != "y" ]]; then echo "Aborted."; false; fi'
	twine upload $(bdist_file) $(sdist_file)
	@echo 'Done: Uploaded $(package_name_pypi) version to PyPI: $(package_version)'
	@echo '$@ done.'
else
	@echo 'Error: A development version $(package_version) of $(package_name_pypi) cannot be uploaded to PyPI!'
	@false
endif

.PHONY: uninstall
uninstall:
	bash -c '$(PIP_CMD) show $(package_name_pypi) >/dev/null; rc=$$?; if [[ $$rc == 0 ]]; then $(PIP_CMD) uninstall -y $(package_name_pypi); fi'
	@echo '$@ done.'

.PHONY: clobber
clobber:
	rm -Rf .cache $(package_name_pypi_under).egg-info .eggs $(build_dir) $(doc_check_dir) htmlcov .tox
	rm -f MANIFEST MANIFEST.in AUTHORS ChangeLog .coverage flake8_*.log test_*.log $(validate_modules_log_file)
	find . -name "*.pyc" -delete -o -name "__pycache__" -delete -o -name "*.tmp" -delete -o -name "tmp_*" -delete
	rm -rf $(doc_build_dir)

	@echo 'Done: Removed all build products to get to a fresh state.'
	@echo '$@ done.'

.PHONY: doccheck
doccheck: $(doc_check_dir)/list_of_all_modules.rst
	bash -c 'diff -bB --exclude=common_return_values.rst --exclude=modules_support.rst $(doc_gen_dir) $(doc_check_dir); if [[ "$$?" != "0" ]]; then echo "Error: Module documentation files are not up to date - run make docs and commit them."; false; fi'
	@echo '$@ done.'

.PHONY: linkcheck
linkcheck: $(doc_build_dir)/linkcheck/output.txt
	@echo '$@ done.'

.PHONY: dist
dist: $(bdist_file) $(sdist_file)
	@echo '$@ done.'

.PHONY: _check_version
_check_version:
ifeq (,$(package_version))
	@echo 'Error: Package version could not be determined'
	@false
else
	@true
endif

.PHONY: _pip
_pip:
	$(PYTHON_CMD) remove_duplicate_setuptools.py
	@echo 'Installing/upgrading pip, setuptools, and wheel with PACKAGE_LEVEL=$(PACKAGE_LEVEL)'
	$(PYTHON_CMD) -m pip install $(pip_level_opts) pip setuptools wheel

$(bdist_file): _check_version Makefile $(dist_dependent_files)
ifneq ($(PLATFORM),Windows)
	rm -Rf $(package_name_pypi_under).egg-info .eggs
	mkdir -p $(dist_build_dir)
	$(PYTHON_CMD) setup.py bdist_wheel -d $(dist_build_dir) --universal
	@echo 'Done: Created distribution file: $@'
else
	@echo 'Error: Creating bdist_wheel distribution archive requires to run on Linux or OS-X'
	@false
endif

$(sdist_file): _check_version Makefile $(dist_dependent_files)
ifneq ($(PLATFORM),Windows)
	rm -Rf $(package_name_pypi_under).egg-info .eggs
	mkdir -p $(dist_build_dir)
	$(PYTHON_CMD) setup.py sdist -d $(dist_build_dir)
	@echo 'Done: Created distribution file: $@'
else
	@echo 'Error: Creating sdist distribution archive requires to run on Linux or OS-X'
	@false
endif

$(ansible_repo_dir):
	@echo 'Cloning our fork of the Ansible repo into: $@'
# pinned to a fixed version since the doc generation process has been changed
# in 2.10 (ansibull). TODO: Adapt doc generation.
	git clone https://github.com/ansible/ansible.git --branch stable-2.10 $@

$(doc_gen_dir)/list_of_all_modules.rst: Makefile $(module_py_files) $(ansible_repo_dir)
	mkdir -p $(doc_gen_dir)
	PYTHONPATH=$(ansible_repo_lib_dir) $(plugin_formatter) -vv --type=rst --template-dir=$(plugin_formatter_template_dir) --module-dir=$(module_src_dir) --output-dir=$(doc_gen_dir)/
	rm -fv $(doc_gen_dir)/modules_by_category.rst $(doc_gen_dir)/list_of__modules.rst

$(doc_check_dir)/list_of_all_modules.rst: Makefile $(module_py_files) $(ansible_repo_dir)
	mkdir -p $(doc_check_dir)
	PYTHONPATH=$(ansible_repo_lib_dir) $(plugin_formatter) -vv --type=rst --template-dir=$(plugin_formatter_template_dir) --module-dir=$(module_src_dir) --output-dir=$(doc_check_dir)/
	rm -fv $(doc_check_dir)/modules_by_category.rst $(doc_check_dir)/list_of__modules.rst

$(doc_build_dir)/html/index.html: 
	mkdir -p $(doc_dir)/build
	mv plugins/modules/__init__.py plugins/modules/__init__.py.skip
	ansible-doc-extractor $(doc_dir)/source/modules plugins/modules/*.py
	echo "Completed restructured text generation"
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) -Q $(O)
	mv plugins/modules/__init__.py.skip plugins/modules/__init__.py
	@echo "Done: Created the HTML pages with top level file: $@"

$(doc_build_dir)/linkcheck/output.txt: Makefile $(doc_dependent_files) $(doc_gen_dir)/list_of_all_modules.rst
	$(sphinx) -b linkcheck $(sphinx_opts) $(doc_dir) $(doc_build_dir)/linkcheck
	@echo
	@echo "Done: Look for any errors in the above output or in: $@"

$(flake8_log_file): Makefile $(flake8_rc_file) $(check_py_files)
	rm -f $@
	bash -c 'set -o pipefail; flake8 $(check_py_files) 2>&1 |tee $@.tmp'
	mv -f $@.tmp $@
	@echo 'Done: Flake8 checker succeeded'

$(validate_modules_log_file): Makefile $(module_py_files) $(ansible_repo_dir)
	rm -f $@
	bash -c 'PYTHONPATH=$(ansible_repo_lib_dir) $(validate_modules) $(module_py_files) 2>&1 |grep -v -E "$(validate_modules_exclude_pattern)" |tee $@.tmp'
	bash -c 'if [[ -n "$$(cat $@.tmp)" ]]; then false; fi'
	mv -f $@.tmp $@
	@echo 'Done: Ansible validate-modules checker succeeded'

$(test_log_file): Makefile $(check_py_files)
	rm -f $@
	bash -c 'set -o pipefail; PYTHONWARNINGS=default ANSIBLE_LIBRARY=$(module_src_dir) PYTHONPATH=. pytest -s --cov $(module_src_dir) --cov-config .coveragerc --cov-report=html:htmlcov $(pytest_opts) $(test_dir)/unit $(test_dir)/function 2>&1 |tee $@.tmp'
	mv -f $@.tmp $@
	@echo 'Done: Created test log file: $@'

.PHONY:	end2end
end2end:
	bash -c 'PYTHONWARNINGS=default TESTHMCDIR=$(TESTHMCDIR) TESTHMC=$(TESTHMC) py.test -s -v $(pytest_opts) $(test_dir)/end2end'
	@echo '$@ done.'

.PHONY:	sanity
sanity:
	@echo 'Starting sanity tests...'
	rm -rf ../ansible
	ansible-test sanity --docker
	# then uninstall 2.9 and install 2.10 (ansible-base)
	pip uninstall -y ansible
	pip install ansible-base
	# and run the sanity tests with 2.10
	ansible-test sanity --docker
	@echo '$@ done.'
