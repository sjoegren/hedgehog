import collections
import pathlib
import re
import textwrap
import warnings

from typing import Dict, Iterable

from .. import Error

ANSIBLE_INVENTORY = pathlib.Path.home() / ".ansible-inventory"

Host = collections.namedtuple("Host", "name, address")


def get_inventory(*, inventory=None) -> Dict[str, Host]:
    """Get all hosts from inventory. If `inventory` is set to None, default
    will be used."""
    hosts = {}
    inventory = pathlib.Path(inventory) if inventory else ANSIBLE_INVENTORY
    try:
        with inventory.open() as fp:
            for line in fp:
                if (match := re.match(r"(^[\w.-]+)\s.*?\bansible_host=(\S+)", line)) :
                    if match[1] in hosts:
                        warnings.warn(f"Duplicate host {match[1]} in inventory")
                    hosts[match[1]] = Host(*match.groups())
    except OSError as err:
        raise Error(f"Failed to read inventory: {err}") from err
    return hosts


def write_ssh_config(ssh_config: str, inventory: Iterable[Host], /):
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
