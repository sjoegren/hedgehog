"""
git fixup - display a menu with commits to choose from to create a fixup commit.
"""
import logging
import sys

from simple_term_menu import TerminalMenu

import hedgehog
from .. import Error, Print
from . import common

log = None


def _init(parser, argv: list, /):
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
    parser.add_argument(
        "-p",
        "--print-commit",
        action="store_true",
        help="Print commit id instead of issuing 'git commit --fixup'",
    )
    args, remainder = parser.parse_known_args(argv)
    setattr(args, "remainder", remainder)
    return args


def main(*, cli_args: str = None):
    global log
    args = hedgehog.init(
        _init,
        arguments=cli_args,
        logger=True,
        argp_kwargs=dict(
            description=__doc__, usage="%(prog)s [opts] [git-commit args]"
        ),
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

    if args.print_commit:
        print(commits[index][1])
        return

    git_args = [
        "commit",
        *args.remainder,
        args.commit_type,
        commits[index][1],
    ]
    common.print_git_command(git_args, f"   # ({commits[index][0]})")
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
