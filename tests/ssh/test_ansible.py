import textwrap

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
    ansible.write_ssh_config(str(config), inventory)
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
