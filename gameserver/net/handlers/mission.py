from proto import *


async def on_get_mission_status_cs_req(
    _session: "PlayerSession",
    body: GetMissionStatusCsReq,
    res: GetMissionStatusScRsp,
) -> None:
    res.finished_main_mission_id_list = body.main_mission_id_list
    res.sub_mission_status_list = [
        Mission(
            id=id,
            progress=1,
            status=MissionStatus.MISSION_FINISH,
        )
        for id in body.sub_mission_id_list
    ]
