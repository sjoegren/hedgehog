from hedgehog.ssh import ansible


def test_get_inventory():
    hosts = ansible.get_inventory()
    assert hosts["host1"].name == "host1"
    assert hosts["host1"].address == "192.0.2.1"
    assert hosts["remote.example.com"].address == "198.51.100.1"
