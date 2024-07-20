import pytest

from rstms_vmwctl.vmx import VMX


@pytest.fixture
def vmx(datadir):
    vmx_file = datadir / "vmxtest.vmx"
    return VMX(vmx_file)


def test_vmx_gen(vmx):
    vmx.generate(
        cpu_count=2,
        ram_mb=256,
        vmdk_pathname="vmdk_pathname",
    )
    assert vmx.text
    assert 'numvcpus = "2"' in vmx.text
    assert 'memsize = "256"' in vmx.text
    assert 'nvme0.present = "TRUE"' in vmx.text
    assert 'nvme0:0.fileName = "vmdk_pathname"' in vmx.text
