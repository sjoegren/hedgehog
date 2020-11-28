"""
This is only for running in dev environment.
"""
import argparse
import logging
import sys
import os
import pathlib
import re

import toml

from . import init, Print, Logger, Error

PROJECT_FILE = pathlib.Path.cwd() / "pyproject.toml"
INSTALLER = pathlib.Path.cwd() / "install-hedgehog.bash"
cprint = None
log = None


def _init(parser, argv: list, /):
    parser.add_argument("--dryrun", action="store_true", help=argparse.SUPPRESS)
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
        default_loglevel="WARNING",
        argp_kwargs=dict(description=__doc__),
    )
    global log
    log = logging.getLogger("tool")
    cprint = Print.instance()

    settings = toml.load(args.pyproject)

    log.debug_obj(settings, "pyproject settings")
    return

    update_installer(INSTALLER, settings)

    # p("red", "red")
    # p("green", "green")
    # p("yellow", "yellow")
    # p("blue", "blue")
    # p("magenta", "magenta")
    # p("cyan", "cyan")


def update_installer(installer_path, settings):
    data = installer_path.read_text()
    if not (
        m := re.search(
            r"(\d+)\.(\d+)", data["tool"]["poetry"]["dependencies"]["python"]
        )
    ):
        raise Error("couldn't find python version in settings")
    # re.sub(r"^MIN_VERSION_MINOR=\d+"


if __name__ == "__main__":
    try:
        main()
    except Error as exc:
        Print.instance()(f"Error: {exc}", color="red")
        sys.exit(exc.retcode)
