# cli tests

import json
import os
import shlex

import pytest
from click.testing import CliRunner

import rstms_vmwctl
from rstms_vmwctl import __version__, cli


def test_version():
    """Test reading version and module name"""
    assert rstms_vmwctl.__name__ == "rstms_vmwctl"
    assert __version__
    assert isinstance(__version__, str)


@pytest.fixture
def run():
    runner = CliRunner()

    env = os.environ.copy()
    env["TESTING"] = "1"

    def _run(cmd, **kwargs):
        assert_exit = kwargs.pop("assert_exit", 0)
        assert_exception = kwargs.pop("assert_exception", None)
        parse_json = kwargs.pop("parse_json", True)
        env.update(kwargs.pop("env", {}))
        kwargs["env"] = env
        result = runner.invoke(cli, cmd, **kwargs)
        if assert_exception is not None:
            assert isinstance(result.exception, assert_exception)
        elif result.exception is not None:
            raise result.exception from result.exception
        elif assert_exit is not None:
            assert result.exit_code == assert_exit, (
                f"Unexpected {result.exit_code=} (expected {assert_exit})\n"
                f"cmd: '{shlex.join(cmd)}'\n"
                f"output: {str(result.output)}"
            )
        if parse_json:
            result = json.loads(result.stdout)
        return result

    return _run


def test_cli_no_args(run):
    result = run([], parse_json=False)
    assert "Usage:" in result.output


def test_cli_help(run):
    result = run(["--help"], parse_json=False)
    assert "Show this message and exit." in result.output


def test_cli_exception(run):
    cmd = ["--shell-completion", "and_now_for_something_completely_different"]

    with pytest.raises(RuntimeError) as exc:
        result = run(cmd, parse_json=False)
    assert isinstance(exc.value, RuntimeError)

    # example of testing for expected exception
    result = run(cmd, assert_exception=RuntimeError, parse_json=False)
    assert result.exception
    assert result.exc_info[0] == RuntimeError
    assert result.exception.args[0] == "cannot determine shell"

    with pytest.raises(AssertionError) as exc:
        result = run(cmd, assert_exception=ValueError)
    assert exc


def test_cli_exit(run):
    result = run(["--help"], assert_exit=None, parse_json=False)
    assert result
    result = run(["--help"], assert_exit=0, parse_json=False)
    assert result
    with pytest.raises(AssertionError):
        run(["--help"], assert_exit=-1, parse_json=False)


def test_cli_create_gui(run, client):
    client.destroy("test_gui", force=True)
    result = run("create test_gui --gui --start")
    assert isinstance(result, dict)
    assert result["power"] == "poweredOn"
    client.destroy("test_gui", force=True)


def test_cli_describe(run, test_vm):
    ret = run("describe test_vm")
    assert isinstance(ret, dict)


def test_cli_ip(run, test_vm):
    ret = run("ip test_vm")
    assert isinstance(ret, str)
    assert ret


def test_cli_mac(run, test_vm):
    ret = run("mac test_vm")
    assert isinstance(ret, str)
    assert ret


def test_cli_state(run, test_vm):
    ret = run("state test_vm")
    assert isinstance(ret, str)
    assert ret


def test_cli_status(run, test_vm):
    ret = run("status test_vm")
    assert isinstance(ret, dict)
    assert set(ret.keys()) == set(["name", "vmx", "id", "mac", "ip", "power"])


def test_cli_iso(run, test_vm):
    ret = run("iso test_vm")
    assert isinstance(ret, dict)
    assert set(ret.keys()) == set(["name", "id", "iso", "present", "start_connected"])


def test_cli_vnc(run, test_vm):
    ret = run("vnc test_vm")
    assert isinstance(ret, dict)
    assert set(ret.keys()) == set(["id", "enabled", "port", "ip"])


def test_cli_ls(run, test_vm):
    ret = run("ls")
    assert isinstance(ret, list)
    assert "test_vm" in ret


def test_cli_power(run, test_vm):
    ret = run("poweroff test_vm")
    assert isinstance(ret, dict)
    ret = run("start test_vm")
    assert isinstance(ret, dict)
    ret = run("stop test_vm")
    assert isinstance(ret, dict)


def test_cli_reboot(run, test_vm):
    ret = run("reboot test_vm")
    assert isinstance(ret, dict)


def test_cli_vmx(run, test_vm):
    ret = run("vmx test_vm", parse_json=False)
    assert isinstance(ret.stdout, str)
    assert ret.stdout
