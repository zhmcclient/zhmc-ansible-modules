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
#     rm, find
#   These commands on all OS platforms in the active Python environment:
#     python (or python3 on OS-X)
#     pip (or pip3 on OS-X)
#   These commands on Linux and OS-X:
#     uname
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

# Namespace and name of this collection
# TODO: Check out whether this needs to match the 'name' attribute specified in setup.py.
collection_namespace := ibm
collection_name := ibm_zhmc
collection_full_name := $(collection_namespace).$(collection_name)

# Collection version (full version, e.g. "1.0.0")
# Note: The collection version is defined in galaxy.yml
collection_version := $(shell $(PYTHON_CMD) tools/version.py)

# Python versions
python_major_version := $(shell $(PYTHON_CMD) -c "import sys; sys.stdout.write('%s'%sys.version_info[0])")
python_m_n_version := $(shell $(PYTHON_CMD) -c "import sys; sys.stdout.write('%s.%s'%(sys.version_info[0],sys.version_info[1]))")
pymn := $(shell $(PYTHON_CMD) -c "import sys; sys.stdout.write('py%s%s'%(sys.version_info[0],sys.version_info[1]))")

# Flag indicating whether docs can be built
# Keep in sync with Sphinx & ansible-doc-extractor install in minimum-constraints.txt and dev-requirements.txt
doc_build := $(shell $(PYTHON_CMD) -c "import sys; sys.stdout.write('true' if sys.version_info[0:2]>=(3,6) else 'false')")

# The Python source files that are Ansible modules
module_py_dir := plugins/modules
module_py_files := $(wildcard $(module_py_dir)/zhmc_*.py)

# All Python source files (including Ansible modules)
src_py_dir := plugins
src_py_files := \
    $(wildcard $(src_py_dir)/*.py) \
    $(wildcard $(src_py_dir)/*/*.py) \
    $(wildcard $(src_py_dir)/*/*/*.py) \

# All Python test source files
test_dir := tests
test_py_files := \
    $(wildcard $(test_dir)/*.py) \
    $(wildcard $(test_dir)/*/*.py) \
    $(wildcard $(test_dir)/*/*/*.py) \

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

# Flake8 options
flake8_opts := --max-line-length 160 --config /dev/null --ignore E402,E741,W503,W504

# Sanity test directory
# Note: 'ansible-test sanity' requires the collection to be tested to be
#       located in {...}/collections/ansible_collections/{namespace}/{name}.
#       The .git subtree must also be present.
#       There is issue https://github.com/ansible/ansible/issues/60215 that
#       discusses improving that.
#       We copy most of the repo directory into sanity_dir to establish the
#       required directory structure.
sanity_dir := tmp_sanity/collections/ansible_collections/ibm/ibm_zhmc
sanity_dir1 := tmp_sanity
sanity_tar_file := tmp_workspace.tar

# Directories for documentation
doc_source_dir := docs/source
doc_templates_dir := docs/templates
doc_linkcheck_dir := docs_linkcheck
doc_build_dir := docs_build
doc_build_local_dir := docs_local

# Module RST files
module_rst_dir := $(doc_source_dir)/modules
module_rst_files := $(patsubst $(module_py_dir)/%.py,$(module_rst_dir)/%.rst,$(module_py_files))

# All documentation RST files (including module RST files)
doc_rst_files := \
    $(wildcard $(doc_source_dir)/*.rst) \
    $(module_rst_files) \

# The Ansible Galaxy distribution archive
dist_dir := dist
dist_file := $(dist_dir)/$(collection_namespace)-$(collection_name)-$(collection_version).tar.gz
dist_dependent_files := \
    README.md \
    requirements.txt \
    $(wildcard *.py) \
    $(src_py_files) \
    $(test_py_files) \
    $(doc_rst_files) \

# Sphinx options (besides -M)
sphinx_opts := -v

# Pytest options
pytest_opts := $(TESTOPTS) -s
ifeq ($(python_m_n_version),3.4)
  pytest_cov_opts :=
else
  pytest_cov_opts := --cov $(module_py_dir) --cov-config .coveragerc --cov-report=html:htmlcov
endif

# No built-in rules needed:
.SUFFIXES:
.SUFFIXES: .py .rst

.PHONY: help
help:
	@echo 'Makefile for Ansible collection:     $(collection_full_name)'
	@echo 'Collection version will be:          $(collection_version)'
	@echo 'Currently active Python environment: Python $(python_m_n_version)'
	@echo 'Valid targets are:'
	@echo '  install    - Install collection and its dependent Python packages'
	@echo '  develop    - Set up the development environment'
	@echo '  dist       - Build the collection distribution archive in: $(dist_dir)'
	@echo '  test       - Run unit and function tests with test coverage'
	@echo '  check      - Run flake8'
	@echo '  sanity     - Run Ansible sanity tests (includes pep8, pylint, validate-modules)'
	@echo '  docs       - Build the documentation for all enabled (docs/source/conf.py) versions in: $(doc_build_dir) using remote repo'
	@echo '  docslocal  - Build the documentation from local repo contents in: $(doc_build_local_dir)'
	@echo '  linkcheck  - Check links in documentation'
	@echo '  all        - Do all of the above'
	@echo '  end2end    - Run end2end tests'
	@echo '  upload     - Publish the collection to Ansible Galaxy'
	@echo '  clobber    - Remove any produced files'
	@echo 'Environment variables:'
	@echo '  TESTHMC=... - Nickname of HMC to be used in end2end tests. Default: $(default_test_hmc)'
	@echo '  TESTHMCDIR=... - Path name of directory with hmc_definitions.yaml file. Default: $(default_test_hmc_dir)'
	@echo '  TESTOPTS=... - Additional options for py.test (e.g. "-k test_module.py")'
	@echo '  PACKAGE_LEVEL="minimum" - Install minimum version of dependent Python packages'
	@echo '  PACKAGE_LEVEL="latest" - Default: Install latest version of dependent Python packages'
	@echo '  PYTHON_CMD=... - Name of python command. Default: python'
	@echo '  PIP_CMD=... - Name of pip command. Default: pip'
	@echo '  GALAXY_TOKEN=... - Your Ansible Galaxy token, required for upload (see https://galaxy.ansible.com/me/preferences)'
	@echo 'Invocation of ansible commands from within repo main directory:'
	@echo '  export ANSIBLE_LIBRARY="$$(pwd)/$(module_py_dir);$$ANSIBLE_LIBRARY"'
	@echo '  # currently: ANSIBLE_LIBRARY=$(ANSIBLE_LIBRARY)'
	@echo '  ansible-playbook playbooks/....'

.PHONY: all
all: install develop dist test check sanity docs docslocal linkcheck
	@echo '$@ done.'

.PHONY: install
install: _check_version install_$(pymn).done
	@echo '$@ done.'

.PHONY: develop
develop: _check_version develop_$(pymn).done
	@echo '$@ done.'

.PHONY: docs
docs: _check_version develop_$(pymn).done $(doc_build_dir)/index.html
	@echo '$@ done.'

.PHONY: linkcheck
linkcheck: _check_version develop_$(pymn).done $(doc_rst_files)
	-sphinx-build -b linkcheck $(sphinx_opts) $(doc_source_dir) $(doc_linkcheck_dir)
	@echo '$@ done.'

.PHONY: test
test: _check_version develop_$(pymn).done
	bash -c 'PYTHONWARNINGS=default ANSIBLE_LIBRARY=$(module_py_dir) PYTHONPATH=. pytest $(pytest_cov_opts) $(pytest_opts) $(test_dir)/unit $(test_dir)/function'
	@echo '$@ done.'

.PHONY: check
check: _check_version develop_$(pymn).done
	flake8 $(flake8_opts) $(src_py_dir) $(test_dir)
	@echo '$@ done.'

.PHONY:	sanity
sanity: _check_version develop_$(pymn).done
	# The sanity check requires the .git directory to be present.
	rm -f $(sanity_tar_file)
	tar -rf $(sanity_tar_file) .git .gitignore bindep.txt galaxy.yml requirements.txt collections docs meta plugins tests
	rm -rf $(sanity_dir)
	mkdir -p $(sanity_dir)
	tar -xf $(sanity_tar_file) --directory $(sanity_dir)
	sh -c "cd $(sanity_dir); ansible-test sanity --verbose --truncate 0 --local --python $(python_m_n_version)"
ifeq ($(PACKAGE_LEVEL),latest)
  # On minimum package level (i.e. Ansible 2.9), the pylint check fails with:
  #   internal error with sending report for module ['plugins/module_utils/common.py']
  #   object of type 'Uninferable' has no len()
	sh -c "cd $(sanity_dir); ansible-test sanity --verbose --truncate 0 --venv --requirements --python $(python_m_n_version)"
endif
	@echo '$@ done.'

.PHONY:	end2end
end2end: _check_version develop_$(pymn).done
	bash -c 'PYTHONWARNINGS=default TESTHMCDIR=$(TESTHMCDIR) TESTHMC=$(TESTHMC) py.test -v $(pytest_opts) $(test_dir)/end2end'
	@echo '$@ done.'

.PHONY: upload
upload: _check_version _check_galaxy_token $(dist_file)
ifeq (,$(findstring .dev,$(collection_version)))
	@echo '==> This will publish collection $(collection_full_name) version $(collection_version) on Ansible Galaxy!'
	@echo -n '==> Continue? [yN] '
	@bash -c 'read answer; if [[ "$$answer" != "y" ]]; then echo "Aborted."; false; fi'
	ansible-galaxy collection publish --token $(GALAXY_TOKEN) $(dist_file)
	@echo 'Done: Published collection $(collection_full_name) version $(collection_version) on Ansible Galaxy'
	@echo '$@ done.'
else
	$(error Error: A development version $(collection_version) of collection $(collection_full_name) cannot be published on Ansible Galaxy!)
endif

# The second rm command of each type is for files that were used before 1.0.0, to make it easier to switch.
.PHONY: clobber
clobber:
	rm -Rf .cache .pytest_cache $(sanity_dir1) $(sanity_tar_file) htmlcov $(doc_linkcheck_dir) $(doc_build_dir) $(doc_build_local_dir)
	rm -Rf tests/output build .tox *.egg-info
	rm -f .coverage *.done
	rm -f MANIFEST MANIFEST.in AUTHORS ChangeLog
	find . -name "*.pyc" -delete -o -name "__pycache__" -delete -o -name "*.tmp" -delete -o -name "tmp_*" -delete
	@echo '$@ done.'

.PHONY: dist
dist: _check_version $(dist_file)
	@echo '$@ done.'

.PHONY: _check_version
_check_version:
ifeq (,$(collection_version))
	$(error Error: Collection version could not be determined)
else
	@true >/dev/null
endif

.PHONY: _check_galaxy_token
_check_galaxy_token:
ifeq (,$(GALAXY_TOKEN))
	$(error Error: GALAXY_TOKEN env var needs to be set to your Ansible Galaxy API Key, see https://galaxy.ansible.com/me/preferences)
else
	@true >/dev/null
endif

install_$(pymn).done: Makefile develop_$(pymn).done $(dist_file) requirements.txt
	$(PIP_CMD) install $(pip_level_opts) $(pip_level_opts_new) -r requirements.txt
	ansible-galaxy collection install --force $(dist_file)
	echo "done" >$@

develop_$(pymn).done: Makefile install_pip_$(pymn).done tools/os_setup.sh dev-requirements.txt
	bash -c 'tools/os_setup.sh'
	$(PIP_CMD) install $(pip_level_opts) $(pip_level_opts_new) -r dev-requirements.txt
	echo "done" >$@

install_pip_$(pymn).done: Makefile
	bash -c 'pv=$$($(PYTHON_CMD) -m pip --version); if [[ $$pv =~ (^pip [1-8]\..*) ]]; then $(PYTHON_CMD) -m pip install pip==9.0.1; fi'
	$(PYTHON_CMD) -m pip install $(pip_level_opts) pip setuptools wheel
	echo "done" >$@

$(dist_file): $(dist_dependent_files) galaxy.yml
	mkdir -p $(dist_dir)
	ansible-galaxy collection build --output-path=$(dist_dir) --force .

$(module_rst_dir):
	mkdir -p $(module_rst_dir)

$(module_rst_dir)/%.rst: $(module_py_dir)/%.py $(module_rst_dir) $(doc_templates_dir)/module.rst.j2
ifneq ($(doc_build),true)
	@echo "makefile: Warning: Skipping module docs extraction on Python $(python_m_n_version)"
else
	ansible-doc-extractor --template $(doc_templates_dir)/module.rst.j2 $(module_rst_dir) $<
endif

# .nojekyll file disables GitHub pages jekyll pre-processing
$(doc_build_dir)/index.html: $(doc_rst_files) $(doc_source_dir)/conf.py
ifneq ($(doc_build),true)
	@echo "makefile: Warning: Skipping docs build on Python $(python_m_n_version)"
else
	sphinx-versioning -l $(doc_source_dir)/conf.py build $(doc_source_dir) $(doc_build_dir)
	touch $(doc_build_dir)/.nojekyll
endif

.PHONY: docslocal
docslocal: _check_version develop_$(pymn).done $(doc_rst_files) $(doc_source_dir)/conf.py
	rm -rf $(doc_build_local_dir)
	sphinx-build -b html $(sphinx_opts) $(doc_source_dir) $(doc_build_local_dir)
#	open $(doc_build_local_dir)/index.html
