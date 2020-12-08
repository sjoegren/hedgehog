import logging
import re
import subprocess

from simple_term_menu import TerminalMenu

from .. import Error, Print


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


def select_branch(*, include_remotes=False):
    """Display a menu of git branches and return the selected branch name, or None."""
    log = logging.getLogger(__name__)
    lines = git_command("branch", "--list", "--no-color", "--verbose").splitlines()
    log.debug_obj(lines, "git branch output")
    branches = []
    for line in lines:
        if (match := re.match(r"..(\S+)", line)) :
            branches.append((line, match[1]))
    log.debug_obj(branches, "menu data")
    menu = TerminalMenu(
        ("|".join(b) for b in branches),
        preview_command="git log -3 {}",
        cycle_cursor=False,
        preview_size=0.7,
    )
    index = menu.show()
    if index is None:
        return None
    log.debug("Selected index: %s, branch: %s", index, branches[index])
    return branches[index][1]


def print_git_command(git_args: list, /, extra=None):
    cprint = Print.instance()
    cprint("Running: ", color="yellow", end="")
    cprint("git " + " ".join(git_args), color="green", attrs=["bold"], end="")
    if extra:
        print(extra, end="")
    print()
