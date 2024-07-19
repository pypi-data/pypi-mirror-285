import re
from typing import Optional

from ciscoconfparse import CiscoConfParse
from ipfabric import IPFClient
from ipfabric.models.device import Device, DeviceConfig


def parse_family(family: str):
    if "ios" in family:
        return "ios"
    elif "asa" in family:
        return "asa"
    elif "nx-os" == family:
        return "nxos"
    elif "asa" == family:
        return "asa"
    else:
        return family


class ParsedConfig:
    def __init__(self, current: CiscoConfParse, startup: CiscoConfParse = None):
        self.current: CiscoConfParse = current
        self.startup: Optional[CiscoConfParse] = startup if startup else None


class IPFDevice:
    def __init__(self, ipf: IPFClient, device: Device):
        self.ipf: IPFClient = ipf
        self.inventory: Device = device
        self.site: str = device.site.upper()
        self.loaded: bool = False

        # Config will load when test is run and then be removed to saved memory.
        self.config: Optional[DeviceConfig] = None
        self.parsed_config: Optional[ParsedConfig] = None

    def __repr__(self):
        return f"{self.inventory.hostname}:{self.inventory.sn}"

    def load_data(self):
        self.get_config()
        self.loaded = True

    def clear_data(self):
        self.config = None
        self.parsed_config = None
        self.loaded = False

    def _cisco_config(self):
        current = (
            CiscoConfParse(
                self.config.current.split("\n"),
                syntax=parse_family(self.inventory.family),
                ignore_blank_lines=False,
            )
            if self.config.current
            else None
        )
        startup = (
            CiscoConfParse(
                self.config.start.split("\n"),
                syntax=parse_family(self.inventory.family),
                ignore_blank_lines=False,
            )
            if self.config.start
            else None
        )
        if self.config.current:
            self.parsed_config = ParsedConfig(current, startup)

    def _palo_alto_config(self):
        log = self.inventory.get_log_file()
        user = re.search(r"(\S*)@", log.split("\n")[0]).group(1)
        self.config = DeviceConfig(
            currentConfig=re.split(
                rf"^{user}", log.split("show config merged")[1], flags=re.M
            )[0].replace("\r\n", "\n"),
            startupConfig=None,
            status="N/A",
        )

    def get_config(self):
        if self.inventory.vendor == "cisco":
            self.config = self.inventory.get_config()
            self._cisco_config()
        elif self.inventory.vendor == "paloalto":
            self._palo_alto_config()
