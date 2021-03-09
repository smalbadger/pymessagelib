from field import Field, Nibbles, Nibble, Bytes, Bits, Bit, Byte


def calcLength(*args):
    """Calculates the length over given fields"""
    bin_data = ""
    for arg in args:
        bin_data += arg.render(fmt=Field.Format.Bin, pad_to_length=len(arg) - 1)[1:]
    hex_str = f"{int(bin_data, 2):X}"
    length = len(hex_str) // 2
    length_in_hex = f"x{length:04X}"
    return length_in_hex


def calcOr(*args):
    """Calculates the length over given fields"""
    val = 0
    for arg in args:
        val |= int(arg.render(fmt=Field.Format.Bin, pad_to_length=len(arg) - 1)[1:], 2)
    return f"x{val:X}"


msg_fmts = {
    "GET_ADDR": {
        "id": Nibbles(4, value="x14"),
        "length": Nibbles(4, value=lambda id: id.render(fmt=Field.Format.Hex, pad_to_length=4)),
        "ptr": Bytes(4),
        "addr": Bits(11),
        "pad": Bits(3, value="b000"),
        "crc": Bytes(2, value=lambda ptr: ptr.render(fmt=Field.Format.Hex)[:5]),
    },
    "FILL_KEY": {
        "id": Nibbles(4, value="x0015"),
        "ptr": Bytes(3),
        "addr": Bits(2),
        "pad": Bits(4, value="b0000"),
        "crc": Bytes(4, value=lambda pad: pad.render()),
    },
    "WRITE_REGISTER_REQUEST": {
        "mid": Nibbles(4, value="x0016"),
        "length": Bytes(2, value=lambda addr, data: calcLength(addr, data)),
        "addr": Bytes(4),
        "data": Bytes(4),
    },
    "WRITE_REGISTER_REQUEST_V2": {
        "mid": Nibbles(4, value="x0016"),
        "or_field": Bytes(4, value=lambda addr, data: calcOr(addr, data)),
        "addr": Bytes(4),
        "data": Bytes(4),
    },
    "WRITE_REGISTER_RESPONSE": {
        "mid": Nibbles(4, value="x1014"),
        "length": Bytes(2, value="x0001"),
        "success": Byte(),
    },
    "READ_REGISTER_REQUEST": {
        "mid": Nibbles(4, value="x0015"),
        "length": Bytes(2, value="x0004"),
        "addr": Bytes(4),
    },
    "READ_REGISTER_RESPONSE": {
        "mid": Nibbles(4, value="x0014", fmt=Field.Format.Hex),
        "length": Bytes(2, value="x0008"),
        "addr": Bytes(4),
        "data": Bytes(4),
    },
}

register_defs = {
    "OUTPUTS": {"reset1": Bit(), "reset2": Bit(), "cautions": Byte(), "unused": Bits(22, value="x0000000")},
    "INPUTS": {
        "service_req": Bit(),
        "voltage_ready": Bit(),
        "exit_code": Bytes(2),
        "last_command_mid": Bits(2),
        "unused": Nibbles(3, value="x0"),
    },
    "RANDOM_MEANING": {
        "byte_1": Byte(),
        "byte_2": Byte(),
        "byte_3": Byte(),
        "byte_4": Byte(),
    },
}

caution_codes = {
    "CAUTION_CODES": {
        "addr": Nibble(),
        "access": Nibble(),
    }
}

circular_dep = {
    "CIRCULAR_DEP": {
        "id": Nibbles(4, value="x0015"),
        "len": Nibbles(2, value=lambda crc: crc),
        "ptr": Bytes(3),
        "addr": Bits(2),
        "pad": Bits(4, value="b0000"),
        "crc": Nibbles(2, value=lambda len: len),
    },
}
