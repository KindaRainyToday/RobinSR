from common.structs.avatar import AvatarJson
from proto import *


async def on_get_all_lineup_data_cs_req(
    session: "PlayerSession",
    _body: GetAllLineupDataCsReq,
    res: GetAllLineupDataScRsp,
) -> None:
    res.lineup_list = [
        LineupInfo(
            extra_lineup_type=ExtraLineupType.LINEUP_NONE,
            name="Squad 1",
            mp=5,
            max_mp=5,
            avatar_list=AvatarJson.to_lineup_avatars(session.json_data),
        )
    ]


async def on_get_cur_lineup_data_cs_req(
    session: "PlayerSession",
    _body: GetCurLineupDataCsReq,
    res: GetCurLineupDataScRsp,
) -> None:
    res.lineup = LineupInfo(
        extra_lineup_type=ExtraLineupType.LINEUP_NONE,
        name="Squad 1",
        mp=5,
        max_mp=5,
        avatar_list=AvatarJson.to_lineup_avatars(session.json_data),
    )


def refresh_lineup(session: "PlayerSession") -> None:
    floor_id = session.json_data._scene.floor_id

    lineup = LineupInfo(
        extra_lineup_type=ExtraLineupType.LINEUP_NONE,
        name="Squad 1",
        mp=5,
        max_mp=5,
        avatar_list=AvatarJson.to_lineup_avatars(session.json_data),
    )

    new_entities = [
        SceneEntityRefreshInfo(
            add_entity=SceneEntityInfo(
                actor=SceneActorInfo(
                    uid=25,
                    avatar_type=AvatarType.AVATAR_FORMAL_TYPE,
                    base_avatar_id=v,
                ),
                entity_id=idx + 1,
            )
        )
        for idx, v in session.json_data._lineups.items()
    ]

    session.send(
        cmd_id=CmdID.SceneGroupRefreshScNotify,
        body=SceneGroupRefreshScNotify(
            group_refresh_list=[
                GroupRefreshInfo(
                    refresh_type=SceneGroupRefreshType.SCENE_GROUP_REFRESH_TYPE_LOADED,
                    refresh_entity=new_entities,
                )
            ],
            floor_id=floor_id,
        ),
    )

    session.send(cmd_id=CmdID.SyncLineupNotify, body=SyncLineupNotify(lineup=lineup))


async def on_join_lineup_cs_req(
    session: "PlayerSession",
    body: JoinLineupCsReq,
    _res: JoinLineupScRsp,
) -> None:
    session.json_data._lineups[body.slot] = body.base_avatar_id
    await session.json_data.save_persistent()
    refresh_lineup(session)


async def on_replace_lineup_cs_req(
    session: "PlayerSession",
    req: ReplaceLineupCsReq,
    _res: ReplaceLineupScRsp,
) -> None:
    for slot, _ in session.json_data._lineups.items():
        if 0 <= slot < len(req.lineup_slot_list):
            new_id = req.lineup_slot_list[slot].id
            session.json_data._lineups[slot] = new_id
        else:
            new_id = 0
            session.json_data._lineups[slot] = new_id

    await session.json_data.save_persistent()
    refresh_lineup(session)


async def on_quit_lineup_cs_req(
    session: "PlayerSession",
    _: QuitLineupCsReq,
    _res: QuitLineupScRsp,
) -> None:
    pass


async def on_change_lineup_leader_cs_req(
    _session: "PlayerSession",
    body: ChangeLineupLeaderCsReq,
    res: ChangeLineupLeaderScRsp,
) -> None:
    res.slot = body.slot
