from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, TypeAdapter
import json
from typing import Dict
import uvicorn
import httpx

from common.util import Logger, AsyncFs
from common.server_config import HOST, SDKSERVER_PORT
from sdkserver.config.version_config import VersionConfig, CONFIG_PATH
from sdkserver.services.auth import auth_router
from sdkserver.services.dispatch import dispatch_router
from sdkserver.services.sr_tools import sr_tools_router


class AppState:
    def __init__(self):
        self.hotfix_map: Dict[str, VersionConfig] = VersionConfig.load_hotfix()
        self.http_client = httpx.AsyncClient()

    async def get_or_insert_hotfix(self, version: str, seed: str) -> VersionConfig:
        if version in self.hotfix_map:
            return self.hotfix_map[version]

        Logger.info(
            f"Trying to fetch hotfix for version {version} with dispatch seed {seed}"
        )

        version_config: VersionConfig = await VersionConfig.fetch_hotfix(
            version, seed, self.http_client
        )
        if not version_config:
            version_config = VersionConfig()

        self.hotfix_map[version] = version_config

        # this is fucking stupid but i can't find any way to dump a TypeAdapter with pydantic
        to_dump = {}
        for k, v in self.hotfix_map.items():
            to_dump[k] = v.model_dump()

        if len(to_dump) > 0:
            json_str = json.dumps(to_dump, indent=2)
            await AsyncFs.write_to_file(CONFIG_PATH, json_str)

        return self.hotfix_map[version]


if __name__ == "__main__":
    fuckass = AppState()
    app = FastAPI()
    app.state.fuckass = fuckass
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(dispatch_router)
    app.include_router(auth_router)
    app.include_router(sr_tools_router)

    h_map = fuckass.hotfix_map
    h_cnt, h_keys = (len(h_map), h_map.keys())
    Logger.info(f"loaded {h_cnt} hotfix(es): {h_keys}")

    uvicorn.run(app, host=HOST, port=SDKSERVER_PORT)
