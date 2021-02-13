"""
Created on Feb 8, 2021

@author: smalb
"""
import unittest
from message import MessageBuilder
from message import Nibbles, Bytes, Bits

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


class TestFields(unittest.TestCase):
    def testConstruction(self):
        builder = MessageBuilder()
        GET_ADDR = builder.build_message_class("GET_ADDR", msg_fmts["GET_ADDR"])

    def testFieldEquals(self):
        builder = MessageBuilder()
        GET_ADDR = builder.build_message_class("GET_ADDR", msg_fmts["GET_ADDR"])
        msg1 = GET_ADDR(ptr="x00000054", addr="b10001101001")
        assert msg1.id != "x4"
        assert msg1.id == "x14"
        assert msg1.id == "x014"
        assert msg1.id == "x0014"
        assert msg1.id == "x00014"
        assert msg1.id == "x000014"
        assert msg1.id != "b0100"
        assert msg1.id == "b10100"
        assert msg1.id == "b010100"
        assert msg1.id == "b0010100"
        assert msg1.id != "o4"
        assert msg1.id == "o24"
        assert msg1.id == "o024"
        assert msg1.id == "o0024"
        assert msg1.id == "o00024"
        assert msg1.id != "d0"
        assert msg1.id == "d20"
        assert msg1.id == "d020"
        assert msg1.id == "d0020"
        assert msg1.id == "d00020"

    def testConstantFields(self):
        builder = MessageBuilder()
        GET_ADDR = builder.build_message_class("GET_ADDR", msg_fmts["GET_ADDR"])
        msg1 = GET_ADDR(ptr="x00000054", addr="b10001101001")
        assert msg1.id == "x0014"
        assert msg1.pad == "b000"

    def testAutoUpdateFields(self):
        builder = MessageBuilder()
        GET_ADDR = builder.build_message_class("GET_ADDR", msg_fmts["GET_ADDR"])

        msg1 = GET_ADDR(ptr="x00000054", addr="b10001101001")
        assert msg1.length == "x0014"
        assert msg1.crc == "x0000"
        msg1.ptr = "x54000000"
        assert msg1.crc == "x5400"

    def testNestedFieldContext(self):
        assert True == False


if __name__ == "__main__":
    unittest.main()
