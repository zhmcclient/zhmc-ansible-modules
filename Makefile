# ------------------------------------------------------------------------------
# Makefile for zhmc-ansible-modules project
#
# Basic prerequisites for running this Makefile, to be provided manually:
#   One of these OS platforms:
#     Linux
#     macOS
#   These commands on all OS platforms:
#     make (GNU make)
#     bash
#     uname
#     rm, mkdir, cp, find, tar
#     git
#     python, pip
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
  pip_level_opts := -c minimum-constraints-develop.txt -c minimum-constraints-install.txt
  pip_level_opts_new :=
else
  ifeq ($(PACKAGE_LEVEL),ansible)
    pip_level_opts := -c ansible-constraints.txt
    pip_level_opts_new :=
  else
    ifeq ($(PACKAGE_LEVEL),latest)
      pip_level_opts := --upgrade
      pip_level_opts_new := --upgrade-strategy eager
    else
      $(error Error: Invalid value for PACKAGE_LEVEL variable: $(PACKAGE_LEVEL))
    endif
  endif
endif

# Run type (normal, scheduled, release, local)
ifndef RUN_TYPE
  RUN_TYPE := local
endif

# Determine OS platform make runs on
PLATFORM := $(shell uname -s)

# Current working directory
PWD := $(shell pwd)

ENV = env | sort
WHICH = which

# Namespace and name of this collection
collection_namespace := ibm
collection_name := ibm_zhmc
collection_full_name := $(collection_namespace).$(collection_name)

# Collection version (full version, e.g. "1.0.0")
# Note: The collection version is defined in galaxy.yml
collection_version := $(shell $(PYTHON_CMD) tools/version.py)

# Python versions
python_version := $(shell $(PYTHON_CMD) -c "import sys; sys.stdout.write('{v[0]}.{v[1]}.{v[2]}'.format(v=sys.version_info))")
python_major_version := $(shell $(PYTHON_CMD) -c "import sys; sys.stdout.write('%s'%sys.version_info[0])")
python_m_n_version := $(shell $(PYTHON_CMD) -c "import sys; sys.stdout.write('%s.%s'%(sys.version_info[0],sys.version_info[1]))")
pymn := $(shell $(PYTHON_CMD) -c "import sys; sys.stdout.write('py%s%s'%(sys.version_info[0],sys.version_info[1]))")

# Installed ansible-core version (empty if ansible is not installed)
ansible_core_version := $(shell $(PYTHON_CMD) -c "import sys,ansible; sys.stdout.write(ansible.__version__)" 2>/dev/null)

# Python versions for which Ansible is supported (i.e. where its sanity test and ansible-lint check can run).
# The format is a string defining a Python dict with key = ansible-core version (m, n), value = Python version (m, n)
# ansible 8 (ansible-core 2.15) requires Python >=3.9 and its sanity test supports Python 3.9 to 3.11.
# ansible 9 (ansible-core 2.16) requires Python >=3.10 and its sanity test supports Python 3.10 to 3.12.
# ansible 10 (ansible-core 2.17) requires Python >=3.10 and its sanity test supports Python 3.10 to 3.12.
# ansible 11 (ansible-core 2.18) requires Python >=3.11 and its sanity test supports Python 3.11 to 3.13.
# ansible 12 (ansible-core 2.19) requires Python >=3.11 and its sanity test supports Python 3.11 to 3.13.
ansible_min_python_versions := "{(2, 15): (3, 9), (2, 16): (3, 10), (2, 17): (3, 10), (2, 18): (3, 11), (2, 19): (3, 11)}"
ansible_max_python_versions := "{(2, 15): (3, 11), (2, 16): (3, 12), (2, 17): (3, 12), (2, 18): (3, 13), (2, 19): (3, 13)}"

# Boolean variable indicating that the Ansible sanity test should be run (in the current and virtual Python environment).
# The variable is empty if ansible is not installed.
# We run the sanity test only on Python and Ansible version combinations that support the sanity test, and in addition exclude:
#  * Python 3.10 with minimum package levels because sanity setup fails with PyYAML 5.4.1 install issue with Cython 3
run_sanity := $(shell PL=$(PACKAGE_LEVEL) PY_MIN_STR=$(ansible_min_python_versions) PY_MAX_STR=$(ansible_max_python_versions) $(PYTHON_CMD) -c "import sys,os,ansible; py=sys.version_info[0:2]; ac=tuple(map(int,ansible.__version__.split('.')))[0:2]; py_min=eval(os.getenv('PY_MIN_STR'))[ac]; py_max=eval(os.getenv('PY_MAX_STR'))[ac]; pl=os.getenv('PL'); sys.stdout.write('true' if py>=py_min and py<=py_max and not (py==(3,10) and pl=='minimum') else 'false')" 2>/dev/null)

# Boolean variable indicating that ansible-lint should be run.
# The variable is empty if ansible is not installed.
# We run ansible-lint only on Python and Ansible version combinations that support the sanity test, and in addition exclude:
# * Nothing
run_ansible_lint := $(shell PL=$(PACKAGE_LEVEL) PY_MIN_STR=$(ansible_min_python_versions) PY_MAX_STR=$(ansible_max_python_versions) $(PYTHON_CMD) -c "import sys,os,ansible; py=sys.version_info[0:2]; ac=tuple(map(int,ansible.__version__.split('.')))[0:2]; py_min=eval(os.getenv('PY_MIN_STR'))[ac]; py_max=eval(os.getenv('PY_MAX_STR'))[ac]; pl=os.getenv('PL'); sys.stdout.write('true' if py>=py_min and py<=py_max else 'false')" 2>/dev/null)

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

# Directory for .done files
done_dir := done

# Defaults for end2end tests - must match the defaults in zhmcclient/testutils.
default_testinventory := $HOME/.zhmc_inventory.yaml
default_testvault := $HOME/.zhmc_vault.yaml
default_testhmc := default

# Flake8 options
flake8_opts := --max-line-length 160 --config /dev/null --ignore E402,E741,W503,W504

# PyLint config file
pylint_rc_file := .pylintrc

# PyLint additional options
pylint_opts := --disable=fixme

# Sanity test directory
# Note: 'ansible-test sanity' requires the collection to be tested to be
#       located in {...}/collections/ansible_collections/{namespace}/{name}.
#       The .git subtree must also be present.
#       There is issue https://github.com/ansible/ansible/issues/60215 that
#       discusses improving that.
#       We perform the sanity test in a temporary directory that contains the
#       content of the distribution archive and some additional files and
#       directories.
sanity_root_dir := tmp_sanity
sanity_coll_dir := $(sanity_root_dir)/collections/ansible_collections/ibm/ibm_zhmc

# Additional files and directories that need to go into the temporary sanity
# test directory
sanity_additional_files := \
    .git \
    .gitignore \
    galaxy.yml \

# Safety policy file (for packages needed for installation)
safety_install_policy_file := .safety-policy-install.yml
safety_develop_policy_file := .safety-policy-develop.yml

# Packages whose dependencies are checked using pip-missing-reqs
ifeq ($(python_m_n_version),3.9)
  check_reqs_packages := ansible pip_check_reqs pytest coverage coveralls flake8 sphinx ansible_doc_extractor pylint safety bandit ansible_test
else ifeq ($(python_m_n_version),3.10)
  check_reqs_packages := ansible pip_check_reqs pytest coverage coveralls flake8 sphinx ansible_doc_extractor pylint safety bandit ansible_test ansiblelint
else ifeq ($(python_m_n_version),3.11)
  check_reqs_packages := ansible pip_check_reqs pytest coverage coveralls flake8 sphinx ansible_doc_extractor pylint safety bandit ansible_test ansiblelint
else
# sphinx is excluded for Python >=3.12 because pip-missing-reqs 2.5 reports missing sphinx-versions package (rightfully)
  check_reqs_packages := ansible pip_check_reqs pytest coverage coveralls flake8 ansible_doc_extractor pylint safety bandit ansible_test ansiblelint
endif

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

# The files in the distribution archive, in addition to dynamically created files
# such as MANIFEST.json and FILES.json.
# Must be in sync with the build_ignore list in galaxy.yml
dist_files := \
    README.md \
    CHANGELOG.rst \
    SECURITY.md \
    bindep.txt \
    requirements.txt \
    collections/requirements.yml \
    $(wildcard meta/*) \
    $(wildcard tests/sanity/*.txt) \
    tests/config.yml \
    $(src_py_files) \

# Files the build of the distribution archive depends upon
dist_dependent_files := \
    $(dist_files) \
    galaxy.yml \

# Sphinx options (besides -M)
sphinx_opts := -v

# Pytest options
coverage_rc_file := .coveragerc
ifdef TESTCASES
  pytest_opts := --color=yes -s $(TESTOPTS) -k "$(TESTCASES)"
else
  pytest_opts := --color=yes -s $(TESTOPTS)
endif
# Note: The --cov-report=html option creates an HTML coverage report in the htmlcov
#       directory, but it is incorrect in case the coverage data file is appended
#       to. The 'coverage html' command fixes that.
pytest_cov_opts := --cov $(src_py_dir) --cov-append --cov-config $(coverage_rc_file) --cov-report=html

# No built-in rules needed:
.SUFFIXES:
.SUFFIXES: .py .rst

.PHONY: help
help:
	@echo "Makefile for Ansible collection:     $(collection_full_name)"
	@echo "Collection version will be:          $(collection_version)"
	@echo "Currently active Python environment: Python $(python_m_n_version)"
	@echo "Valid targets are:"
	@echo "  install    - Install collection and its dependent Python packages"
	@echo "  develop    - Set up the development environment"
	@echo "  dist       - Build the collection distribution archive in: $(dist_dir)"
	@echo "  check      - Run flake8"
	@echo "  pylint     - Run PyLint on sources"
	@echo "  sanity     - Run Ansible sanity tests (includes pep8, pylint, validate-modules)"
	@echo "  ansible_lint - Run ansible-lint on distribution archive (and built it)"
	@echo "  safety     - Run safety for install and all"
	@echo "  bandit     - Run bandit checker"
	@echo "  check_reqs - Perform missing dependency checks"
	@echo "  docs       - Build the documentation for all enabled (docs/source/conf.py) versions in: $(doc_build_dir) using remote repo"
	@echo "  docslocal  - Build the documentation from local repo contents in: $(doc_build_local_dir)"
	@echo "  linkcheck  - Check links in documentation"
	@echo "  test       - Run unit and function tests (adds to coverage results)"
	@echo "  end2end_mocked - Run end2end tests using mocked environment (adds to coverage results)"
	@echo "  all        - Do all of the above"
	@echo "  end2end    - Run end2end tests using environment defined by TESTINVENTORY/TESTHMC (adds to coverage results)"
	@echo "  end2end_show - Show HMCs defined for end2end tests"
	@echo "  authors    - Generate AUTHORS.md file from git log"
	@echo "  upload     - Publish the collection to Ansible Galaxy"
	@echo "  uploadhub  - Publish the collection to Ansible AutomationHub"
	@echo "  clobber    - Remove any produced files"
	@echo "  platform   - Display the information about the platform as seen by make"
	@echo "  env        - Display the environment as seen by make"
	@echo "Environment variables:"
	@echo "  TESTCASES=... - Testcase filter for pytest -k (e.g. 'test_func' or 'test_mod.py')"
	@echo "  TESTOPTS=... - Additional options for pytest (e.g. '-x')"
	@echo "  TESTHMC=... - HMC group or host name in HMC inventory file to be used in end2end tests. Default: $(default_testhmc)"
	@echo "  TESTINVENTORY=... - Path name of HMC inventory file used in end2end tests. Default: $(default_testinventory)"
	@echo "  TESTVAULT=... - Path name of HMC vault file used in end2end tests. Default: $(default_testvault)"
	@echo "  PACKAGE_LEVEL - Package level to be used for installing dependent Python"
	@echo "      packages in 'install' and 'develop' targets:"
	@echo "        latest - Latest package versions available on Pypi"
	@echo "        ansible - Specific Ansible versions"
	@echo "        minimum - A minimum version as defined in minimum-constraints*.txt"
	@echo "      Optional, defaults to 'latest'."
	@echo "  PYTHON_CMD=... - Name of python command. Default: python"
	@echo "  PIP_CMD=... - Name of pip command. Default: pip"
	@echo "  GALAXY_TOKEN=... - Your Ansible Galaxy API token, required for upload (see https://galaxy.ansible.com/me/preferences)"
	@echo "  AUTOMATIONHUB_TOKEN=... - Your Ansible AutomationHub API token, required for upload (see https://cloud.redhat.com/ansible/automation-hub/token)"
	@echo "Invocation of ansible commands from within repo main directory:"
	@echo "  export ANSIBLE_LIBRARY="$(PWD)/$(module_py_dir);$$ANSIBLE_LIBRARY""
	@echo "  # currently: ANSIBLE_LIBRARY=$(ANSIBLE_LIBRARY)"
	@echo "  ansible-playbook playbooks/...."

.PHONY: all
all: install develop dist safety bandit check pylint sanity ansible_lint check_reqs docs docslocal linkcheck test end2end_mocked
	@echo "Makefile: $@ done."

.PHONY: platform
platform:
ifeq ($(PLATFORM),Linux)
	@echo "Makefile: Installing ld to get Linux distributions"
	$(PYTHON_CMD) -m pip -q install ld
endif
	@echo "Makefile: Platform information as seen by make:"
	@echo "Platform detected by Makefile: $(PLATFORM)"
	@$(PYTHON_CMD) -c "import platform; print(f'Platform detected by Python: {platform.platform()}')"
	@$(PYTHON_CMD) -c "import platform; print(f'HW platform detected by Python: {platform.machine()}')"
ifeq ($(PLATFORM),Linux)
	@$(PYTHON_CMD) -c "import ld; d=ld.linux_distribution(); print(f'Linux distro detected by ld: {d[0]} {d[1]}')"
endif
	@echo "Shell used for commands: $(SHELL)"
	@echo "Shell flags: $(.SHELLFLAGS)"
	@echo "Make version: $(MAKE_VERSION)"
	@echo "Python command name: $(PYTHON_CMD)"
	@echo "Python command location: $(shell $(WHICH) $(PYTHON_CMD))"
	@echo "Python version: $(python_m_n_version)"
	@echo "Pip command name: $(PIP_CMD)"
	@echo "Pip command location: $(shell $(WHICH) $(PIP_CMD))"
	@echo "Pip version: $(shell $(PIP_CMD) --version)"
	@echo "$(collection_name) collection version: $(collection_version)"
ifneq ($(ansible_core_version),)
	@echo "ansible-core version: $(ansible_core_version)"
endif
ifneq ($(run_sanity),)
	@echo "Run sanity tests: $(run_sanity)"
endif
ifneq ($(run_ansible_lint),)
	@echo "Run ansible lint check: $(run_ansible_lint)"
endif

.PHONY: env
env:
	@echo "Makefile: Environment variables as seen by make:"
	$(ENV)

.PHONY: install
install: _check_version $(done_dir)/install_$(pymn)_$(PACKAGE_LEVEL).done
	@echo "Makefile: $@ done."

.PHONY: develop
develop: _check_version $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done
	@echo "Makefile: $@ done."

.PHONY: docs
docs: _check_version $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done $(doc_build_dir)/index.html
	@echo "Makefile: $@ done."

.PHONY: linkcheck
linkcheck: _check_version $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done $(doc_rst_files)
	sphinx-build -b linkcheck $(sphinx_opts) $(doc_source_dir) $(doc_linkcheck_dir)
	@echo "Makefile: $@ done."

.PHONY: test
test: _check_version $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done
	bash -c 'PYTHONWARNINGS=default ANSIBLE_LIBRARY=$(module_py_dir) PYTHONPATH=. pytest $(pytest_cov_opts) $(pytest_opts) $(test_dir)/unit $(test_dir)/function'
	coverage html --rcfile $(coverage_rc_file)
	@echo "Makefile: $@ done."

.PHONY: check
check: _check_version $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done
	flake8 $(flake8_opts) $(src_py_dir) $(test_dir)
	@echo "Makefile: $@ done."

.PHONY: pylint
pylint: _check_version $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done $(pylint_rc_file) $(src_py_files) $(test_py_files)
	pylint $(pylint_opts) --rcfile=$(pylint_rc_file) --output-format=text $(src_py_files) $(test_py_files)
	@echo "Makefile: $@ done."

.PHONY: safety
safety: $(done_dir)/safety_develop_$(pymn)_$(PACKAGE_LEVEL).done $(done_dir)/safety_install_$(pymn)_$(PACKAGE_LEVEL).done
	@echo "Makefile: $@ done."

.PHONY: bandit
bandit: $(done_dir)/bandit_$(pymn)_$(PACKAGE_LEVEL).done
	@echo "Makefile: $@ done."

# The sanity check requires the .git directory to be present.
.PHONY:	sanity
sanity: _check_version $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done $(dist_file) $(sanity_additional_files)
	rm -rf $(sanity_root_dir)
	mkdir -p $(sanity_coll_dir)
	cp -R $(sanity_additional_files) $(sanity_coll_dir)
	tar -xf $(dist_file) --directory $(sanity_coll_dir)
ifeq ($(run_sanity),true)
	echo "Running ansible sanity test in the current Python env (using ansible-core $(ansible_core_version) and Python $(python_version))"
	bash -c "cd $(sanity_coll_dir); ansible-test sanity --verbose --truncate 0 --local"
else
	echo "Skipping ansible sanity test in the current Python env (using ansible-core $(ansible_core_version) and Python $(python_version))"
endif
ifeq ($(run_sanity),true)
	echo "Running ansible sanity test in its own virtual Python env (using ansible-core $(ansible_core_version) and Python $(python_version))"
	bash -c "cd $(sanity_coll_dir); ansible-test sanity --verbose --truncate 0 --venv --requirements"
else
	echo "Skipping ansible sanity test in its own virtual Python env (using ansible-core $(ansible_core_version) and Python $(python_version))"
endif
	@echo "Makefile: $@ done."

.PHONY:	ansible_lint
ansible_lint: _check_version $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done $(dist_file)
ifeq ($(run_ansible_lint),true)
	echo "Running ansible-lint on distribution archive (using ansible-core $(ansible_core_version) and Python $(python_version))"
	rm -rf $(dist_dir)/tmp
	mkdir -p $(dist_dir)/tmp
	tar -xf $(dist_file) --directory $(dist_dir)/tmp
	-bash -c "cd $(dist_dir)/tmp; ansible-lint --profile production -f pep8"
else
	echo "Skipping ansible-lint (using ansible-core $(ansible_core_version) and Python $(python_version))"
endif
	@echo "Makefile: $@ done."

.PHONY: check_reqs
check_reqs: _check_version $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done minimum-constraints-develop.txt minimum-constraints-install.txt requirements.txt
ifeq ($(PACKAGE_LEVEL),ansible)
	@echo "Makefile: Warning: Skipping the checking of missing dependencies for PACKAGE_LEVEL=ansible" >&2
else
	@echo "Makefile: Checking missing dependencies of this package"
	pip-missing-reqs $(src_py_dir) --requirements-file=requirements.txt
	pip-missing-reqs $(src_py_dir) --requirements-file=minimum-constraints-install.txt
	@echo "Makefile: Done checking missing dependencies of this package"
	@echo "Makefile: Checking missing dependencies of some development packages"
	bash -c "cat minimum-constraints-develop.txt minimum-constraints-install.txt >tmp_minimum-constraints.txt"
	@rc=0; for pkg in $(check_reqs_packages); do dir=$$($(PYTHON_CMD) -c "import $${pkg} as m,os; dm=os.path.dirname(m.__file__); d=dm if not dm.endswith('site-packages') else m.__file__; print(d)"); cmd="pip-missing-reqs $${dir} --requirements-file=tmp_minimum-constraints.txt"; echo $${cmd}; $${cmd}; rc=$$(expr $${rc} + $${?}); done; exit $${rc}
	rm tmp_minimum-constraints.txt
	@echo "Makefile: Done checking missing dependencies of some development packages"
endif
	@echo "Makefile: $@ done."

.PHONY:	end2end
end2end: _check_version $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done
	bash -c 'PYTHONWARNINGS=default ANSIBLE_LIBRARY=$(module_py_dir) PYTHONPATH=. TESTEND2END_LOAD=true pytest -v $(pytest_cov_opts) $(pytest_opts) $(test_dir)/end2end'
	@echo "Makefile: $@ done."

.PHONY:	end2end_show
end2end_show:
	bash -c "TESTEND2END_LOAD=true $(PYTHON_CMD) -c 'from zhmcclient.testutils import print_hmc_definitions; print_hmc_definitions()'"

# TODO: Enable rc checking again once the remaining issues are resolved
.PHONY:	end2end_mocked
end2end_mocked: _check_version $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done
	-bash -c 'PYTHONWARNINGS=default ANSIBLE_LIBRARY=$(module_py_dir) PYTHONPATH=. TESTEND2END_LOAD=true TESTINVENTORY=$(test_dir)/end2end/mocked_inventory.yaml TESTVAULT=$(test_dir)/end2end/mocked_vault.yaml pytest -v $(pytest_cov_opts) $(pytest_opts) $(test_dir)/end2end'
	coverage html --rcfile $(coverage_rc_file)
	@echo "Makefile: $@ done."

.PHONY: authors
authors: _check_version
	echo "# Authors of this project" >AUTHORS.md
	echo "" >>AUTHORS.md
	echo "Sorted list of authors derived from git commit history:" >>AUTHORS.md
	echo '```' >>AUTHORS.md
	git shortlog --summary --email | cut -f 2 | LC_ALL=C.UTF-8 sort >>AUTHORS.md
	echo '```' >>AUTHORS.md
	@echo "Makefile: $@ done."

.PHONY: upload
upload: _check_version $(dist_file)
ifneq ($(findstring dev,$(collection_version)),)
	$(error Error: A development version $(collection_version) of collection $(collection_full_name) cannot be published on Ansible Galaxy)
endif
ifndef GALAXY_TOKEN
	$(error Error: Environment variable GALAXY_TOKEN with your Galaxy API token is required for uploading to Ansible Galaxy - get one on https://galaxy.ansible.com/me/preferences)
endif
	@echo "==> This will publish collection $(collection_full_name) version $(collection_version) on Ansible Galaxy"
	@echo -n '==> Continue? [yN] '
	@bash -c 'read answer; if [[ "$$answer" != "y" ]]; then echo "Aborted."; false; fi'
	@echo ""
	ansible-galaxy collection publish --server https://galaxy.ansible.com/ --token $(GALAXY_TOKEN) $(dist_file)
	@echo "Done: Published collection $(collection_full_name) version $(collection_version) on Ansible Galaxy"
	@echo "Makefile: $@ done."

.PHONY: uploadhub
uploadhub: _check_version $(dist_file)
ifneq ($(findstring dev,$(collection_version)),)
	$(error Error: A development version $(collection_version) of collection $(collection_full_name) cannot be published on Ansible AutomationHub)
endif
ifndef AUTOMATIONHUB_TOKEN
	$(error Error: Environment variable AUTOMATIONHUB_TOKEN with your Ansible AutomationHub API token is required for uploading to Ansible AutomationHub - get one on https://cloud.redhat.com/ansible/automation-hub/token)
endif
	@echo "==> This will publish collection $(collection_full_name) version $(collection_version) on Ansible AutomationHub"
	@echo -n '==> Continue? [yN] '
	@bash -c 'read answer; if [[ "$$answer" != "y" ]]; then echo "Aborted."; false; fi'
	@echo ""
	@echo "Note: If the following upload fails, upload the collection manually as described in docs/source/development.rst"
	@echo ""
	ansible-galaxy collection publish --server https://console.redhat.com/api/automation-hub/ --token $(AUTOMATIONHUB_TOKEN) $(dist_file)
	@echo "Done: Published collection $(collection_full_name) version $(collection_version) on Ansible AutomationHub"
	@echo "Makefile: $@ done."

# The second rm command of each type is for files that were used before 1.0.0, to make it easier to switch.
.PHONY: clobber
clobber:
	rm -Rf .cache .pytest_cache $(sanity_root_dir) htmlcov $(doc_linkcheck_dir) $(doc_build_dir) $(doc_build_local_dir) tests/output build .tox *.egg-info *.done $(done_dir)/*.done
	rm -f .coverage MANIFEST MANIFEST.in AUTHORS ChangeLog
	find . -name "*.pyc" -delete -o -name "__pycache__" -delete -o -name "*.tmp" -delete -o -name "tmp_*" -delete
	@echo "Makefile: $@ done."

.PHONY: dist
dist: _check_version $(dist_file)
	@echo "Makefile: $@ done."

.PHONY: _check_version
_check_version:
ifeq (,$(collection_version))
	$(error Error: Collection version could not be determined)
else
	@true >/dev/null
endif

$(done_dir)/install_deps_$(pymn)_$(PACKAGE_LEVEL).done: Makefile $(done_dir)/base_$(pymn)_$(PACKAGE_LEVEL).done requirements.txt
	$(PYTHON_CMD) -m pip install $(pip_level_opts) $(pip_level_opts_new) -r requirements.txt
	echo "done" >$@

$(done_dir)/install_$(pymn)_$(PACKAGE_LEVEL).done: Makefile $(done_dir)/base_$(pymn)_$(PACKAGE_LEVEL).done $(done_dir)/install_deps_$(pymn)_$(PACKAGE_LEVEL).done $(dist_file) requirements.txt
	ansible-galaxy collection install --force $(dist_file)
	echo "done" >$@

$(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done: Makefile $(done_dir)/base_$(pymn)_$(PACKAGE_LEVEL).done tools/os_setup.sh requirements-develop.txt
	bash -c 'tools/os_setup.sh'
	$(PYTHON_CMD) -m pip install $(pip_level_opts) $(pip_level_opts_new) -r requirements-develop.txt
	echo "done" >$@

$(done_dir)/base_$(pymn)_$(PACKAGE_LEVEL).done: Makefile requirements-base.txt minimum-constraints-develop.txt minimum-constraints-install.txt
	rm -f $@
	@echo "Makefile: Installing/upgrading pip, setuptools and wheel with PACKAGE_LEVEL=$(PACKAGE_LEVEL)"
	$(PYTHON_CMD) -m pip install $(pip_level_opts) -r requirements-base.txt
	echo "done" >$@

$(done_dir)/safety_develop_$(pymn)_$(PACKAGE_LEVEL).done: Makefile $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done $(safety_develop_policy_file) minimum-constraints-develop.txt minimum-constraints-install.txt
	@echo "Makefile: Running Safety for development packages (and tolerate safety issues when RUN_TYPE is normal or scheduled)"
	rm -f $@
	bash -c "safety check --policy-file $(safety_develop_policy_file) -r minimum-constraints-develop.txt --full-report || test '$(RUN_TYPE)' == 'normal' || test '$(RUN_TYPE)' == 'scheduled' || exit 1"
	echo "done" >$@
	@echo "Makefile: Done running Safety for development packages"

$(done_dir)/safety_install_$(pymn)_$(PACKAGE_LEVEL).done: Makefile $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done $(safety_install_policy_file) minimum-constraints-install.txt
	@echo "Makefile: Running Safety for install packages (and tolerate safety issues when RUN_TYPE is normal)"
	rm -f $@
	bash -c "safety check --policy-file $(safety_install_policy_file) -r minimum-constraints-install.txt --full-report || test '$(RUN_TYPE)' == 'normal' || exit 1"
	echo "done" >$@
	@echo "Makefile: Done running Safety for install packages"

$(done_dir)/bandit_$(pymn)_$(PACKAGE_LEVEL).done: Makefile $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done
	@echo "Makefile: Running Bandit"
	rm -f $@
	bandit $(src_py_dir) -r -l
	echo "done" >$@
	@echo "Makefile: Done running Bandit"

$(dist_file): Makefile $(done_dir)/install_deps_$(pymn)_$(PACKAGE_LEVEL).done $(dist_dependent_files)
	mkdir -p $(dist_dir)
	ansible-galaxy collection build --output-path=$(dist_dir) --force .

$(module_rst_dir):
	mkdir -p $(module_rst_dir)

$(module_rst_dir)/%.rst: $(module_py_dir)/%.py $(module_rst_dir) $(doc_templates_dir)/module.rst.j2
	ansible-doc-extractor --template $(doc_templates_dir)/module.rst.j2 $(module_rst_dir) $(PWD)/$<

# .nojekyll file disables GitHub pages jekyll pre-processing
$(doc_build_dir)/index.html: Makefile $(doc_rst_files) $(doc_source_dir)/conf.py
	sphinx-versioning -l $(doc_source_dir)/conf.py build $(doc_source_dir) $(doc_build_dir) -- $(sphinx_opts)
	touch $(doc_build_dir)/.nojekyll

.PHONY: docslocal
docslocal: _check_version $(done_dir)/develop_$(pymn)_$(PACKAGE_LEVEL).done $(doc_rst_files) $(doc_source_dir)/conf.py
	rm -rf $(doc_build_local_dir)
	sphinx-build -b html $(sphinx_opts) $(doc_source_dir) $(doc_build_local_dir)
#	open $(doc_build_local_dir)/index.html
