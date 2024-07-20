# vmx template

from pathlib import Path


def _flag(value):
    return "TRUE" if value else "FALSE"


class VMX:

    template = """
.encoding = "UTF-8"
config.version = "8"
virtualHW.version = "19"
displayName = "{{NAME}}"
numvcpus = "{{CPU}}"
memsize = "{{RAM}}"
guestOS = "{{GUEST}}"
pciBridge0.present = "TRUE"
pciBridge4.present = "TRUE"
pciBridge4.virtualDev = "pcieRootPort"
pciBridge4.functions = "8"
pciBridge5.present = "TRUE"
pciBridge5.virtualDev = "pcieRootPort"
pciBridge5.functions = "8"
pciBridge6.present = "TRUE"
pciBridge6.virtualDev = "pcieRootPort"
pciBridge6.functions = "8"
pciBridge7.present = "TRUE"
pciBridge7.virtualDev = "pcieRootPort"
pciBridge7.functions = "8"
nvme0.present = "TRUE"
nvme0:0.fileName = "{{DISK}}"
nvme0:0.present = "TRUE"
floppy0.present = "FALSE"
ide1:0.present = "FALSE"
ethernet0.present = "FALSE"
vmx.scoreboard.enabled = "FALSE"
tools.syncTime = "{{TIME_SYNC}}"
isolation.tools.dnd.disable = "{{DRAG_AND_DROP_DISABLE}}"
isolation.tools.copy.disable = "{{CLIPBOARD_COPY_DISABLE}}"
isolation.tools.paste.disable = "{{CLIPBOARD_PASTE_DISABLE}}"
"""

    def __init__(self, vmx_path):
        self.path = Path(vmx_path)

    def generate(
        self,
        *,
        cpu_count,
        ram_mb,
        vmdk_pathname,
        guest_os="other-64",
        efi=False,
        time_sync=False,
        drag_and_drop=False,
        clipboard=False,
    ):

        self.text = self.template
        self._apply("NAME", self.path.stem)
        self._apply("CPU", str(cpu_count))
        self._apply("RAM", str(ram_mb))
        self._apply("DISK", str(vmdk_pathname))
        self._apply("GUEST", guest_os)
        self._apply("TIME_SYNC", _flag(time_sync))
        self._apply("DRAG_AND_DROP_DISABLE", _flag(not drag_and_drop))
        self._apply("CLIPBOARD_COPY_DISABLE", _flag(not clipboard))
        self._apply("CLIPBOARD_PASTE_DISABLE", _flag(not clipboard))
        self.set_cdrom(None, False)
        self.set_ethernet(False)
        if efi:
            self.text += '\nfirmware = "efi"'

    def _apply(self, macro, value):
        self.text = self.text.replace("{{" + macro + "}}", value)

    def set_cdrom(self, iso_pathname=None, connected=False):
        self.iso_pathname = iso_pathname
        self.iso_connected = connected
        self._update("ide1", self._cdrom)

    def _cdrom(self):
        lines = []
        if self.iso_pathname is not None:
            lines.append('ide1:0.present = "TRUE"')
            lines.append('ide1:0.deviceType = "cdrom-image"')
            lines.append(f'ide1:0.fileName = "{str(self.iso_pathname)}"')
            if self.iso_connected:
                lines.append('ide1:0.startConnected = "TRUE"')
            else:
                lines.append('ide1:0.startConnected = "FALSE"')
        else:
            lines.append('ide1:0.present = "FALSE"')
        return lines

    def set_ethernet(self, present=True, mac=None):
        self.ethernet = present
        self.mac = mac
        self._update("ethernet", self._ethernet)

    def _ethernet(self):
        lines = []
        if self.ethernet:
            lines.append('ethernet0.present = "TRUE"')
            lines.append('ethernet0.virtualDev = "e1000"')
            if self.mac:
                lines.append(f'ethernet0.address = "{self.mac}"')
                lines.append('ethernet0.addressType = "static"')
            else:
                lines.append('ethernet0.addressType = "generated"')
        else:
            lines.append('ethernet0.present = "FALSE"')
        return lines

    def _update(self, prefix, add_lines):
        lines = []
        updated = False
        for line in self.text.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith(prefix):
                continue
            if line.startswith("uuid"):
                if not updated:
                    lines.extend(add_lines())
                    updated = True
            lines.append(line)
        if not updated:
            lines.extend(add_lines())
        self.text = "\n".join(lines)

    def read(self):
        self.text = self.path.read_text()

    def write(self):
        self.path.write_text(self.text)
