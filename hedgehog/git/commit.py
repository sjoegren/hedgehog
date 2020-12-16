"""
Display a menu of commits from the currently checked out branch.

* git fixup - display a menu with commits to choose from to create a fixup commit.
* git pv    - Preview commits and print selected commit id.
"""
import functools
import logging
import os
import subprocess
import sys
import tempfile

from simple_term_menu import TerminalMenu

import hedgehog
from .. import Error, Print
from . import common

log = None


def _init_fixup(parser, argv: list, /):
    parser.add_argument(
        "-n",
        "--max-count",
        help="Number of commits to show in menu, default: %(default)s.",
        default="10",
    )
    parser.add_argument(
        "-s",
        "--squash",
        action="store_const",
        dest="commit_type",
        default="--fixup",
        const="--squash",
        help="git commit --squash instead of --fixup",
    )
    args, remainder = parser.parse_known_args(argv)
    setattr(args, "remainder", remainder)
    return args


def fixup(*, cli_args: str = None, doc: str = None):
    global log
    args = hedgehog.init(
        _init_fixup,
        arguments=cli_args,
        logger=True,
        argp_kwargs=dict(description=doc, usage="%(prog)s [opts] [git-commit args]"),
    )
    log = logging.getLogger(args.prog_name)
    log.debug(args)
    lines = (
        common.git_command("log", "--oneline", "--decorate", "-n", args.max_count)
        .strip()
        .splitlines()
    )
    commits = [(line, line.split(maxsplit=1)[0]) for line in lines]
    log.debug_obj(commits, "Commits")
    menu = TerminalMenu(
        ("|".join(c) for c in commits),
        preview_command="git log -1 {}",
        cycle_cursor=False,
        preview_size=0.4,
        show_search_hint=True,
    )
    index = menu.show()
    if index is None:
        return
    log.debug("Selected index: %s, commit: %s", index, commits[index])

    git_args = [
        "commit",
        *args.remainder,
        args.commit_type,
        commits[index][1],
    ]
    common.print_git_command(git_args, f"   # ({commits[index][0]})")
    common.git_command(*git_args)


def _init_preview(parser, argv: list, /):
    parser.add_argument(
        "-n",
        "--max-count",
        help="Number of commits to show in menu, default: %(default)s.",
        default="20",
    )
    parser.add_argument(
        "-l",
        "--log-preview",
        action="store_true",
        help="Show preview of git log instead of patches.",
    )
    parser.add_argument(
        "-p",
        "--print",
        action="store_true",
        help="Print selected commit id instead of showing the patch.",
    )
    args, remainder = parser.parse_known_args(argv)
    setattr(args, "remainder", remainder)
    return args


def preview(*, cli_args: str = None, doc: str = ""):
    """Select and print commit, show preview of "git show" in full screen."""
    global log
    args = hedgehog.init(
        _init_preview,
        arguments=cli_args,
        logger=True,
        argp_kwargs=dict(
            description=doc,
            usage="%(prog)s [opts] [<revision range>] [[--] <path>...]",
        ),
    )
    log = logging.getLogger(args.prog_name)
    log.debug(args)
    git_args = [
        "log",
        "--oneline",
        "--decorate",
        "-n",
        args.max_count,
        *args.remainder,
    ]
    lines = common.git_command(*git_args).strip().splitlines()
    commits = [(line, line.split(maxsplit=1)[0]) for line in lines]
    log.debug_obj(commits, "Commits")

    def _preview_command(commit_id):
        if args.log_preview:
            return common.git_command("log", "-1", commit_id)
        return common.git_command(
            "show", "--color={}".format("always" if args.color else "never"), commit_id
        )

    menu = TerminalMenu(
        ("|".join(c) for c in commits),
        preview_command=_preview_command,
        cycle_cursor=False,
        preview_size=0.85,
        clear_screen=not args.print,
        show_search_hint=True,
    )
    index = menu.show()
    if index is None:
        return
    log.debug("Selected index: %s, commit: %s", index, commits[index])
    if args.print:
        print(commits[index][1])
        return
    tempfd, tempname = tempfile.mkstemp()
    subprocess.run(
        ["git", "show", commits[index][1]], text=True, stdout=tempfd, check=True
    )
    log.debug("'git show %s' written to %s", commits[index][1], tempname)
    subprocess.run(["bat", "--language", "Diff", tempname], text=True)
    os.remove(tempname)


def fixup_wrap():
    """Display a menu with commits to choose from to create a fixup commit."""
    _main_wrap(functools.partial(fixup, doc=fixup_wrap.__doc__))


def preview_wrap():
    """Preview commits and show or print selected commit."""
    _main_wrap(functools.partial(preview, doc=preview_wrap.__doc__))


def _main_wrap(main_func):
    try:
        rv = main_func()
    except Error as exc:
        Print.instance()(f"Error: {exc}", color="red")
        sys.exit(exc.retcode)
    else:
        if rv is not None:
            sys.exit(rv)
