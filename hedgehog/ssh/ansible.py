import collections
import logging
import os
import pathlib
import re
import stat
import tempfile
import textwrap
import warnings

from typing import Dict, Iterable, List

import yaml

from .. import Error

ANSIBLE_INVENTORY = pathlib.Path.home() / "inventory.yaml"

Host = collections.namedtuple("Host", "name, address")
log = logging.getLogger(__name__)


def get_inventory(*, path=None) -> Dict[str, Host]:
    """Get all hosts from inventory. If `path` is set to None, default
    will be used."""
    hosts = {}
    path = pathlib.Path(path) if path else ANSIBLE_INVENTORY
    log.debug("Read inventory: %s", path)
    try:
        with path.open() as fp:
            if path.name.endswith(("yaml", "yml")):
                return _get_inventory_yaml(fp)
            for line in fp:
                if (match := re.match(r"(^[\w.-]+)\s.*?\bansible_host=(\S+)", line)) :
                    if match[1] in hosts:
                        warnings.warn(f"Duplicate host {match[1]} in inventory")
                    hosts[match[1]] = Host(*match.groups())
    except OSError as err:
        raise Error(f"Failed to read inventory: {err}") from err
    return hosts


def _get_inventory_yaml(file_):
    hosts = {}
    inventory = yaml.safe_load(file_)
    for group in inventory["all"]["children"].values():
        for name, hvars in group["hosts"].items():
            try:
                hosts[name] = Host(name, hvars["ansible_host"])
            except KeyError:
                log.debug("Host %s has no ansible_host key", name)
    return hosts


def write_ssh_config(ssh_config: pathlib.Path, inventory: Iterable[Host], /):
    path = pathlib.Path(ssh_config).expanduser()
    lines = []
    for host in inventory:
        extra = ""
        if "el6" in host.name.lower():
            extra = "PubkeyAcceptedKeyTypes ssh-rsa"
        lines.append(
            textwrap.dedent(
                f"""\
                Host {host.name}
                    Hostname {host.address}
                    User root
                    {extra}
                Host {host.name}-tunnel
                    Hostname {host.address}
                    User root
                    LocalForward 13306 localhost:3306
                    {extra}
                """
            )
        )
    path.write_text("\n".join(lines))


def write_hosts_file(inventory: List[Host], hosts: pathlib.Path, domain: str = None):
    """Write host/address pairs to /etc/hosts from ansible inventory."""
    delimiters = (
        "# --- hedgehog managed start ---",
        "# --- hedgehog managed end ---",
    )
    if domain:
        our_lines = [f"{h.address} {h.name} {h.name}.{domain}" for h in inventory]
    else:
        our_lines = [f"{h.address} {h.name}" for h in inventory]
    if not our_lines:
        log.warning("Inventory seems empty, not writing anything.")
        return

    data = hosts.read_text()
    new = []
    in_block = False
    for line in data.splitlines():
        if line == delimiters[0]:
            in_block = True
            new.append(line)
        elif line == delimiters[1]:
            in_block = False
            new += our_lines
            our_lines = []
            new.append(line)
        elif in_block:
            log.debug("old entry: %s", line)
        else:
            new.append(line)
    assert not in_block
    assert len(new)
    if our_lines:
        new.append(delimiters[0])
        new += our_lines
        new.append(delimiters[1])
    new_data = "\n".join(new) + "\n"
    try:
        hosts.write_text(new_data)
    except PermissionError:
        tempfd, tempname = tempfile.mkstemp()
        log.warning(
            "Need super user privileges to write to %s, writing to %s instead",
            hosts,
            tempname,
        )
        os.chmod(tempfd, stat.S_IRUSR | stat.S_IWUSR | stat.S_IROTH)
        with open(tempfd, "w") as f:
            f.write(new_data)
        return tempname
    else:
        log.info("Wrote inventory of %d online hosts to %s", len(inventory), hosts)
        return None
