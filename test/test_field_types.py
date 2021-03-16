import unittest
from pymessagelib import MessageBuilder, InvalidFieldDataException, CircularDependencyException
from msg_definitions import msg_fmts, register_defs, circular_dep


class TestFieldTypes(unittest.TestCase):
    def setUp(self):
        self.builder = MessageBuilder(definitions=msg_fmts)

    def testConstantFields(self):
        msg1 = self.builder.GET_ADDR(ptr="x00000054", addr="b10001101001")
        self.assertEqual(msg1.id, "x0014")
        self.assertEqual(msg1.pad, "b000")
        with self.assertRaises(AttributeError):
            msg1.id = "b1"

    def testWritableFields(self):
        msg1 = self.builder.GET_ADDR(ptr="x00000054", addr="b10001101001")
        with self.assertRaises(InvalidFieldDataException):
            msg1.ptr = "x1000000000000000000000000000000000000000"
        with self.assertRaises(InvalidFieldDataException):
            msg1.ptr.value = "x1000000000000000000000000000000000000000"

    def testAutoUpdateFields(self):
        msg1 = self.builder.GET_ADDR(ptr="x00000054", addr="b10001101001")
        self.assertEqual(msg1.length, "x0014")
        self.assertEqual(msg1.crc, "x0000")
        msg1.ptr = "x54000000"
        self.assertEqual(msg1.crc, "x5400")

        with self.assertRaises(CircularDependencyException):
            builder = MessageBuilder(circular_dep)

    def testNestedFields(self):
        WRITE_REGISTER_REQUEST = self.builder.WRITE_REGISTER_REQUEST
        builder = MessageBuilder(register_defs)
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        INPUTS = builder.build_message_class("INPUTS", register_defs["INPUTS"])

        def verify_msg_outputs(msg):
            self.assertEqual(msg.data.context, OUTPUTS)
            self.assertEqual(type(msg.data), OUTPUTS)
            self.assertEqual(msg.data.reset1, "b1")
            self.assertEqual(msg.data.reset2, "b0")
            self.assertEqual(msg.data.cautions, "x00")
            self.assertEqual(msg.data.unused, "x0")

        def verify_msg_inputs(msg):
            self.assertEqual(msg.data.context, INPUTS)
            self.assertEqual(type(msg.data), INPUTS)
            self.assertEqual(msg.data.service_req, "b1")
            self.assertEqual(msg.data.voltage_ready, "b0")
            self.assertEqual(msg.data.exit_code, "x0000")
            self.assertEqual(msg.data.last_command_mid, "x0")
            self.assertEqual(msg.data.unused, "x00")

        send_msg_1 = WRITE_REGISTER_REQUEST(addr="x60000001", data="x80000000")
        send_msg_1.data.context = OUTPUTS
        verify_msg_outputs(send_msg_1)
        send_msg_1.data.context = INPUTS
        verify_msg_inputs(send_msg_1)

        send_msg_2 = WRITE_REGISTER_REQUEST(addr="x60000001", data=OUTPUTS(reset1="b1", reset2="b0", cautions="x00"))
        verify_msg_outputs(send_msg_2)
        send_msg_2.data.context = INPUTS
        verify_msg_inputs(send_msg_2)
