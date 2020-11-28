import pytest

from unittest.mock import Mock

import hedgehog
from hedgehog.ssh import main


@pytest.fixture
def mock_exec(monkeypatch):
    m = Mock()
    monkeypatch.setattr("os.execlp", m)
    return m


@pytest.fixture(autouse=True)
def cache_file(tmp_path):
    """Remove cache file after each test case."""
    cache_file = tmp_path / "sshansible_last_host"
    yield cache_file
    if cache_file.exists():
        cache_file.unlink()


def test_main_complete_hosts(capsys):
    main.main(cli_args="--complete-hosts")
    assert capsys.readouterr().out == "host1\tremote.example.com\n"


def test_main_ssh(mock_exec, cache_file):
    main.main(cli_args="host1")
    assert mock_exec.called_once_with("ssh", "ssh", "-o", "Hostname=192.0.2.1", "host1")
    assert cache_file.read_text() == "host1", "host was not written to cache"


def test_main_ssh_unknown_host(capsys, mock_exec):
    with pytest.raises(hedgehog.Error, match=r"Couldn't find a host with name: foo"):
        main.main(cli_args="foo")


def test_main_ssh_last(mock_exec, cache_file):
    cache_file.write_text("remote.example.com")
    main.main(cli_args="--last")
    assert mock_exec.called_once_with(
        "ssh", "ssh", "-o", "Hostname=198.51.0.1", "remote.example.com"
    )


def test_main_scp(mock_exec):
    main.main(cli_args="--scp host1 localfile :/dir/")
    assert mock_exec.called_once_with(
        "scp", "scp", "-o", "Hostname=192.0.2.1", "localfile", "host1:/dir/"
    )


def test_main_ssh_copy_id_to_last(mock_exec):
    main.main(cli_args="--copy-id host1")
    assert mock_exec.called_once_with(
        "ssh-copy-id", "ssh-copy-id", "-o", "Hostname=192.0.2.1", "host1"
    )
