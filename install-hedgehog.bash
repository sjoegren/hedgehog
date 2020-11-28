#!/bin/bash
# Install the hedgehog package in a virtualenv in $HOME/.local/hedgehog

set -uo pipefail

INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/hedgehog}"
PACKAGE="git+https://github.com/akselsjogren/hedgehog#egg=hedgehog"
#PACKAGE="git+https://github.com/akselsjogren/hedgehog.git@devel#egg=hedgehog"
MIN_VERSION_MAJOR=3
MIN_VERSION_MINOR=8
STATUS_PYTHON_OK=0
STATUS_PYTHON_NOK=3
STATUS_PYTHON_PYENV=4
ENV_PYTHON="$INSTALL_DIR/bin/python"
BASH_LINK_DIR="${BASH_LINK_DIR:-}"

if [ -n "${HHDEBUG:-}" ]; then
	set -x
fi

xtrace_level=$(shopt -op xtrace)
set -e  # shopt returns false on unset option, therefore wait until here with -e

log() {
	set +x
	label=$1; shift
	echo -e "[$label]: $*" >&2
	$xtrace_level
}
debug() {
	set +x
	if [ -n "${HHDEBUG:-}" ]; then
		log "DEBUG" "$@"
	fi
	$xtrace_level
}
error() {
	log "ERROR" "$@"
	exit 1
}
info() {
	log "INFO" "$@"
}

hash python3

# Check if we have a Python version >= minimum version.
# If current "python3" binary is new enough, use it.
# Else, look for pyenv installations use the latest installed version if it
# meets the minimum version.
set +e
output=$(python3 - <<EOF
import os, re, sys
from os.path import join, exists
MIN_VERSION = ($MIN_VERSION_MAJOR, $MIN_VERSION_MINOR, 0)
if sys.version_info >= MIN_VERSION:
	sys.exit($STATUS_PYTHON_OK)
root = os.getenv('PYENV_ROOT')
if not (root and exists(join(root, "versions"))):
	sys.exit($STATUS_PYTHON_NOK)
version_dir = os.path.join(root, "versions")
installed = [v for v in os.listdir(version_dir) if re.match(r'3\.\d+\.\d+', v)]
installed.sort(key=lambda v: tuple(int(n) for n in v.split('.')))
newest_installed = installed[-1]
if tuple(int(n) for n in newest_installed.split('.')) < MIN_VERSION:
	sys.exit($STATUS_PYTHON_NOK)
print(newest_installed)
sys.exit($STATUS_PYTHON_PYENV)
EOF
)
exit_code=$?
set -e

# Bail out if Python version is lower than min version.
case $exit_code in
	$STATUS_PYTHON_OK)
		debug "Python is new enough"
		python=python3
		;;
	$STATUS_PYTHON_NOK)
		error "Could not find a Python version installed that meets the minimum version $MIN_VERSION_MAJOR.$MIN_VERSION_MINOR\nCannot continue installation."
		exit 1
		;;
	$STATUS_PYTHON_PYENV)
		debug "Use PYENV_VERSION $output"
		python="$PYENV_ROOT/versions/$output/bin/python"
		test -x "$python"
esac

info "Using $(command -v $python): $(command $python -V)"
info "Installing into $INSTALL_DIR"
if [ -e "$INSTALL_DIR" ]; then
	info "$INSTALL_DIR already exists, attempting to upgrade."
	if ! $ENV_PYTHON -m pip -V > /dev/null; then
		error "Installation is borked, remove it manually and try again: $INSTALL_DIR"
		exit 1
	fi
else
	mkdir -pv "$INSTALL_DIR"
	info "Create virtual env at $INSTALL_DIR"
	$python -m venv "$INSTALL_DIR"
	info "Upgrade pip"
	$ENV_PYTHON -m pip --isolated -q install -U pip
fi
info "Install $PACKAGE"
$ENV_PYTHON -m pip --isolated -q install --use-pep517 --upgrade "$PACKAGE"
$xtrace_level

if [ -n "$BASH_LINK_DIR" ]; then
    bash_dir=$INSTALL_DIR/lib/python*/site-packages/bash
    test -d $bash_dir
    for file in $bash_dir/*; do
        info "Installing $file"
        ln -v -f -s $file $BASH_LINK_DIR/
    done
fi

version=$($ENV_PYTHON -m hedgehog)
info "Successfully installed version $version"

if ! echo $PATH | tr ':' '\n' | grep -q -F -x $INSTALL_DIR/bin; then
	echo "'$INSTALL_DIR/bin' doesn't seem to be in your PATH. Update with:"
	echo "export PATH=${PATH}:$INSTALL_DIR/bin"
fi
