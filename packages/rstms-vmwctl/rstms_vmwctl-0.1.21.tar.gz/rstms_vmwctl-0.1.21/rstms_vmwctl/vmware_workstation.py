import re
import shlex
import shutil
import socket
import subprocess
import time
from pathlib import Path
from urllib.parse import quote

import requests

from .vmx import VMX

MAC_PATTERN = r"([0-9a-f]{2}:){5}[0-9a-f]{2}$"


class VMFailure(Exception):
    pass


class VM:
    def __init__(self, name=None, vmx=None, id=None, mac=None, ip=None, power=None, dict=None):
        self.name = name
        self.vmx = Path(vmx) if vmx else None
        self.id = id
        self.mac = mac
        self.ip = ip
        self.power = power
        if dict is not None:
            self.from_dict(dict)

    def to_dict(self):
        return dict(name=self.name, vmx=str(self.vmx), id=self.id, mac=self.mac, ip=self.ip, power=self.power)

    def from_dict(self, data):
        self.name = data["name"]
        vmx = data["vmx"]
        self.vmx = Path(vmx) if vmx else None
        self.id = data.get("id", None)
        self.mac = data.get("mac", None)
        self.ip = data.get("ip", None)
        self.power = data.get("power", None)


class Client:

    cpu_count = 1
    disk_size = 8192
    ram_size = 1024
    timeout = 60
    wait = True
    protected_names = ["phobos", "cryptovault"]

    def __init__(self, host, url, username, password, path_list, arp_command, iso):
        self.host = host
        self.url = url
        self.username = username
        self.password = password
        self.arp_command = arp_command
        self.iso = iso
        self.vm = {}
        self.arp_table = None
        self.vmrun = False
        self.verbose = False
        self.raw = False
        self.vmware_path_list = [Path(p) for p in path_list.split(",")]
        self.vmware_path = self.vmware_path_list[0]

    def wait_power_state(self, name, operation, power_state, echo=None):
        if echo is None:
            self.verbose = False
        if self.wait:
            self.vmrun = False
            if self.verbose:
                echo(operation, err=True, nl=False)
            timeout = time.time() + self.timeout
            while True:
                if self.verbose:
                    echo(".", err=True, nl=False)
                time.sleep(1)
                if name in self.get_vms():
                    if self.power_state(name) == power_state:
                        break
                if time.time() > timeout:
                    raise VMFailure(f"timed out after {self.timeout} seconds awaiting '{power_state}'")
            if self.verbose:
                echo(err=True)
        return self.get_status(name)

    def _host_path(self, path, enforce_file=None, enforce_absent=None):
        path = Path(path)
        if enforce_file:
            if not path.is_file():
                raise VMFailure(f"file not found: {str(path)}")
        if enforce_absent:
            if path.exists():
                raise VMFailure(f"path exists: {str(path)}")
        if str(path).startswith("/mnt/beaker/"):
            _, _, path = str(path).partition("/")
            _, _, path = path.partition("/")
            _, _, path = path.partition("/")
            drive, _, path = path.partition("/")
            path = drive.upper() + ":/" + path
        path = path.replace("/", "\\")
        return Path(path)

    def _local_path(self, path):
        if not path:
            return ""
        path = str(path)
        path = path.replace("\\", "/")
        if path[1] == ":":
            path = "/mnt/beaker/" + path[0].lower() + path[2:]
        return Path(path)

    def _vmrun(self, cmd, strip=True, split=None):
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)
        proc = self._run(
            ["vmrun", "-T", "ws"] + cmd,
            return_proc=True,
        )
        if proc.returncode == 0:
            ret = proc.stdout
            if strip:
                ret = ret.strip()
            if split:
                ret = ret.split(split)
            return ret
        else:
            raise VMFailure("\n".join([proc.stderr.strip() + proc.stdout.strip()]))

    def _run(self, cmd, **kwargs):
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)
        strip = kwargs.pop("strip", True)
        split = kwargs.pop("split", False)
        return_proc = kwargs.pop("return_proc", False)
        kwargs.setdefault("text", True)
        kwargs.setdefault("check", not return_proc)
        kwargs.setdefault("capture_output", True)
        proc = subprocess.run(["ssh", self.host] + cmd, **kwargs)
        if return_proc:
            return proc
        ret = proc.stdout
        if strip:
            ret = ret.strip()
        if split:
            ret = ret.split(split)
        return ret

    def _request(self, func, path, **kwargs):
        raise_on_failure = kwargs.pop("raise_on_failure", True)
        parse_json = kwargs.pop("parse_json", True)
        kwargs["auth"] = (self.username, self.password)
        kwargs["headers"] = {
            "Content-Type": "application/vnd.vmware.vmw.rest-v1+json",
            "Accept": "application/vnd.vmware.vmw.rest-v1+json",
        }
        result = func(f"{self.url}/api/{path}", **kwargs)
        if raise_on_failure:
            result.raise_for_status()
        if parse_json:
            return result.json()
        return result

    def get(self, path, **kwargs):
        return self._request(requests.get, path, **kwargs)

    def delete(self, path, **kwargs):
        return self._request(requests.delete, path, **kwargs)

    def put(self, path, **kwargs):
        return self._request(requests.put, path, **kwargs)

    def post(self, path, **kwargs):
        return self._request(requests.put, path, **kwargs)

    def get_vms_api(self):
        self.vm = {}
        vms = self.get("vms")
        for vm in vms:
            path = self._local_path(vm["path"])
            name = path.stem
            self.vm[name] = VM(name=name, vmx=path, id=vm["id"])
        return self.vm

    def get_vms_vmrun(self):
        ret = {}
        lines = self._vmrun("list", split="\n")
        for line in lines:
            if line.startswith("Total"):
                continue
            path = Path(self._local_path(line))
            name = path.stem
            vm = VM(name=name, vmx=path)
            cvm = self.vm.get(name, None)
            if cvm:
                if cvm.vmx != vm.vmx:
                    raise VMFailure(f"vmx path mismatch: {name}")
                vm.id = cvm.id
            ret[name] = vm
        return ret

    def get_vms(self):
        if self.vmrun:
            return self.get_vms_vmrun()
        else:
            return self.get_vms_api()

    def get_vm(self, name, must_exist=True):
        vms = self.get_vms()
        try:
            return vms[name]
        except KeyError:
            raise VMFailure(f"not found: {name}")

    def get_vid(self, name):
        vm = self.get_vm(name)
        return vm.id

    def get_status(self, name):
        vm = self.get_vm(name).to_dict()
        vm.update(self.get_power(None, vm["id"]))
        vm.update(self.get_mac(None, vm["id"]))
        if vm["mac"]:
            vm.update(self.get_ip(None, mac=vm["mac"]))
        else:
            vm["ip"] = ""
        return vm

    def get_detail(self, name, vid=None):
        vid = vid or self.get_vid(name)
        config = self.get(f"vms/{vid}/restrictions")
        return config

    def get_vmx_files(self):
        return [str(f) for f in self._vmx_files()]

    def _vmx_files(self):
        ret = []
        for vmware_dir in self.vmware_path_list:
            names = [item.name for item in vmware_dir.iterdir() if item.is_dir()]
            files = [vmware_dir / name / f"{name}.vmx" for name in names]
            ret.extend([f for f in files if f.is_file()])
        return ret

    def _find_vmx_file(self, name):
        for file in self._vmx_files():
            if file.stem == name:
                return file
        raise VMFailure(f"vmx not found: {name}")

    def _gui_start(self, vmx, fullscreen):
        cmd = ["cmd", "vmware", "-n", "-q"]
        if fullscreen:

            cmd.append("-X")
        else:
            cmd.append("-x")
        cmd.append(str(vmx))
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return proc.pid

    def _power_result(self, operation):
        if operation == "start":
            return "vm_started"
        elif operation == "stop":
            return "vm_stopped"
        elif operation == "reboot":
            return "vm_rebooted"
        elif operation == "on":
            return "vm_powered_up"
        elif operation == "off":
            return "vm_powered_down"
        elif operation == "shutdown":
            return "vm_shutdown"
        return operation

    def set_power(self, name, operation, hard=False, gui=False, fullscreen=False):
        ret = dict(name=name)
        if operation in ["start", "stop", "reboot"]:
            vmx = self._host_path(self._find_vmx_file(name), enforce_file=True)
            if operation == "start" and (gui or fullscreen):
                ret["mode"] = "vmware"
                self.set_parameter(name, "gui.enableStretchGuest", "TRUE" if fullscreen else "FALSE")
                ret["pid"] = self._gui_start(vmx, fullscreen)
            else:
                cmd = [operation, f"'{vmx}'"]
                if operation in ["stop", "reset"]:
                    if hard:
                        cmd.append("hard")
                    else:
                        cmd.append("soft")
                ret["result"] = self._vmrun(cmd)
                ret["mode"] = "vmrun"
        elif operation in ["on", "off", "shutdown"]:
            self.vmrun = False
            vid = self.get_vid(name)
            ret["id"] = vid
            ret["mode"] = "api"
            state = self.put(f"vms/{vid}/power", data=operation.encode())
            ret["power"] = state["power_state"]
        else:
            raise VMFailure(f"unexpected power operation: {operation}")

        ret["result"] = self._power_result(operation)
        return ret

    def get_power(self, name, vid=None):
        vid = vid or self.get_vid(name)
        ret = self.get(f"vms/{vid}/power")
        return dict(power=ret["power_state"])

    def get_mac(self, name, vid=None, fail_ok=True):
        if self.vmrun:
            vm = self.get_vm(name)
            path = self._host_path(vm.vmx, enforce_file=True)
            return dict(mac=self._vmrun(["readVariable", f"'{path}'", "runtimeConfig", "ethernet0.generatedAddress"]))
        else:
            vid = vid or self.get_vid(name)
            result = self.get(f"vms/{vid}/nic")
            for nic in result.get("nics", []):
                return dict(mac=nic.get("macAddress"))

        if fail_ok:
            return dict(mac="")

        raise VMFailure("no mac address")

    def get_ip(self, name, vid=None, mac=None, fail_ok=True):

        if self.vmrun:
            vm = self.get_vm(name)
            path = self._host_path(vm.vmx, enforce_file=True)
            return dict(ip=self._vmrun(["getGuestIpAddress", f"'{path}'"]))

        mac = mac or self.get_mac(name, vid=vid)["mac"]
        if mac:
            if self.arp_table is None:
                self.arp_table = (
                    subprocess.run(shlex.split(self.arp_command), text=True, capture_output=True, check=True)
                    .stdout.strip()
                    .split("\n")
                )
            for arp in self.arp_table:
                m = re.match(r"(\S+)\s+" + mac + r".*", arp, re.I)
                if m:
                    return dict(ip=m.groups()[0])

        if fail_ok:
            return dict(ip="")

        raise VMFailure("no IP address")

    def _vm_exists(self, name):
        self.get_vms()
        return name in self.vm

    def _vmx_path(self, name, enforce_exists=None, enforce_absent=None, create=False):
        path = self.vmware_path / name
        if path.exists():
            if enforce_absent:
                raise VMFailure(f"vmx path '{str(path)}' exists")
            if not path.is_dir():
                raise VMFailure(f"vmx path '{str(path)}' is not a directory")
        else:
            if enforce_exists:
                raise VMFailure(f"vmx path '{str(path)}' does not exist")
            if create:
                path.mkdir()
        return path

    def create(
        self,
        name,
        *,
        cpu_count=None,
        ram_size=None,
        disk_size=None,
        disk_type=1,
        iso_path=None,
        iso_connected=True,
        mac=None,
        efi=False,
        time_sync=True,
        clipboard=False,
        drag_and_drop=False,
    ):

        cpu_count = cpu_count or self.cpu_count
        ram_size = ram_size or self.ram_size
        disk_size = disk_size or self.disk_size
        iso_path = iso_path or self.iso

        if mac:
            mac = mac.strip('"')
            mac = mac.strip("'")
            if not re.match(MAC_PATTERN, mac):
                raise VMFailure(f"Unrecognized mac format: '{mac}'")

        if self._vm_exists(name):
            raise VMFailure(f"VM '{name}' exists")

        vmx_path = self._vmx_path(name, enforce_absent=True, create=True)

        ssh_path = str(vmx_path).replace("/mnt/beaker/", "/cygdrive/")
        self._run(["sh", "-c", f"'cd {ssh_path} && vmware-vdiskmanager -c -s {disk_size}MB -a nvme -t {disk_type} {name}.vmdk'"])

        vmdk_path = self.vmware_path / name / (name + ".vmdk")
        host_vmdk_path = self._host_path(vmdk_path, enforce_file=True)
        vmx_file = vmx_path / f"{name}.vmx"

        vmx = VMX(vmx_file)
        vmx.generate(
            cpu_count=cpu_count,
            ram_mb=ram_size,
            vmdk_pathname=name+".vmdk",
            efi=efi,
            time_sync=time_sync,
            drag_and_drop=drag_and_drop,
            clipboard=clipboard,
        )
        # configure ethernet if dynamic MAC
        if not mac:
            vmx.set_ethernet(True, mac)
        vmx.write()
        vm = self.get_vm(name)
        if str(vm.vmx) != str(vmx_file):
            raise VMFailure("vmx path mismatch")

        # start/stop VM so vmware can set uuid.bios, uuid.location
        on_status = self.set_power(name, "on")
        if on_status["power"] != "poweredOn":
            raise VMFailure(f"unexpected power state: {on_status['power']}")
        off_status = self.set_power(name, "off")
        if off_status["power"] != "poweredOff":
            raise VMFailure(f"unexpected power state: {off_status['power']}")
        vmx.read()

        # configure cdrom
        if iso_path:
            host_iso_path = self._host_path(iso_path, enforce_file=True)
        else:
            host_iso_path = None
            iso_connected = False
        vmx.set_cdrom(host_iso_path, iso_connected)

        # configure ethernet
        if mac:
            vmx.set_ethernet(True, mac)

        vmx.write()
        ret = self.get_status(name)
        ret.update(dict(result="created"))
        return ret

    def register(self, name, vmx_path):
        host_vmx_path = self._host_path(vmx_path, enforce_file=True)
        ret = self.post("vms/registration", json=dict(name=name, path=host_vmx_path))
        return ret

    def destroy(self, name, force):  # noqa: C901
        ret = dict(name=name)
        self.vmrun = False
        if self._vm_exists(name):
            ret["result"] = "vm_destroyed"
            vid = self.get_vid(name)
            if force:
                if self.power_state(None, vid) != "poweredOff":
                    self.set_power(name, "off")
            else:
                self.check_power_off(None, vid)
            ret["id"] = vid
            response = self.delete(f"/vms/{vid}", parse_json=False)
            if not response.ok:
                raise VMFailure(f"{response} {response.reason}")

        path = self._vmx_path(name)
        if path.exists():
            if path.is_dir():
                ret["result"] = "vmx_path_deleted"
                for name in self.protected_names:
                    assert name not in str(path)
                ret["path"] = str(path)
                if force:
                    try:
                        shutil.rmtree(path)
                    except Exception as e:
                        if type(e) is FileNotFoundError:
                            raise
                else:
                    raise VMFailure("vmx path not deleted without --force")
            else:
                raise VMFailure(f"vmx path is not a directory: {str(path)}")
        if "result" not in ret:
            ret["result"] = "vm_nonexistent"
        self.vm.pop(name, None)
        return ret

    def power_state(self, name, vid=None):
        return self.get_power(name, vid)["power"]

    def check_power_off(self, name, vid=None):
        vid = vid or self.get_vid(name)
        if self.power_state(None, vid) != "poweredOff":
            raise VMFailure("VM must be powered off")
        return vid

    def set_parameter(self, name, key, value):
        if self.vmrun:
            vm = self.get_vm(name)
            path = self._host_path(vm.vmx, enforce_file=True)
            return self._vmrun(["writeVariable", f"'{path}'", key, value])
        else:
            vid = self.get_vid(name)
            return self.put(f"vms/{vid}/params", json=dict(name=key, value=value), parse_json=False)

    def cdrom(self, name, iso_path=None, connected=None):
        ret = dict(result="failure", detail="unknown")
        vid = self.get_vid(name)
        if iso_path:
            if not iso_path.is_file():
                raise VMFailure(f"iso_path is not a file: '{str(iso_path)}'")
            host_iso_path = self._host_path(iso_path, enforce_file=True)
            self.put(f"vms/{vid}/params", json=dict(name="ide1:0.present", value="TRUE"), parse_json=False)
            self.put(f"vms/{vid}/params", json=dict(name="ide1:0.fileName", value=str(host_iso_path)), parse_json=False)
            if connected is True:
                self.put(f"vms/{vid}/params", json=dict(name="ide1:0.startConnected", value="TRUE"), parse_json=False)
            elif connected is False:
                self.put(f"vms/{vid}/params", json=dict(name="ide1:0.startConnected", value="FALSE"), parse_json=False)
        else:
            self.put(f"vms/{vid}/params", json=dict(name="ide1:0.present", value="FALSE"), parse_json=False)
            self.put(f"vms/{vid}/params", json=dict(name="ide1:0.fileName", value=""), parse_json=False)
            self.put(f"vms/{vid}/params", json=dict(name="ide1:0.startConnected", value="FALSE"), parse_json=False)

        ret = {}
        ret["name"] = name
        ret["id"] = vid
        params = self.get(f"vms/{vid}/params/{quote("ide1:0.fileName")}")
        iso_path = params["value"]
        ret["iso"] = str(self._local_path(iso_path))
        params = self.get(f"vms/{vid}/params/{quote("ide1:0.present")}")
        ret["present"] = params["value"]
        params = self.get(f"vms/{vid}/params/{quote("ide1:0.startConnected")}")
        ret["start_connected"] = params["value"]

        return ret

    def get_vmx(self, name):
        vm = self.get_vm(name)
        return vm.vmx.read_text()

    def _vnc_port(self, vid):
        vmip = self.get_ip(None, vid=vid)
        ip = vmip.get("ip", "0.0.0.0")
        host = int(ip.split(".")[-1])
        port = 5900 + (host & 0xFF)
        return port

    def vnc(self, name, enable=False, disable=False, port=None, address=None):
        ret = {}
        vid = self.get_vid(name)
        ret["id"] = vid
        if enable:
            self.put(f"vms/{vid}/params", json=dict(name="RemoteDisplay.vnc.enabled", value="TRUE"), parse_json=False)
            port = port or self._vnc_port(vid)
            address = address or "127.0.0.1"
            if str(address) in ["0.0.0.0", "egress", "public"]:
                address = socket.gethostbyname(self.host)
        if disable:
            self.put(f"vms/{vid}/params", json=dict(name="RemoteDisplay.vnc.enabled", value="FALSE"), parse_json=False)
        if port:
            self.put(f"vms/{vid}/params", json=dict(name="RemoteDisplay.vnc.port", value=str(port)), parse_json=False)
        if address:
            self.put(f"vms/{vid}/params", json=dict(name="RemoteDisplay.vnc.ip", value=str(address)), parse_json=False)

        for param in ["enabled", "port", "ip"]:
            result = self.get(f"vms/{vid}/params/{'RemoteDisplay.vnc.' + param}")
            ret[param] = result["value"]

        return ret

    def clipboard(self, name, copy=None, paste=None, dnd=None, hgfs=None):
        ret = {}
        vid = self.get_vid(name)
        ret["id"] = vid
        params = {
            "isolation.tools.copy.disable": copy, 
            "isolation.tools.paste.disable": paste, 
            "isolation.tools.dnd.disable": dnd,
            "isolation.tools.hgfs.disable": hgfs
        }
        for key, value in params.items():
            if value is not None:
                self.put(f"vms/{vid}/params", json=dict(name=key, value="FALSE" if value else "TRUE"), parse_json=False)

        detail = self.get_detail(name)
        isolation = detail['guestIsolation']
        
        for key in params.keys():
            ret['copy'] = "FALSE" if isolation['copyDisabled'] else "TRUE"
            ret['paste'] = "FALSE" if isolation['pasteDisabled'] else "TRUE"
            ret['dnd'] = "FALSE" if isolation['dndDisabled'] else "TRUE"
            ret['hgfs'] = "FALSE" if isolation['hgfsDisabled'] else "TRUE"

        return ret


    def boot(self, name):
        ret = {}
        vid = self.get_vid(name)
        ret["id"] = vid

        for param in ["bootOrder", "hddOrder", "bootDeviceClasses"]:
            result = self.get(f"vms/{vid}/params/bios.{param}")
            ret[param] = result["value"]

        return ret
