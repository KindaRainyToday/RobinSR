from gameserver.util import cur_timestamp_ms
from proto import *


async def on_player_get_token_cs_req(
    _session: "PlayerSession", _body: PlayerGetTokenCsReq, res: PlayerGetTokenScRsp
) -> None:
    res.msg = "OK"
    res.uid = 25


async def on_player_login_cs_req(
    _session: "PlayerSession", body: PlayerLoginCsReq, res: PlayerLoginScRsp
) -> None:
    res.login_random = body.login_random
    res.server_timestamp_ms = cur_timestamp_ms()
    res.stamina = 240
    res.basic_info = PlayerBasicInfo(
        nickname="RobinSR",
        level=70,
        world_level=6,
        stamina=240,
    )
