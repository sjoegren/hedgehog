"""
git fixup - display a menu with commits to choose from to create a fixup commit.
"""
import argparse
import logging
import os
import queue
import subprocess
import sys
import threading
import time

from simple_term_menu import TerminalMenu

import hedgehog
from .. import Error, Print

log = None


def _init(parser, argv: list, /):
    parser.add_argument(
        "-n",
        "--max-count",
        help="Number of commits to show in menu, default: %(default)s.",
        default="10",
    )
    args, remainder = parser.parse_known_args(argv)
    setattr(args, "remainder", remainder)
    return args


def main(*, cli_args: str = None):
    args = hedgehog.init(
        _init,
        arguments=cli_args,
        logger=True,
        argp_kwargs=dict(
            description=__doc__, usage="%(prog)s [opts] [git-commit args]"
        ),
    )
    global log
    log = logging.getLogger(args.prog_name)
    log.debug(args)
    commits = [
        (c, c.split(maxsplit=1)[0])
        for c in git_command("log", "--oneline", "--decorate", "-n", args.max_count)
    ]
    log.debug_obj(commits, "Commits")
    menu = TerminalMenu(
        ("|".join(c) for c in commits),
        preview_command="git show {}",
        cycle_cursor=False,
        clear_screen=True,
        preview_size=0.7,
    )
    index = menu.show()
    if index is None:
        return
    log.debug("Selected index: %s, commit: %s", index, commits[index])
    git_command(
        "commit",
        *args.remainder,
        "--fixup",
        commits[index][1],
        printer=Print.instance(),
    )


def git_command(*args, printer=None):
    cmd = ["git"] + list(args)
    log.debug("run command: %s", " ".join(cmd))
    if printer:
        printer("Running: ", color="yellow", end="")
        printer(" ".join(cmd), color="green")
    proc = subprocess.run(
        ["git"] + list(args),
        text=True,
        # check=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        log.debug("stdout: %s, stderr: %s", proc.stdout, proc.stderr)
        raise Error(
            "%s %s",
            proc.stdout,
            proc.stderr,
            retcode=proc.returncode,
        )
    return proc.stdout.strip().splitlines()


def main_wrap():
    """Called from script created at package install."""
    try:
        main()
    except Error as exc:
        Print.instance()(f"Error: {exc}", color="red")
        sys.exit(exc.retcode)


if __name__ == "__main__":
    main_wrap()
