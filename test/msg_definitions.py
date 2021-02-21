
from field import Nibbles, Bytes, Bits, Bit, Byte

msg_fmts = {
    "GET_ADDR": {
        "id": Nibbles(4, value="x14"),
        "length": Nibbles(4, value=lambda id: id),
        "ptr": Bytes(4),
        "addr": Bits(11),
        "pad": Bits(3, value="b000"),
        "crc": Bytes(2, value=lambda ptr: ptr[:5]),
    },
    "FILL_KEY": {
        "id": Nibbles(4, value="x0015"),
        "ptr": Bytes(3),
        "addr": Bits(2),
        "pad": Bits(4, value="b0000"),
        "crc": lambda ptr, addr, pad: EKMS32Bit(ptr, addr, pad),
    },
    "WRITE_REGISTER_REQUEST": {
        "mid": Nibbles(4, value="x0014"),
        "length": Bytes(2, value="x0008"),
        "addr": Bytes(4),
        "data": Bytes(4),
    },
    "WRITE_REGISTER_RESPONSE": {
        "mid": Nibbles(4, value="x1014"),
        "length": Bytes(2, value="x0001"),
        "success": Bytes(1),
    },
    "READ_REGISTER_REQUEST": {
        "mid": Nibbles(4, value="x0015"),
        "length": Bytes(2, value="x0004"),
        "addr": Bytes(4),
    },
    "READ_REGISTER_RESPONSE": {
        "mid": Nibbles(4, value="x0014"),
        "length": Bytes(2, value="x0008"),
        "addr": Bytes(4),
        "data": Bytes(4),
    },
}

register_defs = {
    "OUTPUTS": {"reset1": Bit(1), "reset2": Bit(1), "cautions": Byte(1), "unused": Bits(22, value="x0000000")},
    "INPUTS": {
        "service_req": Bit(1),
        "voltage_ready": Bit(1),
        "exit_code": Bytes(2),
        "last_command_mid": Bits(2),
        "unused": Byte(1, value="x0"),
    },
}
