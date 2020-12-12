"""
Display a menu of branches from the current git repo.

* git cob       - checkout selected branch.
* git getbranch - print name of selected branch.
"""
import logging
import sys


import hedgehog
from .. import Error, Print
from . import common

log = None

# TODO: -b/--create to checkout local branch from remote/branch


def _init(parser, argv: list, /):
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Show branches from remotes too.",
    )
    parser.add_argument(
        "-P",
        "--no-preview",
        action="store_false",
        dest="preview",
        help="Don't show preview window in menu with latest commits.",
    )
    args = parser.parse_args(argv)
    return args


def _select_branch(doc, cli_args: str = None):
    global log
    args = hedgehog.init(
        _init,
        arguments=cli_args,
        logger=True,
        argp_kwargs=dict(description=doc),
    )
    log = logging.getLogger(args.prog_name)
    log.debug(args)
    return common.select_branch(include_remotes=args.all, preview=args.preview)


def cob(*, cli_args: str = None):
    branch = _select_branch(
        doc="git cob - display a menu with branches to choose from to checkout.",
        cli_args=cli_args,
    )
    if not branch:
        return 0
    git_args = ["checkout", branch.branch]
    common.print_git_command(git_args)
    common.git_command(*git_args)


def getbranch(*, cli_args: str = None):
    branch = _select_branch(
        doc="git getbranch - select a branch from a menu and print it.",
        cli_args=cli_args,
    )
    if not branch:
        return 1
    print(branch.branch)


def cob_wrap():
    """Called from script created at package install."""
    _main_wrap(cob)


def getbranch_wrap():
    """Called from script created at package install."""
    _main_wrap(getbranch)


def _main_wrap(main_func):
    try:
        rv = main_func()
    except Error as exc:
        Print.instance()(f"Error: {exc}", color="red")
        sys.exit(exc.retcode)
    else:
        if rv is not None:
            sys.exit(rv)
