BUILD_DIR = dist
PYTHON_PKG = hedgehog
TESTDIR = tests
PYTHON_FILES = $(shell find . -name \*.py)

# Check if we're called from a git hook
ifdef GIT_AUTHOR_NAME
	export PYTEST_ADDOPTS = -q -m "not integration"
else
	BLACK_OPTS = --diff --color
endif

.PHONY: all build test unittest check-format flake8 clean clean-env black githook help

all: test build push-check

build:
	poetry run python -m hedgehog.tool
	poetry build

test: flake8 unittest check-format

unittest:
	poetry run pytest

black:
	poetry run black $(PYTHON_PKG) $(TESTDIR)

check-format:
	poetry run black --check $(BLACK_OPTS) $(PYTHON_PKG) $(TESTDIR)

flake8:
	poetry run flake8

check-poetry:
	@poetry run pytest --version &> /dev/null || \
		(echo "Installing poetry environment..."; poetry install)

clean:
	rm -rf $(BUILD_DIR)

push-check:
	poetry run python -m hedgehog.tool --color --check-clean
	poetry run python -m hedgehog.tool --color
	poetry run python -m hedgehog.tool --color --check-clean

clean-env:
	poetry env info -p && poetry env remove python || :

githook: .git/hooks/post-commit .git/hooks/pre-push

.git/hooks/post-commit: $(PYTHON_FILES)
	test -e $@ || (echo "#!/bin/sh" > $@; chmod +x $@)
	grep -q "^make test" $@ || echo "make test" >> $@

.git/hooks/pre-push: $(PYTHON_FILES)
	test -e $@ || (echo "#!/bin/sh" > $@; chmod +x $@)
	grep -q "^make push-check" $@ || echo "make push-check" >> $@

help:
	@perl -lne 'print $$1 if /^([a-z][\w-]+).*:/' $(lastword $(MAKEFILE_LIST)) | sort
