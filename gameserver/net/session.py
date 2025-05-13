from common.sr_tools import FreesrData
from asyncio import DatagramTransport
from kcp import Kcp
from gameserver.util import cur_timestamp_secs
from gameserver.net.packet import NetPacket, RSP_MAP
from gameserver.net.handlers.dummy import DUMMY_MAP
from typing import List, Tuple
from proto import CmdID, PlayerSyncScNotify, AvatarSync
from common.util import Logger
from dataclasses import dataclass
import betterproto


@dataclass
class PlayerSession:
    transport: DatagramTransport
    addr: Tuple[str, int]
    kcp: Kcp
    start_time: int
    should_drop: bool
    json_data: FreesrData
    next_scene_save: int

    @classmethod
    async def new(
        cls, transport: DatagramTransport, addr: Tuple[str, int], session_id: int
    ) -> "PlayerSession":
        dummy = cls(
            transport=transport,
            addr=addr,
            kcp=None,
            start_time=cur_timestamp_secs(),
            should_drop=False,
            json_data=await FreesrData.load(),
            next_scene_save=0,
        )
        dummy.kcp = Kcp(session_id, dummy.datagram_send_to)
        return dummy

    def datagram_send_to(self, data: bytes) -> None:
        self.transport.sendto(data, self.addr)

    def session_time(self) -> int:
        return cur_timestamp_secs() - self.start_time

    async def consume(self, buffer: bytes) -> None:
        self.kcp.input(buffer)
        self.kcp.update(self.session_time())
        self.kcp.flush()

        packets = []
        while data := self.kcp.recv():
            packets.append(NetPacket.from_bytes(data))

        for packet in packets:
            if packet.cmd_type == int(CmdID.PlayerLogoutCsReq):
                self.should_drop = True
                return
            else:
                await self.on_message(packet.cmd_type, packet.body)

        self.kcp.update(self.session_time())

    def send_raw(self, payload: NetPacket) -> None:
        self.kcp.send(payload.to_bytes())
        self.kcp.flush()
        self.kcp.update(self.session_time())

    def send(self, body: betterproto.Message, cmd_id: CmdID) -> None:
        buf = bytes(body)
        payload = NetPacket(cmd_type=int(cmd_id), head=b"", body=buf)
        self.send_raw(payload)

    def sync_player(self) -> None:
        self.send(
            cmd_id=CmdID.PlayerSyncScNotify,
            body=PlayerSyncScNotify(
                del_equipment_list=list(range(2000, 3501)),
                del_relic_list=list(range(1, 2001)),
            ),
        )

        self.send(
            cmd_id=CmdID.PlayerSyncScNotify,
            body=PlayerSyncScNotify(
                avatar_sync=AvatarSync(
                    avatar_list=[
                        a.to_avatar_proto(None, [])
                        for a in self.json_data.avatars.values()
                        if a
                    ],
                ),
                multi_path_avatar_info_list=self.json_data.get_multi_path_info(),
            ),
        )

        self.send(
            cmd_id=CmdID.PlayerSyncScNotify,
            body=PlayerSyncScNotify(
                relic_list=[r.to_relic_proto() for r in self.json_data.relics],
                equipment_list=[
                    l.to_equipment_proto() for l in self.json_data.lightcones
                ],
            ),
        )

        self.send(
            cmd_id=CmdID.PlayerSyncScNotify,
            body=PlayerSyncScNotify(
                avatar_sync=AvatarSync(
                    avatar_list=[
                        av_proto
                        for a in self.json_data.avatars.values()
                        if (av_proto := self.json_data.get_avatar_proto(a.avatar_id))
                        is not None
                    ]
                )
            ),
        )

    async def on_message(self, cmd_type: int, packet_body: bytes) -> None:
        cmd_enum: CmdID
        try:
            cmd_enum = CmdID(cmd_type)
        except:
            Logger.warn(f"received unknown cmd_id: {cmd_type}")
            return

        if rsp_cmd := DUMMY_MAP.get(cmd_enum):
            self.send_raw(NetPacket(cmd_type=int(rsp_cmd), head=b"", body=b""))
        elif rsp_dict := RSP_MAP.get(cmd_enum):
            req_msg = rsp_dict["req_msg"]().parse(packet_body)
            rsp_msg = rsp_dict["rsp_msg"]()
            rsp_cmd = rsp_dict["rsp_cmd"]
            await rsp_dict["handler"](self, req_msg, rsp_msg)
            self.send(body=rsp_msg, cmd_id=rsp_cmd)
        else:
            Logger.warn(f"unhandled cmd: {cmd_enum}")
