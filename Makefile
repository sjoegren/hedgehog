BUILD_DIR = dist
PYTHON_PKG = hedgehog
TESTDIR = tests

# Check if we're called from a git hook
ifdef GIT_AUTHOR_NAME
	export PYTEST_ADDOPTS = -q -m "not integration"
else
	BLACK_OPTS = --diff --color
endif

.PHONY: all build test unittest check-format flake8 clean clean-env black githook help

all: test build

build:
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

clean-env:
	poetry env info -p && poetry env remove python || :

githook: .git/hooks/post-commit
	@test -e $< || (echo "#!/bin/sh" > $<; chmod +x $<)
	@grep -q "^make test" $< && (echo "$@ already installed"; exit 1)
	echo "make test" >> $<

help:
	@perl -lne 'print $$1 if /^([a-z][\w-]+).*:/' $(lastword $(MAKEFILE_LIST)) | sort
