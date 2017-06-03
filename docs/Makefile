# ------------------------------------------------------------------------------
# Makefile for docs of zhmc-ansible-modules project
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
# Environment variables:
#   PYTHON_CMD: Python command to use (OS-X needs to distinguish Python 2/3)
# ------------------------------------------------------------------------------

# Python / Pip commands
ifndef PYTHON_CMD
  PYTHON_CMD := python
endif
ifndef PIP_CMD
  PIP_CMD := pip
endif

# Determine OS platform make runs on
ifeq ($(OS),Windows_NT)
  PLATFORM := Windows
else
  # Values: Linux, Darwin
  PLATFORM := $(shell uname -s)
endif

# Build directory
build_dir := ../build

# Directory tree with our Ansible module source files
ansible_dir := ../ansible

# Our Ansible module source files
ansible_py_files := \
    $(wildcard $(ansible_dir)/*.py) \
    $(wildcard $(ansible_dir)/*/*.py) \
    $(wildcard $(ansible_dir)/*/*/*.py) \

# Directory for documentation sources (.rst files)
doc_dir := .
doc_gen_dir := $(doc_dir)/gen

# Directory for generated documentation
doc_build_dir := $(build_dir)/docs

# Git repo of Ansible project (remote URL and cloned repo)
ansible_repo_url := git://github.com/ansible/ansible.git
ansible_repo_dir := ../../ansible

# Stuff from repo of Ansible project
ar_template_dir := $(ansible_repo_dir)/docs/templates
ar_bin_dir := $(ansible_repo_dir)/docs/bin
ar_lib_dir := $(ansible_repo_dir)/lib
ar_plugin_formatter := $(ar_bin_dir)/plugin_formatter.py
ar_plugin_template := $(ar_template_dir)/plugin.rst.j2
ar_keyword_dumper := $(ar_bin_dir)/dump_keywords.py
ar_keyword_template := $(ar_template_dir)/playbooks_keywords.rst.j2
ar_keyword_desc := $(ansible_repo_dir)/docs/docsite/keyword_desc.yml

# Documentation generator command
sphinx := sphinx-build
sphinx_conf_dir := $(doc_dir)
sphinx_opts := -v -d $(doc_build_dir)/doctrees -c $(sphinx_conf_dir)

# Dependents for Sphinx documentation build
doc_dependent_files := \
    $(sphinx_conf_dir)/conf.py \
    $(wildcard $(doc_dir)/*.rst) \
    $(ansible_py_files) \

# No built-in rules needed:
.SUFFIXES:

.PHONY: help
help:
	@echo 'Makefile for docs'
	@echo 'Valid targets are:'
	@echo '  docs       - Build the documentation in: $(doc_build_dir)'
	@echo '  linkcheck  - Check links in documentation'
	@echo 'Environment variables:'
	@echo '  PYTHON_CMD=... - Name of python command. Default: python'

.PHONY: docs
docs: $(doc_build_dir)/html/index.html
	@echo '$@ done.'

.PHONY: linkcheck
linkcheck: $(doc_build_dir)/linkcheck/output.txt
	@echo '$@ done.'

$(doc_gen_dir)/playbooks_keywords.rst: $(ar_keyword_dumper) $(ar_keyword_template) $(ar_keyword_desc)
	mkdir -p $(doc_gen_dir)
	PYTHONPATH=$(ar_lib_dir) $(ar_keyword_dumper) --template-dir=$(ar_template_dir) --output-dir=$(doc_gen_dir)/ -d $(ar_keyword_desc)

$(doc_gen_dir)/modules_by_category.rst: $(ar_plugin_formatter) $(ar_plugin_template) $(ansible_py_files)
	mkdir -p $(doc_gen_dir)
	PYTHONPATH=$(ar_lib_dir) $(ar_plugin_formatter) -vv -t rst --template-dir=$(ar_template_dir) --module-dir=$(ansible_dir)/modules -o $(doc_gen_dir)/

staticmin:
	cat _themes/srtd/static/css/theme.css | sed -e 's/^[    ]*//g; s/[      ]*$$//g; s/\([:{;,]\) /\1/g; s/ {/{/g; s/\/\*.*\*\///g; /^$$/d' | sed -e :a -e '$$!N; s/\n\(.\)/\1/; ta' > _themes/srtd/static/css/theme.min.css

$(doc_build_dir)/html/index.html: Makefile $(doc_dependent_files) $(doc_gen_dir)/playbooks_keywords.rst $(doc_gen_dir)/modules_by_category.rst
	rm -fv $@
	mkdir -p $(doc_build_dir)
	$(sphinx) -b html $(sphinx_opts) $(doc_dir) $(doc_build_dir)/html
	@echo "Done: Created the HTML pages with top level file: $@"

$(doc_build_dir)/linkcheck/output.txt: Makefile $(doc_dependent_files)
	$(sphinx) -b linkcheck $(sphinx_opts) $(doc_dir) $(doc_build_dir)/linkcheck
	@echo
	@echo "Done: Look for any errors in the above output or in: $(doc_build_dir)/linkcheck/output.txt"

