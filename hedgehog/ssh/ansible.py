import collections
import pathlib
import re
import warnings

from typing import Dict

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
