from proto import RegionInfo, Dispatch, GateServer
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import PlainTextResponse
from common.server_config import HOST, GAMESERVER_PORT, SDKSERVER_PORT
from common.util import Logger
from sdkserver.config.version_config import VersionConfig
import base64

dispatch_router = APIRouter()


@dispatch_router.get("/query_dispatch")
async def query_dispatch() -> PlainTextResponse:
    dispatch = Dispatch(
        region_list=[
            RegionInfo(
                name="RobinSR",
                title="RobinSR",
                env_type="22",
                dispatch_url=f"http://{HOST}:{SDKSERVER_PORT}/query_gateway",
            )
        ]
    )
    response_data = base64.b64encode(bytes(dispatch))
    return PlainTextResponse(content=response_data)


@dispatch_router.get("/query_gateway")
async def query_gateway(req: Request) -> PlainTextResponse:
    version = req.query_params.get("version")
    seed = req.query_params.get("dispatch_seed")
    if not version:
        Logger.warn("version query is null!")
    if not seed:
        Logger.warn("dispatch_seed query is null!")

    config: VersionConfig
    if version and seed:
        config = await req.app.state.fuckass.get_or_insert_hotfix(version, seed)
    else:
        config = VersionConfig()

    gateserver = GateServer(
        use_tcp=False,
        ip=HOST,
        port=GAMESERVER_PORT,
        asset_bundle_url=config.asset_bundle_url,
        ex_resource_url=config.ex_resource_url,
        lua_url=config.lua_url,
        ifix_version="0",
        enable_design_data_version_update=True,
        enable_version_update=True,
        enable_upload_battle_log=True,
        network_diagnostic=True,
        close_redeem_code=True,
        enable_android_middle_package=True,
        enable_watermark=True,
        event_tracking_open=True,
        enable_save_replay_file=True,
        enable_cdn_ipv6=1,
    )
    response_data = base64.b64encode(bytes(gateserver))
    return PlainTextResponse(content=response_data)
