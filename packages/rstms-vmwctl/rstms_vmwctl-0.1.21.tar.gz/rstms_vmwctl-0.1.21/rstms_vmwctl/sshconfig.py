# local ssh config update

import os
from pathlib import Path
from subprocess import run

from .vmware_workstation import VMFailure


class SSHConfig:
    def __init__(self, ctx, name):
        self.name = name
        status = ctx.get_status(name)
        self.ip = status["ip"]
        self.mac = status["mac"]
        if not self.ip:
            raise VMFailure(f"{name} has no ip")
        if not self.mac:
            raise VMFailure(f"{name} has no mac address")

    def run(self, cmd, **kwargs):
        fail_ok = kwargs.pop("fail_ok", False)
        kwargs.setdefault("capture_output", True)
        kwargs.setdefault("text", True)
        kwargs.setdefault("check", True)
        proc = run(cmd, **kwargs)
        if proc.returncode != 0 and fail_ok is False:
            raise VMFailure(proc.stderr)
        return proc

    def update(self):
        known_hosts = Path.home() / ".ssh/known_hosts"
        self.run(["ssh-keygen", "-f", str(known_hosts), "-R", self.name], fail_ok=True)
        self.run(["ssh-keygen", "-f", str(known_hosts), "-R", self.ip], fail_ok=True)
        self.run(["sh", "-c", f"ssh-keyscan {self.name} >> {str(known_hosts)}"])
        self.run(["ssh", "-o", "UpdateHostKeys=yes", "-o", "StrictHostKeyChecking=no", self.name, "uptime"])

    def exec(self):
        os.execvp("ssh", ["ssh", self.name])
