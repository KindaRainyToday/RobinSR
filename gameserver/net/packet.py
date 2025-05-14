from dataclasses import dataclass
from gameserver.net.handlers.authentication import *
from gameserver.net.handlers.avatar import *
from gameserver.net.handlers.battle import *
from gameserver.net.handlers.chat import *
from gameserver.net.handlers.inventory import *
from gameserver.net.handlers.lineup import *
from gameserver.net.handlers.mission import *
from gameserver.net.handlers.player import *
from gameserver.net.handlers.scene import *

from proto import *
import struct

HEAD_MAGIC = bytes([0x9D, 0x74, 0xC7, 0x14])
TAIL_MAGIC = bytes([0xD7, 0xA1, 0x52, 0xC8])
NET_OPERATION_SIZE = 20
NET_PACKET_OVERHEAD = 16


@dataclass
class NetOperation:
    head: int
    conv_id: int
    token: int
    data: int
    tail: int

    @staticmethod
    def from_bytes(value: bytes) -> "NetOperation":
        assert len(value) == NET_OPERATION_SIZE, (
            "Bytes len doesn't match NetOperation size"
        )
        head, conv_id, token, data, tail = struct.unpack(">IIIII", value)
        return NetOperation(head, conv_id, token, data, tail)

    def to_bytes(self) -> bytes:
        return struct.pack(
            ">IIIII", self.head, self.conv_id, self.token, self.data, self.tail
        )


@dataclass
class NetPacket:
    cmd_type: int
    head: bytes
    body: bytes

    @staticmethod
    def from_bytes(value: bytes) -> "NetPacket":
        assert len(value) >= NET_PACKET_OVERHEAD, "Bytes len isn't enough for NetPacket"

        head_magic = value[0:4]
        assert head_magic == HEAD_MAGIC, "Invalid head magic"

        cmd_type = struct.unpack_from(">H", value, 4)[0]
        head_length = struct.unpack_from(">H", value, 6)[0]
        body_length = struct.unpack_from(">I", value, 8)[0]
        assert len(value) == NET_PACKET_OVERHEAD + head_length + body_length, (
            "Calculated packet len doesn't match actual len"
        )

        head_start = 12
        head_end = head_start + head_length
        head = value[head_start:head_end]

        body_start = head_end
        body_end = body_start + body_length
        body = value[body_start:body_end]

        tail_magic = value[body_end : body_end + 4]
        assert tail_magic == TAIL_MAGIC, "Invalid tail magic"

        return NetPacket(cmd_type, head, body)

    def to_bytes(self) -> bytes:
        head_length = len(self.head)
        body_length = len(self.body)
        packet_len = NET_PACKET_OVERHEAD + head_length + body_length

        head_start = 12
        head_end = head_start + head_length

        body_start = head_end
        body_end = body_start + body_length

        out = bytearray(packet_len)

        out[0:4] = HEAD_MAGIC
        out[4:6] = struct.pack(">H", self.cmd_type)
        out[6:8] = struct.pack(">H", head_length)
        out[8:12] = struct.pack(">I", body_length)
        out[head_start:head_end] = self.head
        out[body_start:body_end] = self.body
        out[body_end : body_end + 4] = TAIL_MAGIC

        return bytes(out)


# this map only stores the class name
# its constructed only if it's `.get()`-ed
# see the session.on_message() implementation!

# auto-generated <3
RSP_MAP = {
    CmdID.PlayerGetTokenCsReq: {
        "req_msg": PlayerGetTokenCsReq,
        "rsp_msg": PlayerGetTokenScRsp,
        "rsp_cmd": CmdID.PlayerGetTokenScRsp,
        "handler": on_player_get_token_cs_req,
    },
    CmdID.PlayerLoginCsReq: {
        "req_msg": PlayerLoginCsReq,
        "rsp_msg": PlayerLoginScRsp,
        "rsp_cmd": CmdID.PlayerLoginScRsp,
        "handler": on_player_login_cs_req,
    },
    CmdID.GetMissionStatusCsReq: {
        "req_msg": GetMissionStatusCsReq,
        "rsp_msg": GetMissionStatusScRsp,
        "rsp_cmd": CmdID.GetMissionStatusScRsp,
        "handler": on_get_mission_status_cs_req,
    },
    CmdID.GetBasicInfoCsReq: {
        "req_msg": GetBasicInfoCsReq,
        "rsp_msg": GetBasicInfoScRsp,
        "rsp_cmd": CmdID.GetBasicInfoScRsp,
        "handler": on_get_basic_info_cs_req,
    },
    CmdID.GetMultiPathAvatarInfoCsReq: {
        "req_msg": GetMultiPathAvatarInfoCsReq,
        "rsp_msg": GetMultiPathAvatarInfoScRsp,
        "rsp_cmd": CmdID.GetMultiPathAvatarInfoScRsp,
        "handler": on_get_multi_path_avatar_info_cs_req,
    },
    CmdID.GetAvatarDataCsReq: {
        "req_msg": GetAvatarDataCsReq,
        "rsp_msg": GetAvatarDataScRsp,
        "rsp_cmd": CmdID.GetAvatarDataScRsp,
        "handler": on_get_avatar_data_cs_req,
    },
    CmdID.GetAllLineupDataCsReq: {
        "req_msg": GetAllLineupDataCsReq,
        "rsp_msg": GetAllLineupDataScRsp,
        "rsp_cmd": CmdID.GetAllLineupDataScRsp,
        "handler": on_get_all_lineup_data_cs_req,
    },
    CmdID.GetCurLineupDataCsReq: {
        "req_msg": GetCurLineupDataCsReq,
        "rsp_msg": GetCurLineupDataScRsp,
        "rsp_cmd": CmdID.GetCurLineupDataScRsp,
        "handler": on_get_cur_lineup_data_cs_req,
    },
    CmdID.GetCurSceneInfoCsReq: {
        "req_msg": GetCurSceneInfoCsReq,
        "rsp_msg": GetCurSceneInfoScRsp,
        "rsp_cmd": CmdID.GetCurSceneInfoScRsp,
        "handler": on_get_cur_scene_info_cs_req,
    },
    CmdID.PlayerHeartBeatCsReq: {
        "req_msg": PlayerHeartBeatCsReq,
        "rsp_msg": PlayerHeartBeatScRsp,
        "rsp_cmd": CmdID.PlayerHeartBeatScRsp,
        "handler": on_player_heart_beat_cs_req,
    },
    CmdID.SceneEntityMoveCsReq: {
        "req_msg": SceneEntityMoveCsReq,
        "rsp_msg": SceneEntityMoveScRsp,
        "rsp_cmd": CmdID.SceneEntityMoveScRsp,
        "handler": on_scene_entity_move_cs_req,
    },
    CmdID.GetBagCsReq: {
        "req_msg": GetBagCsReq,
        "rsp_msg": GetBagScRsp,
        "rsp_cmd": CmdID.GetBagScRsp,
        "handler": on_get_bag_cs_req,
    },
    CmdID.GetArchiveDataCsReq: {
        "req_msg": GetArchiveDataCsReq,
        "rsp_msg": GetArchiveDataScRsp,
        "rsp_cmd": CmdID.GetArchiveDataScRsp,
        "handler": on_get_archive_data_cs_req,
    },
    CmdID.DressAvatarCsReq: {
        "req_msg": DressAvatarCsReq,
        "rsp_msg": DressAvatarScRsp,
        "rsp_cmd": CmdID.DressAvatarScRsp,
        "handler": on_dress_avatar_cs_req,
    },
    CmdID.TakeOffEquipmentCsReq: {
        "req_msg": TakeOffEquipmentCsReq,
        "rsp_msg": TakeOffEquipmentScRsp,
        "rsp_cmd": CmdID.TakeOffEquipmentScRsp,
        "handler": on_take_off_equipment_cs_req,
    },
    CmdID.DressRelicAvatarCsReq: {
        "req_msg": DressRelicAvatarCsReq,
        "rsp_msg": DressRelicAvatarScRsp,
        "rsp_cmd": CmdID.DressRelicAvatarScRsp,
        "handler": on_dress_relic_avatar_cs_req,
    },
    CmdID.TakeOffRelicCsReq: {
        "req_msg": TakeOffRelicCsReq,
        "rsp_msg": TakeOffRelicScRsp,
        "rsp_cmd": CmdID.TakeOffRelicScRsp,
        "handler": on_take_off_relic_cs_req,
    },
    CmdID.RankUpAvatarCsReq: {
        "req_msg": RankUpAvatarCsReq,
        "rsp_msg": RankUpAvatarScRsp,
        "rsp_cmd": CmdID.RankUpAvatarScRsp,
        "handler": on_rank_up_avatar_cs_req,
    },
    CmdID.SendMsgCsReq: {
        "req_msg": SendMsgCsReq,
        "rsp_msg": SendMsgScRsp,
        "rsp_cmd": CmdID.SendMsgScRsp,
        "handler": on_send_msg_cs_req,
    },
    CmdID.GetPrivateChatHistoryCsReq: {
        "req_msg": GetPrivateChatHistoryCsReq,
        "rsp_msg": GetPrivateChatHistoryScRsp,
        "rsp_cmd": CmdID.GetPrivateChatHistoryScRsp,
        "handler": on_get_private_chat_history_cs_req,
    },
    CmdID.GetFriendListInfoCsReq: {
        "req_msg": GetFriendListInfoCsReq,
        "rsp_msg": GetFriendListInfoScRsp,
        "rsp_cmd": CmdID.GetFriendListInfoScRsp,
        "handler": on_get_friend_list_info_cs_req,
    },
    CmdID.GetFriendLoginInfoCsReq: {
        "req_msg": GetFriendLoginInfoCsReq,
        "rsp_msg": GetFriendLoginInfoScRsp,
        "rsp_cmd": CmdID.GetFriendLoginInfoScRsp,
        "handler": on_get_friend_login_info_cs_req,
    },
    CmdID.JoinLineupCsReq: {
        "req_msg": JoinLineupCsReq,
        "rsp_msg": JoinLineupScRsp,
        "rsp_cmd": CmdID.JoinLineupScRsp,
        "handler": on_join_lineup_cs_req,
    },
    CmdID.ChangeLineupLeaderCsReq: {
        "req_msg": ChangeLineupLeaderCsReq,
        "rsp_msg": ChangeLineupLeaderScRsp,
        "rsp_cmd": CmdID.ChangeLineupLeaderScRsp,
        "handler": on_change_lineup_leader_cs_req,
    },
    CmdID.ReplaceLineupCsReq: {
        "req_msg": ReplaceLineupCsReq,
        "rsp_msg": ReplaceLineupScRsp,
        "rsp_cmd": CmdID.ReplaceLineupScRsp,
        "handler": on_replace_lineup_cs_req,
    },
    CmdID.QuitLineupCsReq: {
        "req_msg": QuitLineupCsReq,
        "rsp_msg": QuitLineupScRsp,
        "rsp_cmd": CmdID.QuitLineupScRsp,
        "handler": on_quit_lineup_cs_req,
    },
    CmdID.StartCocoonStageCsReq: {
        "req_msg": StartCocoonStageCsReq,
        "rsp_msg": StartCocoonStageScRsp,
        "rsp_cmd": CmdID.StartCocoonStageScRsp,
        "handler": on_start_cocoon_stage_cs_req,
    },
    CmdID.PVEBattleResultCsReq: {
        "req_msg": PVEBattleResultCsReq,
        "rsp_msg": PVEBattleResultScRsp,
        "rsp_cmd": CmdID.PVEBattleResultScRsp,
        "handler": on_pve_battle_result_cs_req,
    },
    CmdID.SceneCastSkillCsReq: {
        "req_msg": SceneCastSkillCsReq,
        "rsp_msg": SceneCastSkillScRsp,
        "rsp_cmd": CmdID.SceneCastSkillScRsp,
        "handler": on_scene_cast_skill_cs_req,
    },
    CmdID.QuickStartCocoonStageCsReq: {
        "req_msg": QuickStartCocoonStageCsReq,
        "rsp_msg": QuickStartCocoonStageScRsp,
        "rsp_cmd": CmdID.QuickStartCocoonStageScRsp,
        "handler": on_quick_start_cocoon_stage_cs_req,
    },
    CmdID.GetEnteredSceneCsReq: {
        "req_msg": GetEnteredSceneCsReq,
        "rsp_msg": GetEnteredSceneScRsp,
        "rsp_cmd": CmdID.GetEnteredSceneScRsp,
        "handler": on_get_entered_scene_cs_req,
    },
    CmdID.GetSceneMapInfoCsReq: {
        "req_msg": GetSceneMapInfoCsReq,
        "rsp_msg": GetSceneMapInfoScRsp,
        "rsp_cmd": CmdID.GetSceneMapInfoScRsp,
        "handler": on_get_scene_map_info_cs_req,
    },
    CmdID.EnterSceneCsReq: {
        "req_msg": EnterSceneCsReq,
        "rsp_msg": EnterSceneScRsp,
        "rsp_cmd": CmdID.EnterSceneScRsp,
        "handler": on_enter_scene_cs_req,
    },
    CmdID.PlayerLoginFinishCsReq: {
        "req_msg": PlayerLoginFinishCsReq,
        "rsp_msg": PlayerLoginFinishScRsp,
        "rsp_cmd": CmdID.PlayerLoginFinishScRsp,
        "handler": on_player_login_finish_cs_req,
    },
    CmdID.GetBigDataAllRecommendCsReq: {
        "req_msg": GetBigDataAllRecommendCsReq,
        "rsp_msg": GetBigDataAllRecommendScRsp,
        "rsp_cmd": CmdID.GetBigDataAllRecommendScRsp,
        "handler": on_get_big_data_all_recommend_cs_req,
    },
}
