from common.sr_tools import FreesrData
from asyncio import DatagramTransport
from kcp import Kcp
from gameserver.util import cur_timestamp_secs
from gameserver.net.packet import NetPacket
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

    async def send(self, body: betterproto.Message, cmd_id: CmdID) -> None:
        buf = bytes(body)
        payload = NetPacket(cmd_type=int(CmdID), head=b"", body=buf).to_bytes()

        self.kcp.send(payload)
        self.kcp.flush()
        self.kcp.update(self.session_time())

    async def send_raw(self, payload: NetPacket) -> None:
        self.kcp.send(payload.to_bytes())
        self.kcp.flush()
        self.kcp.update(self.session_time())

    async def sync_player(self) -> None:
        json = self.json_data

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
                        a.to_avatar_proto(None, []) for a in json.avatars.values() if a
                    ],
                ),
                multi_path_avatar_info_list=json.get_multi_path_info(),
            ),
        )

        self.send(
            cmd_id=CmdID.PlayerSyncScNotify,
            body=PlayerSyncScNotify(
                relic_list=[r.to_relic_proto() for r in json.relics],
                equipment_list=[l.to_equipment_proto() for l in json.lightcones],
            ),
        )

        self.send(
            cmd_id=CmdID.PlayerSyncScNotify,
            body=PlayerSyncScNotify(
                avatar_sync=AvatarSync(
                    avatar_list=[
                        av_proto
                        for a in json.avatars.values()
                        if (av_proto := json.get_avatar_proto(a.avatar_id)) is not None
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

        match cmd_enum:
            case _:
                Logger.warn(f"Unhandled cmd_id: {cmd_type}")
