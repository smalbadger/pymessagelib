from pprint import pprint
from message import *

format = "[id:4x][ptr:8x][addr:11b][5b]"


msg_fmts = {
    "GET_ADDR": {
        "id": Nibbles(4, value="x14"),
        "length": Nibbles(4, value=lambda id: id),
        "ptr": Bytes(4),
        "addr": Bits(11),
        "pad": Bits(3, value="b000"),
        "crc": Bytes(2, value=lambda length: length),
    },
    "FILL_KEY": {
        "id": Nibbles(4, value="x0015"),
        "ptr": Bytes(3),
        "addr": Bits(2),
        "pad": Bits(4, value="b0000"),
        "crc": lambda ptr, addr, pad: EKMS32Bit(ptr, addr, pad),
    },
    "FILL_KEK": "FILL_KEY",
    "FILL_TSK": "FILL_KEY",
    "FILL_TEK": "FILL_KEY",
}


builder = MessageBuilder()
GET_ADDR = builder.build_message_class("GET_ADDR", msg_fmts["GET_ADDR"])

msg1 = GET_ADDR(ptr="x00000054", addr="b10001101001")
print(f'{msg1.id=}')
print(f'{msg1.length=}')
print(f'{msg1.ptr=}')
print(f'{msg1.addr=}')
print(f'{msg1.pad=}')
print(f'{msg1.crc=}')

msg2 = GET_ADDR(ptr="x00000050", addr="b00000000000")
print(f'{msg2.id=}')
print(f'{msg2.length=}')
print(f'{msg2.ptr=}')
print(f'{msg2.addr=}')
print(f'{msg2.pad=}')
print(f'{msg2.crc=}')

assert msg1.ptr != msg2.ptr
assert msg1.addr != msg2.addr













