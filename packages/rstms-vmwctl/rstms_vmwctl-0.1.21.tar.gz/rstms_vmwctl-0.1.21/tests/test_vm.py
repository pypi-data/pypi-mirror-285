import pytest

from rstms_vmwctl.vmware_workstation import VM


def _check_vms(vms):
    assert isinstance(vms, dict)
    assert vms
    for k, v in vms.items():
        assert isinstance(k, str)
        assert isinstance(v, VM)
    return True


def test_vm_api_get_vms(client, test_vm_api):
    assert client.vmrun is False
    vms = client.get_vms()
    assert _check_vms(vms)
    assert test_vm_api in vms


def test_vm_vmrun_get_vms(client, test_vm_gui):
    client.vmrun = True
    vms = client.get_vms()
    assert _check_vms(vms)
    assert test_vm_gui in vms


def test_vm_api_get_mac(client, test_vm_api):
    assert client.vmrun is False
    mac = client.get_mac(test_vm_api)
    assert isinstance(mac, dict)
    assert "mac" in mac
    assert mac["mac"]


def test_vm_vmrun_get_mac(client, test_vm_gui):
    client.vmrun = True
    mac = client.get_mac(test_vm_gui)
    assert isinstance(mac, dict)
    assert "mac" in mac
    assert mac["mac"]


def test_vm_api_get_ip(client, test_vm_api):
    assert client.vmrun is False
    ip = client.get_ip(test_vm_api)
    assert isinstance(ip, dict)
    assert "ip" in ip
    assert ip["ip"]


@pytest.mark.skip(reason="disabled")
def test_vm_vmrun_get_ip(client, test_vm_gui):
    client.vmrun = True
    ip = client.get_ip(test_vm_gui)
    assert isinstance(ip, dict)
    assert "ip" in ip
    assert ip["ip"]


def test_vm_api_get_vmx(client, test_vm_api):
    assert client.vmrun is False
    vmx = client.get_vmx(test_vm_api)
    assert isinstance(vmx, str)
    assert vmx


def test_vm_vmrun_get_vmx(client, test_vm_gui):
    client.vmrun = True
    vmx = client.get_vmx(test_vm_gui)
    assert isinstance(vmx, str)
    assert vmx
