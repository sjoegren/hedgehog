import collections
import logging
import re
import subprocess

from typing import Optional

from simple_term_menu import TerminalMenu

from .. import Error, Print

Branch = collections.namedtuple("Branch", "branch, all, index, is_checked_out")


def git_command(*args):
    """Run `git *args` and return stdout."""
    log = logging.getLogger(__name__)
    cmd = ["git"] + args[0] if isinstance(args[0], list) else ["git"] + list(args)
    log.debug("run command: %s", cmd)
    proc = subprocess.run(cmd, text=True, capture_output=True)
    log.debug("stdout: %s, stderr: %s", proc.stdout, proc.stderr)
    if proc.returncode != 0:
        raise Error(
            "%s\n%s",
            proc.stdout,
            proc.stderr,
            retcode=proc.returncode,
        )
    return proc.stdout


def select_branch(
    *, include_remotes=False, title=None, preview=True
) -> Optional[Branch]:
    """Display a menu of git branches and return the selected branch name, or None."""
    log = logging.getLogger(__name__)
    args = ["branch", "--list", "--no-color", "--verbose"]
    if include_remotes:
        args.append("--all")
    lines = git_command(*args).splitlines()
    log.debug_obj(lines, "git branch output")
    branches = []
    checked_out_branch = None
    for i, line in enumerate(lines):
        if match := re.match(r"(.).(?:remotes/)?(\S+)", line):
            branches.append((line, match[2]))
            if match[1] == "*":
                checked_out_branch = i
    log.debug_obj(branches, "menu data")

    extra_args = {}
    if preview:
        extra_args = dict(
            preview_command="git log -3 {}",
            preview_size=0.7,
        )

    menu = TerminalMenu(
        ("|".join(b) for b in branches),
        cycle_cursor=False,
        show_search_hint=True,
        title=title,
        **extra_args,
    )
    index = menu.show()
    if index is None:
        return None
    log.debug("Selected index: %s, branch: %s", index, branches[index])
    return Branch(branches[index][1], branches, index, index == checked_out_branch)


def main_branch(branchlist) -> str:
    """Return the (index, name) of the main branch."""
    for i, (desc, name) in enumerate(branchlist):
        if name in ("master", "main"):
            return i, name
    raise Error("Cannot find any main branch in given list.")


def print_git_command(git_args: list, /, extra=None):
    cprint = Print.instance()
    cprint("Running: ", color="yellow", end="")
    cprint("git " + " ".join(git_args), color="green", attrs=["bold"], end="")
    if extra:
        print(extra, end="")
    print()
