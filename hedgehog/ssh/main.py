"""
SSH to hostnames in an ansible-inventory using "ansible_host" address instead
of name resolution.

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
import logging
import os
import pathlib
import queue
import subprocess
import sys
import threading
import time

from typing import List

import yaml

import hedgehog
from . import ansible
from .. import Error, Print

log = None


def _init(parser, argv: list, /):
    parser.add_argument(
        "--config",
        default=str(hedgehog.CONFIG_DIR / "ssh.yaml"),
        help="Config file (default: %(default)s)",
    )
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
        "required, leave host empty is target spec.",
    )
    parser.add_argument(
        "-c",
        "--remote-cmd",
        metavar="FILE",
        help="Execute remote command read from FILE (- to read from stdin), "
        "on target host",
    )
    parser.add_argument(
        "--copy-id", action="store_true", help="Run ssh-copy-id instead of ssh"
    )
    parser.add_argument(
        "-l", "--last", action="store_true", help="ssh to last target used"
    )
    parser.add_argument(
        "-L", "--list", action="store_true", help="List hosts in inventory"
    )
    parser.add_argument(
        "--ssh-config",
        action="store_true",
        help="Re-write host aliases to ssh_config from ansible "
        "inventory. Normally this is done automatically on each invocation.",
    )
    parser.add_argument(
        "--hosts-file", action="store_true", help="Write ansible hosts to /etc/hosts"
    )
    parser.add_argument("--dryrun", "--ip", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if (
        not (
            args.complete_hosts
            or args.last
            or args.list
            or args.ssh_config
            or args.hosts_file
        )
        and not args.sshargs
    ):
        parser.error("hostname argument or --last is required")
    return args


def main(*, cli_args: str = None):
    args = hedgehog.init(
        _init,
        arguments=cli_args,
        logger=True,
        argp_kwargs=dict(description=__doc__),
    )
    global log
    log = logging.getLogger(args.prog_name)
    cprint = Print.instance()
    cache_file = hedgehog.CACHE_DIR / "sshansible_last_host"
    hostname = None
    inventory = ansible.get_inventory(inventory=os.getenv("ANSIBLE_INVENTORY"))

    config_file = pathlib.Path(args.config).resolve()
    config = yaml.safe_load(config_file.read_bytes())
    append_host_domain_name = config["domain_name"]

    ssh_config = hedgehog.TEMP_DIR / "ssh_config"
    if inventory and (args.ssh_config or not ssh_config.exists()):
        log.info("Write inventory of %d hosts to %s", len(inventory), ssh_config)
        ansible.write_ssh_config(ssh_config, inventory.values())
    if args.ssh_config:
        return

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
    elif args.list:
        list_inventory(inventory, cache_file)
        return
    elif args.hosts_file:
        handle_hosts_file(
            [h for h, online in list_inventory(inventory, cache_file) if online],
            append_host_domain_name,
        )
        return

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
    exec_args = [command, "-o", f"Hostname={host.address}", *args.sshargs]

    if args.remote_cmd:
        return run_remote_command(args.remote_cmd, hostname, host.address, exec_args)

    cprint(f"exec: {' '.join(exec_args)}", "yellow", file=sys.stderr)
    sys.stdout.flush()
    if args.dryrun:
        print(host.address)
    else:
        os.execlp(command, *exec_args)


def handle_hosts_file(inventory: List[ansible.Host], append_domain: str):
    hosts_file = pathlib.Path("/etc/hosts")
    cprint = Print.instance()
    if (
        tempname := ansible.write_hosts_file(inventory, hosts_file, append_domain)
    ) is not None:
        log.debug(
            "Hosts were written to temp file %s instead, now run sudo to copy the "
            "file to %s",
            tempname,
            hosts_file,
        )
        cprint(f"Copy {tempname} to {hosts_file} via sudo", color="yellow")
        subprocess.run(
            ["sudo", "install", "-v", "-b", "--mode=644", tempname, str(hosts_file)],
            check=True,
        )


def host_status(task_q, result_q):
    """Return True if host is online, otherwise False."""
    host = task_q.get()
    log.debug("Processing host: %s", host)
    proc = subprocess.run(
        ["ping", "-c", "1", "-W", "0.5", "-q", host.address],
        text=True,
        capture_output=True,
    )
    log.debug("%s returncode: %d", host, proc.returncode)
    result_q.put((threading.current_thread(), host, proc.returncode == 0))
    task_q.task_done()


def list_inventory(inventory, cache_file):
    task_q = queue.Queue()
    threads = []
    result_q = queue.Queue()
    for host in inventory.values():
        t = threading.Thread(target=host_status, args=(task_q, result_q))
        threads.append(t)
        task_q.put(host)
        t.start()
    maxhostlen = max(len(h.name) for h in inventory.values())
    print(
        "Hostname{padding}  Address          Status   URL".format(
            padding=" " * (maxhostlen - 8)
        )
    )
    try:
        lasthost = cache_file.read_text()
    except OSError:
        lasthost = None

    cprint = Print.instance()
    result = []
    # print hosts as soon as they are ready
    for _ in range(len(threads)):
        # Get the number of results as we've created threads.
        thread, host, status = result_q.get(timeout=5)
        thread.join()
        result.append((host, status))
        print(
            "{0:<{colwidth}}  {1:<15}  {2:<7}  https://{1}".format(
                cprint.colored(
                    "{:<{colwidth}}".format(host.name, colwidth=maxhostlen),
                    "cyan" if lasthost and host.name == lasthost else None,
                ),
                host.address,
                cprint.colored("{:<7}".format("online"), "green")
                if status
                else cprint.colored("{:<7}".format("offline"), "red"),
                colwidth=maxhostlen,
            )
        )
    assert threading.active_count() == 1
    return result


def run_remote_command(remote_cmd_file, hostname, address, exec_args):
    """Run the script in file remote_cmd_file on the remote host.

    First transfer the file to remote host with scp.
    Run the file with "sh", then remove the file and print any output.
    """
    assert os.path.exists(remote_cmd_file)
    if remote_cmd_file == "-":
        log.warning("read from stdin is not implemented")
        return False
    remote_tmp_file = "/tmp/sshansible_cmd_{}.sh".format(str(int(time.time())))
    log.info("Transfer %s to %s:%s", remote_cmd_file, address, remote_tmp_file)
    proc = subprocess.run(
        [
            "scp",
            "-o",
            f"Hostname={address}",
            remote_cmd_file,
            f"{hostname}:{remote_tmp_file}",
        ],
        text=True,
        check=True,
        capture_output=True,
    )
    log.info("Run %s on %s (%s)", remote_tmp_file, hostname, address)
    proc = subprocess.run(
        exec_args
        + [f"sh {remote_tmp_file}; ret=$?; rm -f {remote_tmp_file}; exit $ret"],
        text=True,
        capture_output=True,
    )
    cprint = Print.instance()
    if proc.stdout:
        cprint(">>>>> Remote stdout start <<<<<", "yellow")
        print(proc.stdout)
        cprint(">>>>> Remote stdout end <<<<<", "yellow")
    if proc.stderr:
        cprint(">>>>> Remote stderr start <<<<<", "red")
        print(proc.stderr)
        cprint(">>>>> Remote stderr end <<<<<", "red")
    print(f"Remote exit code: {proc.returncode}")
    if proc.returncode != 0:
        raise Error(
            "Remote command exited with non-zero code: %d",
            proc.returncode,
            retcode=proc.returncode,
        )


def main_wrap():
    try:
        main()
    except Error as exc:
        logging.getLogger(__name__).debug("", exc_info=True)
        Print.instance()(f"Error: {exc}", color="red")
        sys.exit(exc.retcode)
