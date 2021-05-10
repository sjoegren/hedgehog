import textwrap

from unittest.mock import MagicMock

from hedgehog.ssh import ansible


def test_get_inventory():
    hosts = ansible.get_inventory()
    assert hosts["host1"].name == "host1"
    assert hosts["host1"].address == "192.0.2.1"
    assert hosts["remote.example.com"].address == "198.51.100.1"


def test_write_ssh_config(tmp_path):
    inventory = [
        ansible.Host("foxtrot", "198.51.100.101"),
        ansible.Host("golf-el6", "198.51.100.102"),
    ]
    config = tmp_path / "ssh_config"
    ansible.write_ssh_config(config, inventory)
    expected = textwrap.dedent(
        """\
        Host foxtrot
            Hostname 198.51.100.101
            User root

        Host foxtrot-tunnel
            Hostname 198.51.100.101
            User root
            LocalForward 13306 localhost:3306


        Host golf-el6
            Hostname 198.51.100.102
            User root
            PubkeyAcceptedKeyTypes ssh-rsa
        Host golf-el6-tunnel
            Hostname 198.51.100.102
            User root
            LocalForward 13306 localhost:3306
            PubkeyAcceptedKeyTypes ssh-rsa
        """
    )
    assert config.read_text() == expected


def test_write_hosts_file_empty_file(tmp_path):
    inventory = [
        ansible.Host("foxtrot", "198.51.100.101"),
        ansible.Host("golf", "192.0.2.42"),
    ]
    hosts = tmp_path / "hosts"
    hosts.write_text("127.0.0.1 localhost")
    ansible.write_hosts_file(inventory, hosts, "bar")
    assert hosts.read_text() == textwrap.dedent(
        """\
        127.0.0.1 localhost
        # --- hedgehog managed start ---
        198.51.100.101 foxtrot foxtrot.bar
        192.0.2.42 golf golf.bar
        # --- hedgehog managed end ---
        """
    )


def test_write_hosts_file_update_existing(tmp_path):
    inventory = [
        ansible.Host("foxtrot", "198.51.100.101"),
        ansible.Host("golf", "192.0.2.42"),
    ]
    hosts = tmp_path / "hosts"
    hosts.write_text(
        textwrap.dedent(
            """\
        127.0.0.1 localhost
        ::1       localhost
        # keep this
        # --- hedgehog managed start ---
        192.0.2.42 golf
        # --- hedgehog managed end ---
        198.51.100.200 hotel
        """
        )
    )
    ansible.write_hosts_file(inventory, hosts, "foo.bar")
    assert hosts.read_text() == textwrap.dedent(
        """\
        127.0.0.1 localhost
        ::1       localhost
        # keep this
        # --- hedgehog managed start ---
        198.51.100.101 foxtrot foxtrot.foo.bar
        192.0.2.42 golf golf.foo.bar
        # --- hedgehog managed end ---
        198.51.100.200 hotel
        """
    )


def test_write_hosts_file_write_to_tempfile_if_not_root(tmp_path):
    inventory = [
        ansible.Host("foxtrot", "198.51.100.101"),
        ansible.Host("golf", "192.0.2.42"),
    ]
    mock_path = MagicMock()
    mock_path.read_text.return_value = textwrap.dedent(
        """\
        # --- hedgehog managed start ---
        # --- hedgehog managed end ---
        127.0.0.1 localhost
        ::1       localhost
        """
    )
    mock_path.write_text.side_effect = PermissionError
    temp = ansible.write_hosts_file(inventory, mock_path)
    with open(temp) as f:
        contents = f.read()
    assert contents == textwrap.dedent(
        """\
        # --- hedgehog managed start ---
        198.51.100.101 foxtrot
        192.0.2.42 golf
        # --- hedgehog managed end ---
        127.0.0.1 localhost
        ::1       localhost
        """
    )
