import os

import pytest

from pynetcheck.models.device import IPFDevice
from pynetcheck.models.shared import return_http_config
from .conftest import CISCO


@pytest.mark.cisco
@pytest.mark.parametrize(
    "device", CISCO, ids=[d.inventory.hostname for d in CISCO], scope="class"
)
class TestCiscoServices:
    __test__ = True if CISCO else False

    @pytest.fixture(autouse=True, scope="class")
    def load_device_data(self, device: IPFDevice):
        if "ios" not in device.inventory.family:
            pytest.skip(
                f"Currently not implemented for family: {device.inventory.family}"
            )
        if not device.loaded:
            device.load_data()
        if not device.parsed_config:
            pytest.skip("No configs for device.")
        yield
        device.clear_data()

    @staticmethod
    def return_status(variable: str):
        check = (
            "enabled"
            if os.getenv(variable, "ENABLED").upper() == "DISABLED"
            else "disabled"
        )
        status = "Disabled" if check == "enabled" else "Enabled"
        return check, status

    def test_http_server(self, device: IPFDevice):
        """Set HTTP_SERVER=DISABLED to fail if HTTP(s) servers are disabled."""
        check, status = self.return_status("CISCO_HTTP_SERVER")
        current, startup = return_http_config(device, "server")
        assert current == check, f"Running Config - HTTP server {status}"
        if device.config.status != "saved" and startup:
            assert startup == check, f"Startup Config - HTTP server {status}"

    def test_https_server(self, device: IPFDevice):
        """Set HTTP_SERVER=DISABLED to fail if HTTP(s) servers are disabled."""
        check, status = self.return_status("CISCO_HTTPS_SERVER")
        current, startup = return_http_config(device, "secure-server")
        assert current == check, f"Running Config - HTTPS server {status}"
        if device.config.status != "saved" and startup:
            assert startup == check, f"Startup Config - HTTPS server {status}"

    def test_scp_server(self, device: IPFDevice):
        """Set SCP_SERVER=DISABLED to fail if SCP Server is disabled."""
        check, status = self.return_status("CISCO_SCP_SERVER")

        assert (
            "enabled"
            if device.parsed_config.current.find_lines("^ip scp server enable")
            else "disabled" == check
        ), f"Running Config - SCP Server {status}"
        if device.config.status != "saved" and device.parsed_config.startup:
            assert (
                "enabled"
                if device.parsed_config.startup.find_lines("^ip scp server enable")
                else "disabled" == check
            ), f"Startup Config - SCP Server {status}"
