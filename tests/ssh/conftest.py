import io
import pytest
import textwrap

from unittest.mock import MagicMock

from hedgehog.ssh import ansible


@pytest.fixture(autouse=True)
def inventory(monkeypatch):
    mock_path = MagicMock()
    inventory = io.StringIO(
        textwrap.dedent(
            """\
    [localservers]
    host1 ansible_host=192.0.2.1

    [remotes]
    remote.example.com ansible_host=198.51.100.1
    """
        )
    )
    mock_path.open.return_value = inventory
    monkeypatch.setattr(ansible, "ANSIBLE_INVENTORY", mock_path)
    return inventory
