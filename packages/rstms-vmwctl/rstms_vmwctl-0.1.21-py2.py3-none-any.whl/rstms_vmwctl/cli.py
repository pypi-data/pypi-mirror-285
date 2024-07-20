"""Console script for rstms_vmwctl."""

import json
import os
import sys
from pathlib import Path

import click
import click.core
from click_params import IP_ADDRESS, MAC_ADDRESS

from .exception_handler import ExceptionHandler
from .shell import _shell_completion
from .sshconfig import SSHConfig
from .version import __timestamp__, __version__
from .vmware_workstation import Client

header = f"vmctl v{__version__} {__timestamp__}"


def _ehandler(ctx, option, debug):
    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["debug"] = debug


def fail(msg):
    click.echo(f"vmwctl: {msg}", err=True)
    sys.exit(-1)


def output(ctx, obj, exit=0):
    if not ctx.raw:
        obj = json.dumps(obj, indent=2)
    click.echo(obj)
    sys.exit(exit)


@click.group("vmctl", context_settings={"auto_envvar_prefix": "VMWCTL"})
@click.version_option(message=header)
@click.option("-d", "--debug", is_eager=True, is_flag=True, callback=_ehandler, help="debug mode")
@click.option("-h", "--host", envvar="VMCTL_HOST")
@click.option("-u", "--url", envvar="VMCTL_URL")
@click.option("-U", "--username", envvar="VMCTL_USERNAME")
@click.option("-P", "--password", envvar="VMCTL_PASSWORD")
@click.option("-a", "--arp-command", envvar="VMCTL_RARP", help="arp table command")
@click.option("-i", "--iso", envvar="VMCTL_ISO", type=click.Path(dir_okay=False, readable=True, path_type=Path))
@click.option("--no-iso", is_flag=True)
@click.option("-t", "--timeout", type=int, help="wait timeout in seconds")
@click.option("-r", "--raw", is_flag=True, help="suppress json formatting")
@click.option("-c", "--config_file", default=".vmctl.conf")
@click.option(
    "--path-list",
    default="/mnt/beaker/h/vmware,/mnt/beaker/d/vmware",
    envvar="VMCTL_PATH_LIST",
    help="comma delimited list of vmware base paths",
)
@click.option("-v", "--verbose", is_flag=True)
@click.option("-V/-A", "--vmrun/--api", is_flag=True, help="use vmware vmrun cli")
@click.option("-w/-W", "--wait/--no-wait", default=True, is_flag=True)
@click.option(
    "--shell-completion",
    is_flag=False,
    flag_value="[auto]",
    callback=_shell_completion,
    help="configure shell completion",
)
@click.pass_context
def cli(
    ctx,
    debug,
    shell_completion,
    host,
    url,
    username,
    password,
    verbose,
    path_list,
    arp_command,
    iso,
    no_iso,
    config_file,
    raw,
    vmrun,
    timeout,
    wait,
):
    """vmctl top-level help"""
    config = Path(config_file)
    if not config.is_file():
        config = Path.home() / config_file
    if not config.is_file():
        config = Path.home() / ".secrets" / "vmctl.conf"
    if config.is_file():
        config = json.loads(config.read_text())
    else:
        config = {}

    host = config.get("host", host)
    url = config.get("url", url)
    username = config.get("username", username)
    password = config.get("password", password)
    path_list = config.get("path_list", path_list)
    arp_command = config.get("arp_command", arp_command)
    iso = Path(config.get("iso", iso))
    if no_iso:
        iso = None
    client = Client(host, url, username, password, path_list, arp_command, iso)
    client.verbose = verbose
    client.raw = raw
    client.vmrun = vmrun
    if timeout:
        client.timeout = timeout
    client.wait = wait
    ctx.obj = client


@cli.command("ls")
@click.option("-l", "--long", is_flag=True)
@click.option("-v", "--vmx", is_flag=True)
@click.option("-r", "--running", is_flag=True)
@click.argument("name", required=False)
@click.pass_obj
def _list(ctx, long, vmx, running, name):
    """list VMs"""

    if vmx:
        files = ctx.get_vmx_files()
        if name:
            files = [f for f in files if f.endswith(name + ".vmx")]
        output(ctx, files)

    if name:
        vms = {name: ctx.get_vm(name)}
    else:
        vms = ctx.get_vms()

    if running:
        vms = {k: v for k, v in vms.items() if ctx.power_state(k) == "poweredOn"}

    if long:
        vms = [ctx.get_status(name) for name in vms.keys()]
    else:
        vms = list(vms.keys())

    output(ctx, vms)


@cli.command
@click.argument("name")
@click.pass_obj
def status(ctx, name):
    """VM status"""
    output(ctx, ctx.get_status(name))


@cli.command
@click.argument("name")
@click.pass_obj
def describe(ctx, name):
    """VM detail"""
    output(ctx, ctx.get_detail(name))


@cli.command
@click.argument("name")
@click.pass_obj
def state(ctx, name):
    """VM power state"""
    output(ctx, ctx.get_power(name)["power"])


@cli.command
@click.argument("name")
@click.pass_obj
def ip(ctx, name):
    """VM IP address"""
    output(ctx, ctx.get_ip(name, fail_ok=False)["ip"])


@cli.command
@click.argument("name")
@click.pass_obj
def mac(ctx, name):
    """VM MAC address"""
    output(ctx, ctx.get_mac(name, fail_ok=False)["mac"])


@cli.command
@click.argument("name")
@click.pass_obj
def edit(ctx, name):
    """edit VMX file"""
    vm = ctx.get_vm(name)
    editor = os.environ.get("EDITOR", "vi")
    os.execvp(editor, [editor, str(vm.vmx)])


@cli.command
@click.argument("name")
@click.pass_obj
def vmx(ctx, name):
    """output VMX file"""
    ctx.raw = True
    output(ctx, ctx.get_vmx(name))


@cli.command
@click.option("-i", "--iso", type=click.Path(dir_okay=False, readable=True, path_type=Path), help="cdrom iso file")
@click.option("--no-iso", is_flag=True)
@click.option("-c/-d", "--connect/--disconnect", is_flag=True, default=None, help="mount/dismount ISO")
@click.argument("name")
@click.pass_obj
def iso(ctx, name, iso, no_iso, connect):
    """show or modify VM CDROM ISO"""
    iso = iso or ctx.iso
    if no_iso:
        iso = None
    result = ctx.cdrom(name, iso, connect)
    output(ctx, result)


@cli.command
@click.argument("name")
@click.option("-g", "--gui", is_flag=True)
@click.option("-f", "--fullscreen", is_flag=True)
@click.option("-c/-d", "--connect/--disconnect", is_flag=True, default=None, help="mount/dismount ISO")
@click.option("-i", "--iso", type=click.Path(dir_okay=False, readable=True, path_type=Path), help="cdrom iso file")
@click.option("--no-iso", is_flag=True)
@click.pass_obj
def start(ctx, gui, fullscreen, connect, iso, no_iso, name):
    """power on"""
    iso = iso or ctx.iso
    if no_iso:
        iso = None
    ctx.cdrom(name, iso, connect)
    _start(ctx, gui, fullscreen, name)
    result = ctx.wait_power_state(name, "start", "poweredOn", click.echo)
    output(ctx, result)


def _start(ctx, gui, fullscreen, name):
    if ctx.vmrun or gui or fullscreen:
        operation = "start"
    else:
        operation = "on"
    return ctx.set_power(name, operation, gui=gui, fullscreen=fullscreen)


@cli.command
@click.argument("name")
@click.option("-g", "--gui", is_flag=True)
@click.option("-f", "--fullscreen", is_flag=True)
@click.option("-h", "--hard", is_flag=True, help="hard shutdown")
@click.pass_obj
def reboot(ctx, hard, gui, fullscreen, name):
    """reboot"""
    if ctx.vmrun or gui or fullscreen:
        ctx.vmrun = True
        ctx.set_power(name, "reset", hard=hard)
        result = ctx.wait_power_state(name, "reset", "poweredOn", click.echo)
    else:
        operation = "off" if hard else "shutdown"
        ctx.set_power(name, operation)
        ctx.wait_power_state(name, operation, "poweredOff", click.echo)
        _start(ctx, gui, fullscreen, name)
        result = ctx.wait_power_state(name, "restart", "poweredOn", click.echo)
    output(ctx, result)


@cli.command
@click.argument("name")
@click.pass_obj
def poweroff(ctx, name):
    """hard power down"""
    if ctx.vmrun:
        result = ctx.set_power(name, "stop", hard=True)
    else:
        result = ctx.set_power(name, "off")
    result.update(ctx.wait_power_state(name, "off", "poweredOff", click.echo))
    output(ctx, result)


@cli.command
@click.argument("name")
@click.pass_obj
def stop(ctx, name):
    """request shutdown and power off"""
    if ctx.vmrun:
        result = ctx.set_power(name, "stop", hard=False)
    else:
        result = ctx.set_power(name, "shutdown")
    result.update(ctx.wait_power_state(name, "shutdown", "poweredOff", click.echo))
    output(ctx, result)


@cli.command
@click.option("-C", "--cpu", type=int, help="cpu count")
@click.option("-R", "--ram", type=int, help="RAM in MB")
@click.option("-D", "--disk", type=int, help="disk size in MB")
@click.option("-m", "--mac", type=MAC_ADDRESS, help="ethernet MAC address")
@click.option(
    "-i",
    "--iso",
    envvar="VMCTL_ISO",
    type=click.Path(dir_okay=False, readable=True, path_type=Path),
    help="cdrom iso file",
)
@click.option("--no-iso", is_flag=True)
@click.option("-c/-d", "--connect/--disconnect", is_flag=True, default=True, help="mount/dismount ISO")
@click.option("-g", "--gui", is_flag=True)
@click.option("-e", "--efi", is_flag=True)
@click.option("-f", "--fullscreen", is_flag=True)
@click.option("-s", "--start", is_flag=True, help="start after create")
@click.option("--time-sync/-no-time-sync", is_flag=True, default=True, help="sync time with host")
@click.option("--drag-and-drop/--no-drag-and-drop", is_flag=True, default=False, help="drag and drop")
@click.option("--clipboard/-no-clipboard", is_flag=True, default=False, help="copy and paste")
@click.option("--disk-growable", "disk_type", flag_value=0, help="growable single file virtual disk")
@click.option(
    "--disk-multifile-growable",
    "disk_type",
    flag_value=1,
    default=True,
    help="growable virtual disk split into multiple files",
)
@click.option("--disk-preallocated", "disk_type", flag_value=2, help="preallocated single file virtual disk")
@click.option(
    "--disk-multifle-preallocated",
    "disk_type",
    flag_value=3,
    help="preallocated virtual disk split into multiple files",
)
@click.option("--disk-esx", "disk_type", flag_value=4, help="preallocated ESX-type virtual disk")
@click.option("--disk-steraming", "disk_type", flag_value=5, help="compressed disk optimized for streaming")
@click.option("--disk-thin", "disk_type", flag_value=6, help="thin provisioned virtual disk")
@click.argument("name")
@click.pass_obj
def create(
    ctx,
    cpu,
    ram,
    disk,
    efi,
    mac,
    iso,
    no_iso,
    connect,
    start,
    gui,
    fullscreen,
    time_sync,
    drag_and_drop,
    clipboard,
    name,
    disk_type,
):
    """create VM"""
    iso = iso or ctx.iso
    if mac:
        mac = str(mac)
    if no_iso:
        iso = None
    result = ctx.create(
        name,
        cpu_count=cpu,
        ram_size=ram,
        disk_size=disk,
        disk_type=disk_type,
        iso_path=iso,
        iso_connected=connect,
        mac=mac,
        efi=efi,
        time_sync=time_sync,
        drag_and_drop=drag_and_drop,
        clipboard=clipboard,
    )
    if start:
        _start(ctx, gui, fullscreen, name)
        result.update(ctx.wait_power_state(name, "start", "poweredOn", click.echo))
    output(ctx, result)


@cli.command
@click.option("-f", "--force", is_flag=True, help="bypass confirmation")
@click.argument("name")
@click.pass_obj
def destroy(ctx, name, force):
    """destroy VM"""
    if not force:
        click.confirm(f"Confirm IRRECOVERABLE DESTRUCTION of VMWare Workstation '{name}' on '{ctx.host}'", abort=True)
    result = ctx.destroy(name, force)
    output(ctx, result)


@cli.command
@click.option("-e", "--enable", is_flag=True)
@click.option("-d", "--disable", is_flag=True)
@click.option("-p", "--port", type=int, help="VNC port (default: 5900 + <vm_ip> & 0xFF)")
@click.option("-a", "--address", type=IP_ADDRESS, default="127.0.0.1", show_default=True, help="listen IP address")
@click.argument("name")
@click.pass_obj
def vnc(ctx, name, enable, disable, port, address):
    """VM VNC settings"""
    result = ctx.vnc(name, enable, disable, port, address)
    output(ctx, result)

@cli.command
@click.option("-c/-C", "--copy/--no-copy", is_flag=True, default=None, help="clipboard cut")
@click.option("-p/-P", "--paste/--no-paste", is_flag=True, default=None, help="clipboard paste")
@click.option("-d/-D", "--dnd/--no-dnd", is_flag=True, default=None, help="drag and drop")
@click.option("-h/-H", "--hgfs/--no-hgfs", is_flag=True, default=None, help="shared folders")
@click.argument("name")
@click.pass_obj
def isolation(ctx, name, copy, paste, dnd, hgfs):
    """VM Isolation settings"""
    result = ctx.clipboard(name, copy, paste, dnd, hgfs)
    output(ctx, result)


@cli.command
@click.argument("name")
@click.pass_obj
def boot(ctx, name):
    """show boot parameters"""
    result = ctx.boot(name)
    output(ctx, result)


@cli.command
@click.option("-u", "--update-host-keys", is_flag=True, help="update ssh known_host keys")
@click.argument("name")
@click.pass_obj
def ssh(ctx, name, update_host_keys):
    """ssh config"""
    ssh = SSHConfig(ctx, name)
    if update_host_keys:
        return ssh.update()
    else:
        ssh.exec()


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
