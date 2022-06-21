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

# Defaults for end2end tests - must match the defaults in zhmcclient/testutils.
default_testinventory := $HOME/.zhmc_inventory.yaml
default_testvault := $HOME/.zhmc_vault.yaml
default_testhmc := default

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
ifdef TESTCASES
  pytest_opts := --color=yes -s $(TESTOPTS) -k "$(TESTCASES)"
else
  pytest_opts := --color=yes -s $(TESTOPTS)
endif
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
	@echo '  uploadhub  - Publish the collection to Ansible AutomationHub'
	@echo '  clobber    - Remove any produced files'
	@echo 'Environment variables:'
	@echo "  TESTCASES=... - Testcase filter for pytest -k (e.g. 'test_func' or 'test_mod.py')"
	@echo "  TESTOPTS=... - Additional options for pytest (e.g. '-x')"
	@echo "  TESTHMC=... - HMC group or host name in HMC inventory file to be used in end2end tests. Default: $(default_testhmc)"
	@echo "  TESTINVENTORY=... - Path name of HMC inventory file used in end2end tests. Default: $(default_testinventory)"
	@echo "  TESTVAULT=... - Path name of HMC vault file used in end2end tests. Default: $(default_testvault)"
	@echo "  PACKAGE_LEVEL - Package level to be used for installing dependent Python"
	@echo "      packages in 'install' and 'develop' targets:"
	@echo "        latest - Latest package versions available on Pypi"
	@echo "        minimum - A minimum version as defined in minimum-constraints.txt"
	@echo "      Optional, defaults to 'latest'."
	@echo '  PYTHON_CMD=... - Name of python command. Default: python'
	@echo '  PIP_CMD=... - Name of pip command. Default: pip'
	@echo '  GALAXY_TOKEN=... - Your Ansible Galaxy API token, required for upload (see https://galaxy.ansible.com/me/preferences)'
	@echo '  AUTOMATIONHUB_TOKEN=... - Your Ansible AutomationHub API token, required for upload (see https://cloud.redhat.com/ansible/automation-hub/token)'
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
	bash -c 'PYTHONWARNINGS=default ANSIBLE_LIBRARY=$(module_py_dir) PYTHONPATH=. TESTEND2END_LOAD=true pytest -v $(pytest_opts) $(test_dir)/end2end'
	@echo '$@ done.'

.PHONY: upload
upload: _check_version $(dist_file)
ifneq ($(findstring dev,$(collection_version)),)
	$(error Error: A development version $(collection_version) of collection $(collection_full_name) cannot be published on Ansible Galaxy)
endif
ifndef GALAXY_TOKEN
	$(error Error: Environment variable GALAXY_TOKEN with your Galaxy API token is required for uploading to Ansible Galaxy - get one on https://galaxy.ansible.com/me/preferences)
endif
	@echo '==> This will publish collection $(collection_full_name) version $(collection_version) on Ansible Galaxy'
	@echo -n '==> Continue? [yN] '
	@bash -c 'read answer; if [[ "$$answer" != "y" ]]; then echo "Aborted."; false; fi'
	@echo ''
	ansible-galaxy collection publish --server https://galaxy.ansible.com/ --token $(GALAXY_TOKEN) $(dist_file)
	@echo 'Done: Published collection $(collection_full_name) version $(collection_version) on Ansible Galaxy'
	@echo '$@ done.'

.PHONY: uploadhub
uploadhub: _check_version $(dist_file)
ifneq ($(findstring dev,$(collection_version)),)
	$(error Error: A development version $(collection_version) of collection $(collection_full_name) cannot be published on Ansible AutomationHub)
endif
ifndef AUTOMATIONHUB_TOKEN
	$(error Error: Environment variable AUTOMATIONHUB_TOKEN with your Ansible AutomationHub API token is required for uploading to Ansible AutomationHub - get one on https://cloud.redhat.com/ansible/automation-hub/token)
endif
	@echo '==> This will publish collection $(collection_full_name) version $(collection_version) on Ansible AutomationHub'
	@echo -n '==> Continue? [yN] '
	@bash -c 'read answer; if [[ "$$answer" != "y" ]]; then echo "Aborted."; false; fi'
	@echo ''
	@echo 'Note: If the following upload fails, upload the collection manually as described in docs/source/development.rst'
	@echo ''
	ansible-galaxy collection publish --server https://console.redhat.com/api/automation-hub/ --token $(AUTOMATIONHUB_TOKEN) $(dist_file)
	@echo 'Done: Published collection $(collection_full_name) version $(collection_version) on Ansible AutomationHub'
	@echo '$@ done.'

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
