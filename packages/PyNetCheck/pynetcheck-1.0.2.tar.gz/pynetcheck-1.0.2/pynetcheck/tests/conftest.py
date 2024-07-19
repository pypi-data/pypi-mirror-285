import os
from importlib import metadata
from pathlib import Path
from typing import Optional, Any

from ipfabric import IPFClient
from pydantic import BaseModel

IPF, CONFIGS = None, []


class ConfigFile(BaseModel):
    file: Path
    parsed: Optional[Any] = None
    raw: Optional[Any] = None


def pytest_addoption(parser):
    parser.addoption(
        "--config-dir",
        help="Path to directory with configurations.",
        action="store",
        type=Path,
    )
    parser.addoption(
        "--snapshot",
        help="Optional: IP Fabric Snapshot ID; defaults to `$last`.",
        action="store",
        default=None,
        type=str,
    )
    parser.addoption(
        "--ipf-url",
        help="IP Fabric URL: `https://demo1.us.ipfabric.io/`, (or use `IPF_URL` in`.env` file).",
        action="store",
        default=None,
        type=str,
    )
    parser.addoption(
        "--ipf-token",
        help="IP Fabric Token, (or use `IPF_TOKEN` in `.env` file).",
        action="store",
        default=None,
        type=str,
    )
    parser.addoption(
        "--insecure",
        help="Verify IP Fabric Certificate, defaults to `True`, (or use `IPF_VERIFY` in`.env` file).",
        dest='insecure',
        action="store_false",
    )


def pytest_configure(config):
    global IPF, CONFIGS

    if config.getoption("--config-dir"):
        cfg_dir = config.getoption("--config-dir").resolve()
        CONFIGS = [ConfigFile(file=cfg_dir / f) for f in os.listdir(cfg_dir)]
    else:
        IPF = IPFClient(
            base_url=config.getoption("--ipf-url"),
            auth=config.getoption("--ipf-token"),
            verify=config.getoption("--insecure", None),
            snapshot_id=config.getoption("--snapshot"),
        )
        IPF._client.headers['user-agent'] += f'; python-pynetcheck/{metadata.version("pynetcheck")}'
