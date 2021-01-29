from pprint import pprint
from msg_format import *
from message_builder import MessageBuilder

format = "[id:4x][ptr:8x][addr:11b][5b]"

msg_fmts = {
    "GET_ADDR": {
        "id": Nibbles(4, value="x14"),
        "length": Nibbles(4, value=lambda ptr, addr, pad: ptr + addr + pad),
        "ptr": Bytes(4),
        "addr": Bits(11),
        "pad": Bits(3, value="b000"),
        "crc": Bytes(2, value=lambda ptr, addr, pad: EKMS32Bit(ptr, addr, pad)),
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

msg = GET_ADDR(ptr="x00000054", addr="b10001101001")
pprint(msg.id)
pprint(msg.length)
pprint(msg.ptr)
pprint(msg.addr)
pprint(msg.pad)
pprint(msg.crc)
