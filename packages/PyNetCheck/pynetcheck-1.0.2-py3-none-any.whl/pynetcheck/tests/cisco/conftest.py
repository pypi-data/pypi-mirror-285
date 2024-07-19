from pynetcheck.models.device import IPFDevice
from pynetcheck.tests.conftest import IPF


if not IPF:
    CISCO, ASA, IOS, IOSXE, IOSXR, NXOS = [], [], [], [], [], []
else:
    # Get all Cisco devices
    CISCO = [
        IPFDevice(ipf=IPF, device=d) for d in IPF.devices.by_vendor.get("cisco", [])
    ]
    ASA = [IPFDevice(ipf=IPF, device=d) for d in IPF.devices.by_family.get("asa", [])]
    IOS = [IPFDevice(ipf=IPF, device=d) for d in IPF.devices.by_family.get("ios", [])]
    IOSXE = [
        IPFDevice(ipf=IPF, device=d) for d in IPF.devices.by_family.get("ios-xe", [])
    ]
    IOSXR = [
        IPFDevice(ipf=IPF, device=d) for d in IPF.devices.by_family.get("ios-xr", [])
    ]
    NXOS = [
        IPFDevice(ipf=IPF, device=d) for d in IPF.devices.by_family.get("nx-os", [])
    ]
