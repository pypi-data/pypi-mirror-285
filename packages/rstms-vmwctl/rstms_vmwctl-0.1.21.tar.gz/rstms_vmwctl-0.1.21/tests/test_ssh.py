import pytest

from rstms_vmwctl.sshconfig import SSHConfig


@pytest.fixture
def name():
    return "opensea"


@pytest.fixture
def ssh(client, name):
    return SSHConfig(client, name)


def test_ssh_update(ssh):
    ssh.update()
