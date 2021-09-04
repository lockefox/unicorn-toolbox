SHELL := /bin/bash

-include secret.env 
PROJECT_NAME = unicorn-toolbox
VERSION = $(strip $(shell cat VERSION))

.PHONY: clean
clean:
	-@find . -type d -maxdepth 3 -name ".eggs" -print0 | xargs -0 rm -rv
	-@find . -type d -maxdepth 3 -name ".tox" -print0 | xargs -0 rm -rv
	-@find . -type d -maxdepth 3 -name "__pycache__" -print0 | xargs -0 rm -rv
	-@find . -type d -maxdepth 3 -name "egg.info" -print0 | xargs -0 rm -rv
	rm -rf dist .python-version build
	coverage erase

WHICH_PYTHON = .venv/bin/python
WHICH_PIP = .venv/bin/pip
.venv: 
	python3 -m venv .venv
	$(WHICH_PIP) install -e .[dev]

dist/$(PROJECT_NAME)-$(VERSION).tar.gz: VERSION setup.py
	$(WHICH_PYTHON) setup.py sdist

dist/$(subst -,_,$(PROJECT_NAME))-$(VERSION)-*.whl: VERSION setup.py
	$(WHICH_PYTHON) setup.py bdist_wheel

.PHONY: build
build: dist/$(PROJECT_NAME)-$(VERSION).tar.gz dist/$(subst -,_,$(PROJECT_NAME))-$(VERSION)-*.whl

TOX_ARGS = 
.PHONY: test
test: test-env
	tox ${TOX_ARGS}

PYENV_LIST = 3.9.7 3.8.12 3.7.11
.PHONY: install-env
install-env:
	for py_ver in ${PYENV_LIST} ; do \
		pyenv install $$py_ver ; \
	done

.PHONY: test-env
test-env: .python-version
	pyenv local ${PYENV_LIST}


.venv/bin/black:
	$(WHICH_PIP) install black

BLACK_ARGS =
.PHONY: black
black: .venv/bin/black
	black ${BLACK_ARGS} . 