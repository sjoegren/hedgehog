"""
SSH to hostnames in an ansible-inventory file when using inventory's
"ansible_host" keys instead of name resolution.

Given an inventory file like this:

    [buildslaves]
    foo     ansible_host=192.0.2.1

Running 'sshansible.py -- -v foo', will exec the command:
  ssh -o Hostname=192.0.2.1 -v foo

That way any config in 'ssh_config' for host 'foo' will still be honored.

scp:
    sshansible.py --scp bar -- /etc/foo.conf bar:/tmp
"""

import argparse

import sys
import os

from . import ansible
from .. import init_args, init_wrap, Error, Print

cprint = None


def init(*parse_args):
    parser = init_args(description=__doc__)
    parser.add_argument("--complete-hosts", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "sshargs",
        nargs="*",
        metavar="arg",
        help="ssh arguments, like host from ansible inventory to connect to",
    )
    parser.add_argument(
        "--scp",
        nargs="?",
        const="last",
        metavar="hostname",
        help="Run scp instead of ssh, if used together with -l no hostname is "
        "requiredi, leave host empty is target spec.",
    )
    parser.add_argument(
        "--copy-id", action="store_true", help="Run ssh-copy-id instead of ssh"
    )
    parser.add_argument(
        "-l", "--last", action="store_true", help="ssh to last target used"
    )
    parser.add_argument("--dryrun", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(*parse_args)
    if not (args.complete_hosts or args.last) and not args.sshargs:
        parser.error("hostname argument or --last is required")
    global cprint
    cprint = Print.instance(args.color)
    return args


def main(*, cli_args: str = None):
    args = init_wrap(init, cli_args)
    cache_file = args.cache_dir / "sshansible_last_host"
    hostname = None
    inventory = ansible.get_inventory(inventory=os.getenv("ANSIBLE_INVENTORY"))
    if args.complete_hosts:
        print("\t".join(inventory.keys()))
        return True
    elif args.last:
        try:
            hostname = cache_file.read_text()
        except OSError:
            raise Error("Cannot use --last because cache file doesn't exist.")
        if not args.sshargs:
            args.sshargs.append(hostname)

    if not hostname:
        hostname = args.scp or args.sshargs[-1]

    # Allow empty hostname in scp src/dest specifications
    for i, arg in enumerate(args.sshargs):
        if arg.startswith(":"):
            args.sshargs[i] = f"{hostname}{arg}"

    try:
        host = inventory[hostname]
    except KeyError:
        raise Error("Couldn't find a host with name: %s", hostname)
    cache_file.write_text(hostname)

    command = "scp" if args.scp else "ssh-copy-id" if args.copy_id else "ssh"
    exec_args = (command, "-o", f"Hostname={host.address}", *args.sshargs)
    cprint(f"exec: {' '.join(exec_args)}", "yellow")
    sys.stdout.flush()
    if not args.dryrun:
        os.execlp(command, *exec_args)


def main_wrap():
    """Called from script created at package install."""
    try:
        main()
    except Error as exc:
        Print.instance()(f"Error: {exc}", color="red")
        sys.exit(exc.retcode)
