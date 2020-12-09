"""
git rmb - select a branch to remove remote and locally.
"""
import argparse
import logging
import re
import sys

import hedgehog
from .. import Error, Print, menu
from . import common

log = None


def _init(parser, argv: list, /):
    # parser.add_argument(
    #     "-a",
    #     "--all",
    #     action="store_true",
    #     help="Show branches from remotes too.",
    # )
    parser.add_argument("--dryrun", action="store_true", help=argparse.SUPPRESS)
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
    branch = common.select_branch(include_remotes=True, title="Select branch to delete")
    if not branch:
        return

    for desc, name in branch.all:
        if (match := re.match(rf"..remotes/(\S*{branch.branch})\s", desc)) :
            log.debug("There seems to be a matching remote: %s", match[1])
            remote_branch = match[1].split("/", maxsplit=1)
            break
    else:
        remote_branch = None

    if remote_branch:
        git_args = ["push", remote_branch[0], f":{remote_branch[1]}"]
        if args.dryrun:
            git_args.insert(1, "--dry-run")
        if menu.confirm(
            "Delete remote branch '{}'? (git {})".format(
                branch.branch,
                " ".join(git_args),
            )
        ):
            common.print_git_command(git_args)
            print(common.git_command(*git_args))
    else:
        log.warning(
            "We don't have a record of the branch '%s' under remotes/ locally",
            branch.branch,
        )
        # TODO: Ask if user want to assume origin/<local branch name> and try anyway?

    main_branch = common.main_branch(branch.all)
    if branch.branch == main_branch:
        log.warning("will not delete your main branch %s", main_branch)
        return
    if branch.is_checked_out:
        common.git_command("checkout", main_branch)
    if menu.confirm(f"Delete local branch '{branch.branch}'?") and not args.dryrun:
        git_args = ["branch", "--delete", "--force", branch.branch]
        common.print_git_command(git_args)
        print(common.git_command(*git_args))


def main_wrap():
    """Called from script created at package install."""
    try:
        main()
    except Error as exc:
        Print.instance()(f"Error: {exc}", color="red")
        sys.exit(exc.retcode)


if __name__ == "__main__":
    main_wrap()
