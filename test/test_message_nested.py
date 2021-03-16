import unittest
from field import Field
from pymessagelib import (
    MessageBuilder,
    InvalidFieldDataException,
    CircularDependencyException,
    ContextDataMismatchException,
)
from msg_definitions import msg_fmts, register_defs, caution_codes, circular_dep


class TestNestedMessages(unittest.TestCase):
    def setUp(self):
        self.builder = MessageBuilder()
        self.builder.load_definitions(msg_fmts)
        self.builder.load_definitions(register_defs)
        self.builder.load_definitions(caution_codes)

    def testMultipleLevelContexts(self):
        WRITE_REGISTER_REQUEST = self.builder.WRITE_REGISTER_REQUEST
        OUTPUTS = self.builder.OUTPUTS
        CAUTION_CODES = self.builder.CAUTION_CODES

        msg = WRITE_REGISTER_REQUEST(addr="x60000001", data="x80000000")
        msg.data.context = OUTPUTS
        msg.data.cautions.context = CAUTION_CODES

        self.assertEqual(msg.context, WRITE_REGISTER_REQUEST)
        self.assertEqual(type(msg), WRITE_REGISTER_REQUEST)
        self.assertEqual(msg.data.context, OUTPUTS)
        self.assertEqual(type(msg.data), OUTPUTS)
        self.assertEqual(msg.data.cautions.context, CAUTION_CODES)
        self.assertEqual(type(msg.data.cautions), CAUTION_CODES)

    def testMultipleLevelValues(self):
        WRITE_REGISTER_REQUEST = self.builder.WRITE_REGISTER_REQUEST
        OUTPUTS = self.builder.OUTPUTS
        CAUTION_CODES = self.builder.CAUTION_CODES

        msg = WRITE_REGISTER_REQUEST(addr="x60000001", data="x80000000")
        msg.data.context = OUTPUTS
        msg.data.cautions.context = CAUTION_CODES

        self.assertEqual(msg.mid, "x0016")
        self.assertEqual(msg.length, "x0008")
        self.assertEqual(msg.addr, "x60000001")
        self.assertEqual(msg.data, "x80000000")
        self.assertEqual(msg.data.reset1, "b1")
        self.assertEqual(msg.data.reset2, "b0")
        self.assertEqual(msg.data.cautions, "x00")
        self.assertEqual(msg.data.cautions.addr, "b0000")
        self.assertEqual(msg.data.cautions.access, "b0000")
        self.assertEqual(msg.data.unused, "x0000000")

    def testMultipleLevelValueUpdates(self):
        WRITE_REGISTER_REQUEST = self.builder.WRITE_REGISTER_REQUEST_V2
        OUTPUTS = self.builder.OUTPUTS
        RANDOM_MEANING = self.builder.RANDOM_MEANING
        CAUTION_CODES = self.builder.CAUTION_CODES

        msg = WRITE_REGISTER_REQUEST(addr="x60000001", data="x80000000")
        msg.or_field.context = RANDOM_MEANING
        msg.data.context = OUTPUTS
        msg.data.cautions.context = CAUTION_CODES

        self.assertEqual(msg.data, "x80000000")
        self.assertEqual(msg.or_field, "xE0000001")
        self.assertEqual(msg.or_field.byte_1, "xE0")
        self.assertEqual(msg.or_field.byte_2, "x00")
        self.assertEqual(msg.or_field.byte_3, "x00")
        self.assertEqual(msg.or_field.byte_4, "x01")
        msg.data.cautions.addr = "x1"
        msg.data.cautions.access = "xF"
        self.assertEqual(msg.data, "x87C00000")
        self.assertEqual(msg.or_field, "xE7C00001")
        self.assertEqual(msg.or_field.byte_1, "xE7")
        self.assertEqual(msg.or_field.byte_2, "xC0")
        self.assertEqual(msg.or_field.byte_3, "x00")
        self.assertEqual(msg.or_field.byte_4, "x01")

    def testSetFieldAsMessage(self):
        WRITE_REGISTER_REQUEST = self.builder.WRITE_REGISTER_REQUEST_V2

        msg = WRITE_REGISTER_REQUEST(addr="x60000001", data="x80000000")
        self.assertEqual(msg.data, "x80000000")
        msg.data = self.builder.OUTPUTS.from_data("x8C000000")
        self.assertEqual(msg.data.reset1, "b1")
        self.assertEqual(msg.data.reset2, "b0")
        self.assertEqual(msg.data.cautions, "x30")
        self.assertEqual(msg.data.unused, "x00000")
        self.assertEqual(msg.data, "x8C000000")

    def testSetContextAsNone(self):
        WRITE_REGISTER_REQUEST = self.builder.WRITE_REGISTER_REQUEST_V2

        msg = WRITE_REGISTER_REQUEST(addr="x60000001", data="x80000000")
        msg.data.context = self.builder.OUTPUTS
        self.assertTrue("data.reset1" in msg.get_field_name_mapping(expand_nested=True))
        msg.data.context = None
        self.assertTrue("data.reset1" not in msg.get_field_name_mapping(expand_nested=True))

    def testSetIncompatibleContext(self):
        WRITE_REGISTER_REQUEST = self.builder.WRITE_REGISTER_REQUEST_V2

        msg = WRITE_REGISTER_REQUEST(addr="x60000001", data="x80000001")
        with self.assertRaises(ContextDataMismatchException):
            msg.data.context = self.builder.OUTPUTS
