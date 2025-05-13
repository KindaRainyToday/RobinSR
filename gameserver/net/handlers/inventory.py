from common.sr_tools import FreesrData
from proto import *
from gameserver.net.handlers.avatar import UNLOCKED_AVATARS
from typing import Optional, List


async def on_get_bag_cs_req(
    session: "PlayerSession",
    _req: GetBagCsReq,
    res: GetBagScRsp,
) -> None:
    res.equipment_list = [l.to_equipment_proto() for l in session.json_data.lightcones]
    res.relic_list = [r.to_relic_proto() for r in session.json_data.relics]
    res.material_list = [
        Material(
            tid=101,
            num=999999,
        ),
        Material(
            tid=102,
            num=9999999,
        ),
    ]


async def on_get_archive_data_cs_req(
    _session: "PlayerSession",
    _: GetArchiveDataCsReq,
    res: GetArchiveDataScRsp,
) -> None:
    res.archive_data = ArchiveData()


def build_sync(
    player: FreesrData,
    ret: PlayerSyncScNotify,
    avatar_ids: List[int],
    lightcone_indexes: List[int],
    relic_indexes: List[int],
) -> None:
    avatar_list = [
        av_proto
        for a in avatar_ids
        if (av_proto := player.get_avatar_proto(a)) is not None
    ]
    ret.avatar_sync = AvatarSync(avatar_list=avatar_list)
    ret.multi_path_avatar_info_list = [
        mp_proto
        for a in avatar_ids
        if (mp_proto := player.get_avatar_multipath_proto(a)) is not None
    ]
    ret.relic_list = [player.relics[idx].to_relic_proto() for idx in relic_indexes]
    ret.equipment_list = [
        player.lightcones[idx].to_equipment_proto() for idx in lightcone_indexes
    ]


def equip_relic(
    player: FreesrData,
    req: DressRelicAvatarCsReq,
) -> Optional[PlayerSyncScNotify]:
    ret = PlayerSyncScNotify()
    target_avatar = player.avatars.get(req.avatar_id)
    if not target_avatar:
        return None

    avatar_ids_to_sync = set()
    relic_index_to_sync = set()

    for param in req.switch_list:
        target_relic_idx = next(
            (
                i
                for i, v in enumerate(player.relics)
                if v.get_unique_id() == param.relic_unique_id
            ),
            None,
        )
        if target_relic_idx is None:
            continue

        cur_avatar_relic_idx = next(
            (
                i
                for i, r in enumerate(player.relics)
                if r.equip_avatar == target_avatar.avatar_id
                and r.get_slot() == param.relic_type
            ),
            None,
        )

        if cur_avatar_relic_idx is not None:
            avatar_ids_to_sync.add(player.relics[cur_avatar_relic_idx].equip_avatar)
            player.relics[cur_avatar_relic_idx].equip_avatar = player.relics[
                target_relic_idx
            ].equip_avatar
            relic_index_to_sync.add(cur_avatar_relic_idx)

        avatar_ids_to_sync.add(player.relics[target_relic_idx].equip_avatar)

        player.relics[target_relic_idx].equip_avatar = target_avatar.avatar_id

        avatar_ids_to_sync.add(player.relics[target_relic_idx].equip_avatar)
        relic_index_to_sync.add(target_relic_idx)

    build_sync(player, ret, list(avatar_ids_to_sync), [], list(relic_index_to_sync))
    return ret


async def on_dress_relic_avatar_cs_req(
    session: "PlayerSession",
    req: DressRelicAvatarCsReq,
    _: DressRelicAvatarScRsp,
) -> None:
    if pkt := equip_relic(session.json_data, req):
        session.send(cmd_id=CmdID.PlayerSyncScNotify, body=pkt)


def unequip_relic(
    player: FreesrData, req: TakeOffRelicCsReq
) -> Optional[PlayerSyncScNotify]:
    ret = PlayerSyncScNotify()
    target_avatar = player.avatars.get(req.avatar_id)
    if not target_avatar:
        return None

    relic_index_to_sync = set()

    for relic_type in req.relic_type_list:
        relics = [
            i
            for i, r in enumerate(player.relics)
            if r.equip_avatar == target_avatar.avatar_id and r.get_slot() == relic_type
        ]

        for idx in relics:
            player.relics[idx].equip_avatar = 0

        relic_index_to_sync.update(relics)

    build_sync(player, ret, [req.avatar_id], [], list(relic_index_to_sync))
    return ret


async def on_take_off_relic_cs_req(
    session: "PlayerSession",
    req: TakeOffRelicCsReq,
    _: TakeOffRelicScRsp,
) -> None:
    if pkt := unequip_relic(session.json_data, req):
        session.send(cmd_id=CmdID.PlayerSyncScNotify, body=pkt)


def set_lightcone_equipper(
    player: FreesrData, target_avatar_id: int, target_lightcone_uid: int
) -> Optional[PlayerSyncScNotify]:
    ret = PlayerSyncScNotify()
    target_avatar = player.avatars.get(target_avatar_id)
    if not target_avatar:
        return None

    cur_avatar_lc_idx = next(
        (
            i
            for i, lc in enumerate(player.lightcones)
            if lc.equip_avatar == target_avatar.avatar_id
        ),
        None,
    )

    if target_lightcone_uid == 0 and cur_avatar_lc_idx is not None:
        player.lightcones[cur_avatar_lc_idx].equip_avatar = 0

        build_sync(
            player,
            ret,
            [target_avatar.avatar_id],
            [cur_avatar_lc_idx],
            [],
        )

        return ret

    target_lightcone_idx = next(
        (
            i
            for i, lc in enumerate(player.lightcones)
            if lc.get_unique_id() == target_lightcone_uid
        ),
        None,
    )

    if target_lightcone_idx is None:
        return None

    if cur_avatar_lc_idx is not None:
        player.lightcones[cur_avatar_lc_idx].equip_avatar = player.lightcones[
            target_lightcone_idx
        ].equip_avatar

    avatars_sync = [
        player.lightcones[target_lightcone_idx].equip_avatar,
        target_avatar.avatar_id,
    ]

    player.lightcones[target_lightcone_idx].equip_avatar = target_avatar.avatar_id

    lightcone_indices = [
        i for i in [target_lightcone_idx, cur_avatar_lc_idx] if i is not None
    ]

    build_sync(
        player,
        ret,
        avatars_sync,
        lightcone_indices,
        [],
    )

    return ret


async def on_dress_avatar_cs_req(
    session: "PlayerSession",
    req: DressAvatarCsReq,
    _: DressAvatarScRsp,
) -> None:
    if pkt := set_lightcone_equipper(
        session.json_data, req.avatar_id, req.equipment_unique_id
    ):
        session.send(cmd_id=CmdID.PlayerSyncScNotify, body=pkt)


async def on_take_off_equipment_cs_req(
    session: "PlayerSession",
    req: TakeOffEquipmentCsReq,
    _: TakeOffEquipmentScRsp,
) -> None:
    if pkt := set_lightcone_equipper(session.json_data, req.avatar_id, 0):
        session.send(cmd_id=CmdID.PlayerSyncScNotify, body=pkt)


async def on_get_big_data_all_recommend_cs_req(
    session: "PlayerSession",
    req: GetBigDataAllRecommendCsReq,
    res: GetBigDataAllRecommendScRsp,
) -> None:
    res.big_data_recommend_type = req.big_data_recommend_type

    if (
        res.big_data_recommend_type
        == BigDataRecommendType.BIG_DATA_RECOMMEND_TYPE_RELIC_AVATAR
    ):
        res.relic_avatar = BigDataRecommendRelicAvatar(
            recommend_avatar_info_list=[
                RecomendedAvatarInfo(
                    avatar_id_list=[],
                    recommend_avatar_id=avatar_id,
                    relic_set_id=0,
                )
                for avatar_id in UNLOCKED_AVATARS
            ]
        )

    elif (
        res.big_data_recommend_type
        == BigDataRecommendType.BIG_DATA_RECOMMEND_TYPE_AVATAR_RELIC
    ):
        res.avatar_relic = BigDataRecommendAvatarRelic(
            recomended_relic_info_list=[
                RecommendedRelicInfo(
                    avatar_id=id,
                )
                for id in UNLOCKED_AVATARS
            ]
        )


async def on_rank_up_avatar_cs_req(
    session: "PlayerSession",
    req: RankUpAvatarCsReq,
    _: RankUpAvatarScRsp,
) -> None:
    if avatar := session.json_data.avatars.get(req.avatar_id):
        session.json_data.avatars[avatar.avatar_id].rank = req.rank
        ret = PlayerSyncScNotify()

        build_sync(session.json_data, ret, [avatar.avatar_id], [], [])

        session.send(cmd_id=CmdID.PlayerSyncScNotify, body=ret)
