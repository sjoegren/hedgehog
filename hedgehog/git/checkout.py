"""
git cob - display a menu with branches to choose from to checkout.
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
    args = parser.parse_args(argv)
    return args


def main(*, cli_args: str = None):
    global log
    args = hedgehog.init(
        _init,
        arguments=cli_args,
        logger=True,
        argp_kwargs=dict(description=__doc__),
    )
    log = logging.getLogger(args.prog_name)
    log.debug(args)
    branch = common.select_branch(include_remotes=args.all)
    if not branch:
        return
    git_args = ["checkout", branch.branch]
    common.print_git_command(git_args)
    common.git_command(*git_args)


def main_wrap():
    """Called from script created at package install."""
    try:
        main()
    except Error as exc:
        Print.instance()(f"Error: {exc}", color="red")
        sys.exit(exc.retcode)


if __name__ == "__main__":
    main_wrap()
