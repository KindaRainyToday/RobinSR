from proto import *
from common.structs.avatar import MultiPathAvatar
from gameserver.util import cur_timestamp_ms
from typing import Optional, Tuple, List

SERVER_UID = 727
SERVER_HEAD_ICON = 201402
SERVER_CHAT_BUBBLE_ID = 220005
SERVER_CHAT_HISTORY = [
    "'reload' to reload freesr-data.json. entering battle will do this too :)"
    "'sync' to synchronize stats between json and in-game view",
    "'mc {mc_id}' mc_id can be set from 8001 to 8008",
    "'march {march_id}' march_id can be set 1001 or 1224",
    "available commands:",
    "visit srtools.pages.dev to configure the PS! (you configure relics, equipment, monsters from there)",
]


async def on_get_friend_login_info_cs_req(
    _session: "PlayerSession",
    _req: GetFriendLoginInfoCsReq,
    res: GetFriendLoginInfoScRsp,
) -> None:
    res.friend_uid_list = [SERVER_UID]


async def on_get_friend_list_info_cs_req(
    _session: "PlayerSession", _req: GetFriendListInfoCsReq, res: GetFriendListInfoScRsp
) -> None:
    res.friend_list = [
        FriendSimpleInfo(
            remark_name="RobinSR",
            player_info=PlayerSimpleInfo(
                uid=SERVER_UID,
                platform=PlatformType.PC,
                online_status=FriendOnlineStatus.FRIEND_ONLINE_STATUS_ONLINE,
                head_icon=SERVER_HEAD_ICON,
                chat_bubble_id=SERVER_CHAT_BUBBLE_ID,
                level=70,
                nickname="Server",
                signature="omg",
            ),
            is_marked=True,
        )
    ]


async def on_get_private_chat_history_cs_req(
    _session: "PlayerSession",
    req: GetPrivateChatHistoryCsReq,
    res: GetPrivateChatHistoryScRsp,
) -> None:
    cur_time = cur_timestamp_ms()
    res.chat_message_list = [
        ChatMessageData(
            message_type=MsgType.MSG_TYPE_CUSTOM_TEXT,
            create_time=cur_time,
            content=s,
            sender_id=SERVER_UID,
        )
        for s in SERVER_CHAT_HISTORY
    ]
    res.contact_side = req.contact_side
    res.target_side = SERVER_UID


def parse_command(command: str) -> Optional[Tuple[str, List[str]]]:
    if parts := command.strip().split():
        return parts[0], parts[1:]
    return None


async def on_send_msg_cs_req(
    session: "PlayerSession",
    body: SendMsgCsReq,
    _res: SendMsgScRsp,
) -> None:
    # fucking stupid that you can't use walrus on tuples
    parsed_cmd = parse_command(body.message_text)
    if parsed_cmd:
        cmd, args = parsed_cmd

        match cmd:
            # doing this because i dont want to make a file watcher
            # it will only reload if the file has been updated
            # entering battle also calls update()
            case "reload":
                await session.json_data.update()
                session.send(
                    cmd_id=CmdID.RevcMsgScNotify,
                    body=RevcMsgScNotify(
                        message_type=body.message_type,
                        message_text="Reloaded freesr-data.json",
                        extra_id=body.extra_id,
                        target_uid=SERVER_UID,
                        source_uid=25,
                        chat_type=body.chat_type,
                        hnbepabnbng=body.hnbepabnbng,
                    ),
                )
            case "sync":
                session.sync_player()
                session.send(
                    cmd_id=CmdID.RevcMsgScNotify,
                    body=RevcMsgScNotify(
                        message_type=body.message_type,
                        message_text="Inventory synced",
                        extra_id=body.extra_id,
                        target_uid=SERVER_UID,
                        source_uid=25,
                        chat_type=body.chat_type,
                        hnbepabnbng=body.hnbepabnbng,
                    ),
                )
            case "mc":
                mc = MultiPathAvatar.from_int(int(args[0]))
                if mc is MultiPathAvatar.Unk:
                    mc = session.json_data._main_character

                session.json_data._main_character = mc
                await session.json_data.save_persistent()

                session.send(
                    cmd_id=CmdID.AvatarPathChangedNotify,
                    body=AvatarPathChangedNotify(
                        base_avatar_id=8001,
                        cur_multi_path_avatar_type=mc.get_type(),
                    ),
                )

                session.sync_player()

                session.send(
                    cmd_id=CmdID.RevcMsgScNotify,
                    body=RevcMsgScNotify(
                        message_type=body.message_type,
                        message_text=f"Success changing mc to {mc}",
                        extra_id=body.extra_id,
                        target_uid=SERVER_UID,
                        source_uid=25,
                        chat_type=body.chat_type,
                        hnbepabnbng=body.hnbepabnbng,
                    ),
                )
            case "march":
                march_type = MultiPathAvatar.from_int(int(args[0]))
                if march_type is MultiPathAvatar.Unk:
                    march_type = session.json_data._march_type
                elif (
                    march_type is not MultiPathAvatar.MarchPreservation
                    or march_type is not MultiPathAvatar.MarchHunt
                ):
                    march_type = MarchHunt

                session.json_data._march_type = march_type
                await session.json_data.save_persistent()

                session.send(
                    cmd_id=CmdID.AvatarPathChangedNotify,
                    body=AvatarPathChangedNotify(
                        base_avatar_id=1001,
                        cur_multi_path_avatar_type=march_type.get_type(),
                    ),
                )

                session.send(
                    cmd_id=CmdID.RevcMsgScNotify,
                    body=RevcMsgScNotify(
                        message_type=body.message_type,
                        message_text=f"Success changing march to {march_type}",
                        extra_id=body.extra_id,
                        target_uid=SERVER_UID,
                        source_uid=25,
                        chat_type=body.chat_type,
                        hnbepabnbng=body.hnbepabnbng,
                    ),
                )
            case _:
                None
    else:
        session.send(
            cmd_id=CmdID.RevcMsgScNotify,
            body=RevcMsgScNotify(
                message_type=body.message_type,
                message_text="Invalid command usage",
                extra_id=body.extra_id,
                target_uid=SERVER_UID,
                source_uid=25,
                chat_type=body.chat_type,
                hnbepabnbng=body.hnbepabnbng,
            ),
        )
