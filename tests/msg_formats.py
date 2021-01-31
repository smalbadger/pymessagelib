from pprint import pprint
from message import *

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
    "FILL_KEK": "FILL_KEY",
    "FILL_TSK": "FILL_KEY",
    "FILL_TEK": "FILL_KEY",
}


builder = MessageBuilder()
GET_ADDR = builder.build_message_class("GET_ADDR", msg_fmts["GET_ADDR"])

msg1 = GET_ADDR(ptr="x00000054", addr="b10001101001")
assert msg1.crc == 'x0000'
msg1.ptr = 'x15000000'
assert msg1.crc == 'x1500'

msg2 = GET_ADDR(ptr="x80000054", addr="b10000011001")
assert msg1.ptr != msg2.ptr
assert msg1.addr != msg2.addr

#msg2.render_table()

print(msg1.compare_tables(msg2))













