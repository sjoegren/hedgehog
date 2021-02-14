#!/bin/bash
# Install the hedgehog package in a virtualenv in $HOME/.local/hedgehog
# Optional environment variables:
# - INSTALL_DIR:	to specify custom install directory.
# - BASH_DIR:		if set, install files to load into your environment in BASH_DIR.

set -uo pipefail

INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/hedgehog}"
PACKAGE="${PACKAGE:-git+https://github.com/akselsjogren/hedgehog.git#egg=hedgehog}"
MIN_VERSION_MAJOR=3
MIN_VERSION_MINOR=9
STATUS_PYTHON_OK=0
STATUS_PYTHON_NOK=3
STATUS_PYTHON_PYENV=4
ENV_PYTHON="$INSTALL_DIR/bin/python"
BASH_DIR="${BASH_DIR:-}"
INSTALL_DIR=$(realpath "$INSTALL_DIR")

set -e  # shopt returns false on unset option, therefore wait until here with -e

log() {
	label=$1; shift
	echo -e "[$label]: $*" >&2
}
debug() {
	if [ -n "${HHDEBUG:-}" ]; then
		log "DEBUG" "$@"
	fi
}
error() {
	log "ERROR" "$@"
	exit 1
}
info() {
	log "INFO" "$@"
}

hash python3 || error "No python interpreter"

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
	$STATUS_PYTHON_PYENV)
		python="$PYENV_ROOT/versions/$output/bin/python"
		info "Found suitable Python version in pyenv: $python"
		test -x "$python"
		;;
	*)
		error "Could not find a Python version installed that meets the minimum version $MIN_VERSION_MAJOR.$MIN_VERSION_MINOR\nCannot continue installation."
		;;
esac

if [ -e "$INSTALL_DIR" ]; then
	if [ "${1:-}" != "--force" ]; then
		error "$INSTALL_DIR already exists. Use the --force to remove it."
	fi
	# Sanity check length of install dir to avoid rm -rf something important as root.
	info "Removing $INSTALL_DIR"
	test ${#INSTALL_DIR} -gt 10 || error "invalid INSTALL_DIR: $INSTALL_DIR"
	test -w "$INSTALL_DIR" || error "$INSTALL_DIR is not writable"
	rm -rf "$INSTALL_DIR"
fi

info "Using $(command -v $python): $(command $python -V)"
info "Installing $PACKAGE into $INSTALL_DIR"

debug $python -m venv "$INSTALL_DIR"
$python -m venv "$INSTALL_DIR"
debug $ENV_PYTHON -m pip --isolated -q install -U pip
$ENV_PYTHON -m pip --disable-pip-version-check --isolated -q install --no-warn-script-location -U pip

debug $ENV_PYTHON -m pip --isolated -q install --use-pep517 --upgrade "$PACKAGE"
$ENV_PYTHON -m pip --isolated -q install --no-warn-script-location --use-pep517 --upgrade "$PACKAGE"

# Make the bash files
bash_src=$(find $INSTALL_DIR/lib -type d -name bash -print -quit)
debug "Distributed bash dir: $bash_src"
test -n "$bash_src" && test -d "$bash_src"
mkdir $INSTALL_DIR/bash
shopt -s nullglob
file_list=("$bash_src"/*.m4)
shopt -u nullglob
for file in ${file_list[*]}; do
    dest="$INSTALL_DIR/bash/$(basename "$file" .m4)"
    if ! type m4 > /dev/null 2>&1; then
        error "$file: m4 not installed"
        continue
    fi
    debug m4 -D INSTALL_DIR="$INSTALL_DIR" "$file" > "$dest"
    m4 -D INSTALL_DIR="$INSTALL_DIR" "$file" > "$dest"
    info "Installed $dest"
done

# If $BASH_DIR is specified, install bash files into that directory.
if [ -n "$BASH_DIR" ]; then
    shopt -s nullglob
	file_list=("$INSTALL_DIR/bash"/*)
    shopt -u nullglob
    for file in ${file_list[*]}; do
        debug install -v -m 644 -b -S.bak -D -p -t "$BASH_DIR" "$file"
        install -v -m 644 -b -S.bak -D -p -t "$BASH_DIR" "$file"
    done
fi

hash -r
version=$(hedgehog --version | awk '$1 == "hedgehog" { print $2 }')
info "Successfully installed version $version. Make sure '$INSTALL_DIR/bin' is in PATH."
