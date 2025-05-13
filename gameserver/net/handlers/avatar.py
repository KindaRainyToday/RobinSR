from proto import *

UNLOCKED_AVATARS = [
    1002,
    1003,
    1004,
    1005,
    1006,
    1008,
    1009,
    1013,
    1101,
    1102,
    1103,
    1104,
    1105,
    1106,
    1107,
    1108,
    1109,
    1110,
    1111,
    1112,
    1201,
    1202,
    1203,
    1204,
    1205,
    1206,
    1207,
    1208,
    1209,
    1210,
    1211,
    1212,
    1213,
    1214,
    1215,
    1217,
    1301,
    1302,
    1303,
    1304,
    1305,
    1306,
    1307,
    1308,
    1309,
    1312,
    1315,
    1310,
    1314,
    1218,
    1221,
    1220,
    1222,
    1223,
    1317,
    1313,
    1225,
    1402,
    1401,
    1404,
    1403,
    1405,
    1407,
    1406,
    1409,
]


async def on_get_avatar_data_cs_req(
    session: "PlayerSession", body: GetAvatarDataCsReq, res: GetAvatarDataScRsp
) -> None:
    mc_and_march_ids = []
    if session.json_data._main_character.get_gender() == Gender.GenderMan:
        mc_and_march_ids = [8001, 8003, 8005, 8007, 1001, 1224]
    else:
        mc_and_march_ids = [8002, 8004, 8006, 8008, 1001, 1224]

    all_ids = UNLOCKED_AVATARS
    all_ids.extend(mc_and_march_ids)

    res.is_get_all = body.is_get_all
    res.avatar_list = [
        av_proto
        if (av_proto := session.json_data.get_avatar_proto(id)) is not None
        else Avatar(
            base_avatar_id=id,
            level=80,
            promotion=6,
            rank=6,
            skilltree_list=[
                AvatarSkillTree(point_id=id * 1000 + m, level=1) for m in range(1, 5)
            ],
            first_met_timestamp=1712924677,
        )
        for id in all_ids
    ]
