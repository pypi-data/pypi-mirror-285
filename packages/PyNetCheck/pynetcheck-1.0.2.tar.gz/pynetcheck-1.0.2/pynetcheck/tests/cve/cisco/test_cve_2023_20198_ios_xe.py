"""
https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-iosxe-webui-privesc-j22SaA4z

This will test for the following:
    - HTTP(S) Server Disabled
    - If Enabled then test HTTP(S) Server Vulnerable
"""

import pytest
from ciscoconfparse import CiscoConfParse
from netutils.os_version import compare_version_loose

from pynetcheck.models.device import IPFDevice
from pynetcheck.models.shared import return_http_config
from pynetcheck.tests.cisco.conftest import IOSXE
from pynetcheck.tests.conftest import CONFIGS, ConfigFile

pytestmark = [pytest.mark.cve, pytest.mark.cisco]

RUNNING = "Running Config - HTTP"
STARTUP = "Startup Config - HTTP"


# Test each device for HTTP(S) Server configuration in running and startup configs
@pytest.mark.parametrize(
    "device", IOSXE, ids=[d.inventory.hostname for d in IOSXE], scope="class"
)
class TestHTTPServerIPF:
    __test__ = True if IOSXE else False  # If no devices then skip

    @pytest.fixture(autouse=True, scope="class")
    def load_device_data(self, device: IPFDevice):
        if not device.loaded:
            device.load_data()
        if not device.parsed_config:
            pytest.skip("No configs for device.  Please check if `Saved Config Consistency` Discovery Task is Enabled.")
        yield
        device.clear_data()

    @staticmethod
    def return_module_config(device: IPFDevice, server):
        current, startup = return_http_config(device, server)
        if current != "enabled" and startup != "enabled":
            pytest.skip(f"HTTP {server} Disabled")
        line = (
            "^ip http active-session-modules none"
            if server == "server"
            else "^ip http secure-active-session-modules none"
        )
        mcurrent = (
            "secured" if device.parsed_config.current.find_lines(line) else "vulnerable"
        )
        mstartup = None
        if device.config.status != "saved" and startup:
            mstartup = (
                "secured"
                if device.parsed_config.startup.find_lines(line)
                else "vulnerable"
            )
        return mcurrent, mstartup

    @staticmethod
    def check_version(device: IPFDevice):
        if (
            (compare_version_loose(device.inventory.version, "<=", "17.3.8a"))
            or (
                compare_version_loose(device.inventory.version, ">=", "17.4")
                and compare_version_loose(device.inventory.version, "<", "17.6.6a")
            )
            or (
                compare_version_loose(device.inventory.version, ">=", "17.7")
                and compare_version_loose(device.inventory.version, "<", "17.9.4a")
            )
        ):
            return True
        return False

    def test_http_server_disabled(self, device: IPFDevice):
        current, startup = return_http_config(device, "server")
        assert current == "disabled", f"{RUNNING} server Enabled"
        if device.config.status != "saved" and startup:
            assert startup == "disabled", f"{STARTUP} server Enabled"

    def test_https_server_disabled(self, device: IPFDevice):
        current, startup = return_http_config(device, "secure-server")
        assert current == "disabled", f"{RUNNING} secure-server Enabled"
        if device.config.status != "saved" and startup:
            assert startup == "disabled", f"{STARTUP} secure-server Enabled"

    def test_http_server_vulnerable(self, device: IPFDevice):
        if not self.check_version(device):
            pytest.skip(
                f"{device.inventory.hostname}:{device.inventory.sn} is not an affected SW Version {device.inventory.version}."
            )
        mcurrent, mstartup = self.return_module_config(device, "server")
        assert mcurrent == "secured", f"{RUNNING} server Vulnerable"
        if device.config.status != "saved" and mstartup:
            assert mstartup == "secured", f"{RUNNING} server Vulnerable"

    def test_https_server_vulnerable(self, device: IPFDevice):
        if not self.check_version(device):
            pytest.skip(
                f"{device.inventory.hostname}:{device.inventory.sn} is not an affected SW Version {device.inventory.version}."
            )
        mcurrent, mstartup = self.return_module_config(device, "secure-server")
        assert mcurrent == "secured", f"{RUNNING} server Vulnerable"
        if device.config.status != "saved" and mstartup:
            assert mstartup == "secured", f"{RUNNING} server Vulnerable"


# Test each config file in `dir` directory for HTTP(S) Server configuration
@pytest.mark.parametrize(
    "config_file", CONFIGS, ids=[c.file.name for c in CONFIGS], scope="class"
)
class TestHTTPServerConfig(object):
    __test__ = True if CONFIGS else False  # If no configs then skip

    @pytest.fixture(autouse=True, scope="class")
    def load_configuration(self, config_file: ConfigFile):
        with open(config_file.file, "r") as file:
            config_file.parsed = CiscoConfParse(
                file.readlines(), syntax="ios", ignore_blank_lines=False
            )
        yield
        config_file.parsed = None

    def test_http_server_disabled(self, config_file):
        assert config_file.parsed.find_lines(
            "^no ip http server"
        ), "HTTP server Enabled"

    def test_http_server_vulnerable(self, config_file):
        if config_file.parsed.find_lines("^no ip http server"):
            pytest.skip("HTTP server Disabled")
        assert config_file.parsed.find_lines(
            "^ip http active-session-modules none"
        ), "HTTP server Vulnerable"

    def test_https_server_disabled(self, config_file):
        assert config_file.parsed.find_lines(
            "^no ip http secure-server"
        ), "HTTP secure-server Enabled"

    def test_https_server_vulnerable(self, config_file):
        if config_file.parsed.find_lines("^no ip http secure-server"):
            pytest.skip("HTTP secure-server Disabled")
        assert config_file.parsed.find_lines(
            "^ip http secure-active-session-modules none"
        ), "HTTP secure-server Vulnerable"
