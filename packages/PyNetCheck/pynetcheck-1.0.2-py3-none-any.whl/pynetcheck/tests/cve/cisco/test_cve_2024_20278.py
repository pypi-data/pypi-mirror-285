"""
https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-iosxe-priv-esc-seAx6NLX
"""

import pytest
from ciscoconfparse import CiscoConfParse

from pynetcheck.models.device import IPFDevice
from pynetcheck.models.shared import return_service_config
from pynetcheck.tests.cisco.conftest import IOSXE
from pynetcheck.tests.conftest import CONFIGS, ConfigFile

pytestmark = [pytest.mark.cve, pytest.mark.cisco]


@pytest.mark.parametrize(
    "device", IOSXE, ids=[d.inventory.hostname for d in IOSXE], scope="class"
)
class TestNetConfYang:
    __test__ = True if IOSXE else False  # If no devices then skip

    @pytest.fixture(autouse=True, scope="class")
    def load_device_data(self, device: IPFDevice):
        if not device.loaded:
            device.load_data()
        if not device.parsed_config:
            pytest.skip("No configs for device.  Please check if `Saved Config Consistency` Discovery Task is Enabled.")
        yield
        device.clear_data()

    def test_netconf_yang_disabled(self, device: IPFDevice):
        current, startup = return_service_config(device, "netconf-yang")
        assert current == "disabled", "Running Config - netconf-yang Enabled"
        if device.config.status != "saved" and startup:
            assert startup == "disabled", "Startup Config - netconf-yang Enabled"


@pytest.mark.parametrize(
    "config_file", CONFIGS, ids=[c.file.name for c in CONFIGS], scope="class"
)
class TestNetConfYangConfig(object):
    __test__ = True if CONFIGS else False  # If no configs then skip

    @pytest.fixture(autouse=True, scope="class")
    def load_configuration(self, config_file: ConfigFile):
        with open(config_file.file, "r") as file:
            config_file.parsed = CiscoConfParse(
                file.readlines(), syntax="ios", ignore_blank_lines=False
            )

            print("SETUP", config_file.file.name)
        yield
        config_file.parsed = None
        print("TEARDOWN", config_file.file.name)

    def test_netconf_yang_disabled(self, config_file):
        line = "^netconf-yang"
        assert not config_file.parsed.find_lines(line), "Config - netconf-yang Enabled"
