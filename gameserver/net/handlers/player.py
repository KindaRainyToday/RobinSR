from proto import *
from gameserver.util import cur_timestamp_ms


async def on_get_basic_info_cs_req(
    _session: "PlayerSession",
    _body: GetBasicInfoCsReq,
    res: GetBasicInfoScRsp,
) -> None:
    res.player_setting_info = PlayerSettingInfo()
    res.gender = int(Gender.GenderWoman)
    res.is_gender_set = True


async def on_player_heart_beat_cs_req(
    _session: "PlayerSession",
    body: PlayerHeartBeatCsReq,
    res: PlayerHeartBeatScRsp,
) -> None:
    res.client_time_ms = body.client_time_ms
    res.server_time_ms = cur_timestamp_ms()


async def on_player_login_finish_cs_req(
    session: "PlayerSession",
    _req: PlayerLoginFinishCsReq,
    _res: PlayerLoginFinishScRsp,
) -> None:
    session.send(
        cmd_id=CmdID.ContentPackageSyncDataScNotify,
        body=ContentPackageSyncDataScNotify(
            data=ContentPackageData(
                content_package_list=[
                    ContentPackageInfo(
                        status=ContentPackageStatus.ContentPackageStatus_Finished,
                        content_id=id,
                    )
                    for id in [
                        200001,
                        200002,
                        200003,
                        200004,
                        150017,
                        150015,
                        150021,
                        150018,
                        130011,
                        130012,
                        130013,
                    ]
                ]
            )
        ),
    )


async def on_get_multi_path_avatar_info_cs_req(
    session: "PlayerSession",
    _req: GetMultiPathAvatarInfoCsReq,
    res: GetMultiPathAvatarInfoScRsp,
) -> None:
    res.cur_avatar_path[1001] = session.json_data._march_type.get_type()
    res.cur_avatar_path[8001] = session.json_data._main_character.get_type()
    res.multi_path_avatar_info_list = session.json_data.get_multi_path_info()
