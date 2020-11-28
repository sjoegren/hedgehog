"""
For development use.

Will update bash installer, README and some files.
"""
import argparse
import logging
import sys
import pathlib
import re
import subprocess

import toml

from . import init, Print, Error

PROJECT_FILE = pathlib.Path.cwd() / "pyproject.toml"
INSTALLER = pathlib.Path.cwd() / "install-hedgehog.bash"
cprint = None
log = None


def _init(parser, argv: list, /):
    parser.add_argument("-n", "--dryrun", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "--pyproject",
        metavar="FILE",
        type=pathlib.Path,
        default=PROJECT_FILE,
        help=f"Default: {PROJECT_FILE}",
    )
    args = parser.parse_args(argv)
    return args


def main(*, cli_args: str = None):
    args = init(
        _init,
        arguments=cli_args,
        logger=True,
        default_loglevel="INFO",
        argp_kwargs=dict(description=__doc__),
    )
    global log
    log = logging.getLogger("tool")
    settings = toml.load(args.pyproject)
    log.debug_obj(settings, "pyproject settings")
    update_installer(INSTALLER, settings, args)


def update_installer(installer_path, settings, args):
    data = installer_path.read_text()
    # Update minimum Python version to match pyproject settings
    match = re.search(
        r"(\d+)\.(\d+)", settings["tool"]["poetry"]["dependencies"]["python"]
    )
    if not match:
        raise Error("couldn't find python version in settings")
    log.info("Python version configured in project: %s", match.group(0))
    data, changes = re.subn(
        r"^(MIN_VERSION_MINOR=)\d+", rf"\g<1>{match[2]}", data, 1, re.M
    )
    if changes:
        log.info("Updated Python version to %s", match.group(0))

    # Update package git url with checked out branch
    proc = subprocess.run(
        ["git", "branch", "--show-current"], check=True, capture_output=True, text=True
    )
    branch = proc.stdout.strip()
    branch = "" if branch == "main" else f"@{branch}"
    data, changes = re.subn(
        r'^(PACKAGE=".+\.git).*(#egg.*")', rf"\g<1>{branch}\g<2>", data, 1, re.M
    )
    if changes:
        log.info("Updated package git url with branch '%s'", branch)

    if not args.dryrun:
        installer_path.write_text(data)
        log.info("Wrote back changes to %s", installer_path)


if __name__ == "__main__":
    try:
        main()
    except Error as exc:
        Print.instance()(f"Error: {exc}", color="red")
        sys.exit(exc.retcode)
