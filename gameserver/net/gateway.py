from typing import Dict, Optional, Tuple
from asyncio import (
    DatagramTransport,
    DatagramProtocol,
    BaseProtocol,
    get_running_loop,
    Event,
    CancelledError,
    create_task,
    AbstractEventLoop,
)
import random

from common.util import Logger
from kcp import get_conv
from gameserver.net.packet import NetOperation, NET_OPERATION_SIZE
from gameserver.net.session import PlayerSession


class Gateway:
    transport: DatagramTransport
    protocol: DatagramProtocol
    id_counter: int = 0
    sessions: Dict[int, PlayerSession] = {}

    def next_conv_pair(self) -> Tuple[int, int]:
        self.id_counter += 1
        return self.id_counter, random.randint(0, 0xFFFFFFFF)

    # not doing anything with the token rn
    def drop_kcp_session(
        self,
        conv_id: int,
        existance_checked: Optional[bool] = None,
        _token: Optional[int] = None,
    ) -> None:
        if existance_checked == True or conv_id in self.sessions:
            del self.sessions[conv_id]
            Logger.info(f"Dropped session with conv_id={conv_id}")
        else:
            Logger.warn(f"Tried to drop unknown session conv_id={conv_id}")

    async def establish_kcp_session(self, data: int, addr: Tuple[str, int]) -> None:
        conv_id, token = self.next_conv_pair()
        session_id = (conv_id << 32) | token

        Logger.info(f"New KCP session from {addr}, conv_id={conv_id}, token={token}")

        session = await PlayerSession.new(self.transport, addr, session_id)
        self.sessions[conv_id] = session

        response = NetOperation(
            head=0x145, conv_id=conv_id, token=token, data=data, tail=0x14514545
        ).to_bytes()

        self.transport.sendto(response, addr)

    async def process_net_operation(
        self, op: NetOperation, addr: Tuple[str, int]
    ) -> None:
        if (op.head, op.tail) == (0xFF, 0xFFFFFFFF):
            await self.establish_kcp_session(op.data, addr)
        elif (op.head, op.tail) == (0x194, 0x19419494):
            self.drop_kcp_session(op.conv_id)
        else:
            Logger.warn(f"Unknown NetOperation magic: {op.head}-{op.tail}")

    async def process_kcp_payload(self, data: bytes, addr: Tuple[str, int]) -> None:
        conv_id = get_conv(data)
        session = self.sessions.get(conv_id)

        if session and session.should_drop:
            self.drop_kcp_session(conv_id, existance_checked=True)
        elif session:
            await session.consume(data)
        else:
            Logger.warn(f"Received data for unknown session conv_id={conv_id}")

    @classmethod
    async def new(cls, host: str, port: int) -> None:
        gateway = cls()

        class UDPProtocol(DatagramProtocol):
            transport: Optional[DatagramTransport]
            shutdown_event: Event
            loop: AbstractEventLoop

            def __init__(self, loop: AbstractEventLoop) -> None:
                self.transport = None
                self.shutdown_event = Event()
                self.loop = loop

            def connection_made(self, transport: BaseProtocol) -> None:
                if isinstance(transport, DatagramTransport):
                    self.transport = transport
                else:
                    Logger.warn(f"Unexpected transport type: {transport}")

            def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
                # we do this because datagram_received cannot be async
                self.loop.create_task(self.dispatch_received(data, addr))

            async def dispatch_received(
                self, data: bytes, addr: Tuple[str, int]
            ) -> None:
                packet_length = len(data)

                if packet_length == NET_OPERATION_SIZE:
                    await gateway.process_net_operation(
                        NetOperation.from_bytes(data), addr
                    )
                elif packet_length >= 28:
                    await gateway.process_kcp_payload(data, addr)
                else:
                    Logger.warn(f"Unknown handshake length: {packet_length}")

            def error_received(self, exc: Exception) -> None:
                Logger.error(exc)

            def connection_lost(self, exc: Optional[Exception]) -> None:
                if exc:
                    Logger.error(exc)
                else:
                    Logger.info("Finished.")

        loop = get_running_loop()
        gateway.protocol = UDPProtocol(loop)
        gateway.transport, _ = await loop.create_datagram_endpoint(
            lambda: gateway.protocol, local_addr=(host, port)
        )

        try:
            Logger.info(f"KCP gateway is listening on {host}:{port}")
            await gateway.protocol.shutdown_event.wait()
        except CancelledError:
            Logger.info("Shutting down KCP gateway.")
        except Exception as exc:
            Logger.error(exc)
        finally:
            gateway.transport.close()
