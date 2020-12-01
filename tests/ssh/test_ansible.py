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
        ansible.Host("golf", "198.51.100.102"),
        ansible.Host("hotel", "198.51.100.103"),
    ]
    config = tmp_path / "ssh_config"
    ansible.write_ssh_config(str(config), inventory)
    expected = textwrap.dedent(
        """\
        Host foxtrot
            Hostname 198.51.100.101
            User root
            LocalForward 13306 localhost:3306

        Host golf
            Hostname 198.51.100.102
            User root
            LocalForward 13306 localhost:3306

        Host hotel
            Hostname 198.51.100.103
            User root
            LocalForward 13306 localhost:3306
        """
    )
    assert config.read_text() == expected
