from pynetcheck.models.device import IPFDevice
from pynetcheck.tests.conftest import IPF


if not IPF:
    PALOALTO, PRISMA, PA_FW, PANORAMA = [], [], [], []
else:
    # Get all Palo Alto devices
    PALOALTO = [
        IPFDevice(ipf=IPF, device=d) for d in IPF.devices.by_vendor.get("paloalto", [])
    ]
    PRISMA = [
        IPFDevice(ipf=IPF, device=d) for d in IPF.devices.by_family.get("ion", [])
    ]
    PA_FW = [
        IPFDevice(ipf=IPF, device=d)
        for d in sum(
            list(
                IPF.devices.by_vendor.search("paloalto")
                .sub_regex("model", r"^pa(?!norama).*")
                .values()
            ),
            [],
        )
    ]
    PANORAMA = [
        IPFDevice(ipf=IPF, device=d) for d in IPF.devices.by_model.get("panorama", [])
    ]
