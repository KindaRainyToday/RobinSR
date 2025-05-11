from typing import Dict, Optional
from proto import GateServer
from pydantic import BaseModel, TypeAdapter
from common.util import SyncFs, Logger
import asyncio
import httpx
import base64

CONFIG_PATH = "versions.json"

DEFAULT_VERSIONS = """{  
  "OSPRODWin3.3.0": {
    "asset_bundle_url": "",
    "ex_resource_url": "",
    "lua_url": "",
    "ifix_url": ""
  }
}"""

CNPROD_HOST = "prod-gf-cn-dp01.bhsr.com"
CNBETA_HOST = "beta-release01-cn.bhsr.com"
OSPROD_HOST = "prod-official-asia-dp01.starrails.com"
OSBETA_HOST = "beta-release01-asia.starrails.com"
PROXY_HOST = "proxy1.neonteam.dev"


class VersionConfig(BaseModel):
    asset_bundle_url: str = ""
    ex_resource_url: str = ""
    lua_url: str = ""
    ifix_url: str = ""

    @staticmethod
    def load_hotfix() -> Dict[str, "VersionConfig"]:
        try:
            data = SyncFs.read_to_str(CONFIG_PATH)
        except Exception:
            SyncFs.write_to_file(CONFIG_PATH, DEFAULT_VERSIONS)
            data = DEFAULT_VERSIONS

        try:
            return TypeAdapter(Dict[str, VersionConfig]).validate_json(data)
        except Exception:
            Logger.error("malformed versions.json. replacing it with default one")
            SyncFs.write_to_file(CONFIG_PATH, DEFAULT_VERSIONS)
            return TypeAdapter(Dict[str, VersionConfig]).validate_json(DEFAULT_VERSIONS)

    @staticmethod
    def create_gateway_url(version: str, seed: str) -> Optional[str]:
        host: Optional[str]
        if version.startswith("CNP"):
            host = CNPROD_HOST
        elif version.startswith("CNB"):
            host = CNBETA_HOST
        elif version.startswith("OSP"):
            host = OSPROD_HOST
        elif version.startswith("OSB"):
            host = OSBETA_HOST
        else:
            return None
        return f"https://{PROXY_HOST}/{host}/query_gateway?version={version}&dispatch_seed={seed}&language_type=1&platform_type=2&channel_id=1&sub_channel_id=1&is_need_url=1&account_type=1"

    @staticmethod
    async def fetch_hotfix(
        version: str, seed: str, client: httpx.AsyncClient
    ) -> Optional["VersionConfig"]:
        url = VersionConfig.create_gateway_url(version, seed)
        if not url:
            Logger.error(f"Invalid version: {version}")
            return None

        Logger.info(f"Fetching hotfix: {url}")

        try:
            resp = await client.get(url)
            encoded = resp.text

            decoded_bytes = base64.b64decode(encoded)
            gateserver = GateServer().parse(decoded_bytes)

            if not gateserver.asset_bundle_url and not gateserver.ex_resource_url:
                Logger.error("Empty hotfix URLs received.")
                return None

            Logger.info(f"fetching hotfix success: {gateserver}")

            return VersionConfig(
                asset_bundle_url=gateserver.asset_bundle_url,
                ex_resource_url=gateserver.ex_resource_url,
                lua_url=gateserver.lua_url,
                ifix_url=gateserver.ifix_url,
            )

        except Exception as e:
            Logger.error(f"Error while fetching hotfix: {e}")
            return None
