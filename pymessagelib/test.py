"""
Created on Feb 8, 2021

@author: smalb
"""
import unittest
from message_builder import MessageBuilder
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


class TestFields(unittest.TestCase):
    def testClassBuilder(self):
        builder = MessageBuilder()
        GET_ADDR = builder.build_message_class("GET_ADDR", msg_fmts["GET_ADDR"])
        
    def testMessageLength(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        outputs = OUTPUTS(reset1='b1', reset2='b0', cautions='x00')
        assert len(outputs.reset1) == 1
        assert len(outputs.reset2) == 1
        assert len(outputs.cautions) == 8
        assert len(outputs.unused) == 22
        assert OUTPUTS.bit_length == 32
        
    def testMessageConstruction(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        outputs = OUTPUTS.from_data('b11100000000000000000000000000000')
        assert outputs.reset1 == 'b1'
        assert outputs.reset2 == 'b1'
        assert outputs.cautions == 'x80'
        assert outputs.unused == 'x0'

    def testFieldEquals(self):
        builder = MessageBuilder()
        GET_ADDR = builder.build_message_class("GET_ADDR", msg_fmts["GET_ADDR"])
        msg1 = GET_ADDR(ptr="x00000054", addr="b10001101001")
        assert msg1.id != "x4"
        assert msg1.id == "x14"
        assert msg1.id == "x014"
        assert msg1.id == "x0014"
        assert msg1.id == "x00014"
        assert msg1.id != "b0100"
        assert msg1.id == "b10100"
        assert msg1.id == "b010100"
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
        builder = MessageBuilder()
        WRITE_REGISTER_REQUEST = builder.build_message_class(
            "WRITE_REGISTER_REQUEST", msg_fmts["WRITE_REGISTER_REQUEST"]
        )
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        INPUTS = builder.build_message_class("INPUTS", register_defs["INPUTS"])

        def verify_msg_outputs(msg):
            assert msg.data.context == OUTPUTS
            assert type(msg.data) == OUTPUTS
            assert msg.data.reset1 == "b1"
            assert msg.data.reset2 == "b0"
            assert msg.data.cautions == "x00"
            assert msg.data.unused == "x0"

        def verify_msg_inputs(msg):
            assert msg.data.context == INPUTS
            assert type(msg.data) == INPUTS
            assert msg.data.service_req == "b1"
            assert msg.data.voltage_ready == "b0"
            assert msg.data.exit_code == "x0000"
            assert msg.data.last_command_mid == "x0"
            assert msg.data.unused == "x00"

        send_msg_1 = WRITE_REGISTER_REQUEST(addr="x60000001", data="x80000000")
        send_msg_1.data.context = OUTPUTS
        verify_msg_outputs(send_msg_1)
        send_msg_1.data.context = INPUTS
        verify_msg_inputs(send_msg_1)

        send_msg_2 = WRITE_REGISTER_REQUEST(addr="x60000001", data=OUTPUTS(reset1="b1", reset2="b0", cautions="x00"))
        verify_msg_outputs(send_msg_2)
        send_msg_2.data.context = INPUTS
        verify_msg_inputs(send_msg_2)


if __name__ == "__main__":
    unittest.main()
