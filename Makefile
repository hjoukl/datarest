.PHONY: clean-pyc clean-build clean

# System Python interpreter to use.
python ?= python
# Development virtualenv for installing build, test, package dependencies.
VENV := .venv/dev
# Shortcut to the pip in our dev venv.
PIP := ${VENV}/bin/pip
# Shortcut to the Python interpreter in our dev venv.
PYTHON := ${VENV}/bin/python
# The default publish target PyPI repo.
PYPI ?= testpypi

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "clean-bootstrap - remove bootstrapped dev venv"
	@echo "bootstrap - bootstrap dev venv"
	@echo "build - build"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "dist - package"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

clean-bootstrap:
	rm -fr ${VENV}

bootstrap:
	${python} -m venv ${VENV} 
	${PIP} install -r requirements/dev/dev-base-requirements.txt
	${PIP} install -r requirements/dev/dev-requirements.txt

build:
	${PYTHON} setup.py build

test:
	${PYTHON} setup.py test

test-all:
	tox

dist: clean
	${PYTHON} setup.py sdist
	${PYTHON} setup.py bdist_wheel
	ls -l dista

publish:
	${PYTHON} -m twine upload --repository ${PYPI} dist/* ${TWINE_FLAGS}
