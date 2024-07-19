from typing import Tuple

from pynetcheck.models.device import IPFDevice


def return_http_config(device: IPFDevice, server: str) -> Tuple[str, str]:
    line = f"^ip http {server}"
    current = "enabled" if device.parsed_config.current.find_lines(line) else "disabled"
    startup = None
    if device.config.status != "saved" and device.parsed_config.startup:
        startup = (
            "enabled" if device.parsed_config.startup.find_lines(line) else "disabled"
        )
    return current, startup


def return_service_config(device: IPFDevice, service: str) -> Tuple[str, str]:
    line = f"^{service}"
    current = "enabled" if device.parsed_config.current.find_lines(line) else "disabled"
    startup = None
    if device.config.status != "saved" and device.parsed_config.startup:
        startup = (
            "enabled" if device.parsed_config.startup.find_lines(line) else "disabled"
        )
    return current, startup
