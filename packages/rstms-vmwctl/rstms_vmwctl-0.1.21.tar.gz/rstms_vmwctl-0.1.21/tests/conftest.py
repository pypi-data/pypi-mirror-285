import json
from pathlib import Path

import pytest

import rstms_vmwctl.vmware_workstation


def _client():
    config_file = Path("tests/data/config.conf")
    config_text = config_file.read_text()
    config = json.loads(config_text)
    return rstms_vmwctl.vmware_workstation.Client(
        config["host"],
        config["url"],
        config["username"],
        config["password"],
        config["path"],
        config["arp_command"],
        config["iso"],
    )


@pytest.fixture
def client():
    api = _client()
    assert api
    return api


@pytest.fixture(scope="session")
def test_vm():
    client = _client()
    name = "test_vm"
    client.destroy(name, force=True)
    client.create(name)
    client.set_power(name, "on")
    client.wait_power_state(name, "on", "poweredOn")
    yield name
    client.set_power(name, "off")
    client.wait_power_state(name, "off", "poweredOff")
    client.destroy(name, force=True)


@pytest.fixture(scope="session")
def test_vm_api():
    client = _client()
    name = "test_vm_api"
    client.destroy(name, force=True)
    client.create(name)
    client.set_power(name, "on")
    client.wait_power_state(name, "on", "poweredOn")
    yield name
    client.set_power(name, "off")
    client.wait_power_state(name, "off", "poweredOff")
    client.destroy(name, force=True)


@pytest.fixture(scope="session")
def test_vm_gui():
    client = _client()
    name = "test_vm_gui"
    client.destroy(name, force=True)
    client.create(name)
    client.set_power(name, "start", gui=True)
    client.wait_power_state(name, "start", "poweredOn")
    yield name
    client.set_power(name, "off")
    client.wait_power_state(name, "off", "poweredOff")
    client.destroy(name, force=True)
