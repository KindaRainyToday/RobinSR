from proto import *


async def on_get_gacha_info_cs_req(
    _session: "PlayerSession", _req: GetGachaInfoCsReq, res: GetGachaInfoScRsp
) -> None:
    res.gacha_info_list = [
        GachaInfo(
            end_time=1924992000,
            begin_time=0,
            gacha_ceiling=GachaCeiling(),
            prize_item_list=[23002, 1003, 1101, 1104, 23000, 23003],
            item_detail_list=[
                1001,
                1002,
                1008,
                1009,
                1013,
                1103,
                1105,
                1106,
                1108,
                1109,
                1110,
                1111,
                1201,
                1202,
                1206,
                1207,
                1210,
                1003,
                1004,
                1101,
                1107,
                1104,
                1209,
                1211,
                21000,
                21001,
                21002,
                21003,
                21004,
                21005,
                21006,
                21007,
                21008,
                21009,
                21010,
                21011,
                21012,
                21013,
                21014,
                21015,
                21016,
                21017,
                21018,
                21019,
                21020,
                23000,
                23002,
                23003,
                23004,
                23005,
                23012,
                23013,
            ],
            gacha_id=1001,
        )
    ]


async def on_do_gacha_cs_req(
    _session: "PlayerSession", req: DoGachaCsReq, res: DoGachaScRsp
) -> None:
    res.gacha_id = req.gacha_id
    res.gacha_num = req.gacha_num

    res.gacha_item_list = [
        GachaItem(
            is_new=False,
            gacha_item=Item(
                item_id=1310 if i % 2 == 0 else 1314,
            ),
            token_item=ItemList(
                item_list_=[
                    Item(
                        item_id=251,
                        num=100,
                    )
                ]
            ),
            transfer_item_list=ItemList(),
        )
        for i in range(req.gacha_num)
    ]
