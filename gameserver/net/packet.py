from dataclasses import dataclass
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
