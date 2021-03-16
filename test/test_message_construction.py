import unittest
from msg_definitions import msg_fmts, register_defs, invalid_def
from pymessagelib import (
    MessageBuilder,
    InvalidDataFormatException,
    InvalidFieldException,
    MissingFieldDataException,
    InvalidFieldDataException,
)


class TestMessageConstruction(unittest.TestCase):
    def testConstructionFromData_Normal(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        outputs = OUTPUTS.from_data("b11100000000000000000000000000000")
        self.assertTrue(outputs.reset1 == "b1")
        self.assertTrue(outputs.reset2 == "b1")
        self.assertTrue(outputs.cautions == "x80")
        self.assertTrue(outputs.unused == "x0")

    def testConstructionFromData_Invalid(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        with self.assertRaises(InvalidDataFormatException):
            OUTPUTS.from_data("b11100000000000000000000000000000111")

    def testConstructionFromDefinition_MissingArg(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        with self.assertRaises(MissingFieldDataException):
            OUTPUTS(reset1="b1")

    def testConstructionFromDefinition_InvalidValue(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        with self.assertRaises(InvalidFieldDataException):
            OUTPUTS(reset1="b10", reset2="b0", cautions="x00")

    def testConstructionFromDefinition_InvalidField(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        with self.assertRaises(InvalidFieldException):
            OUTPUTS(reset1="b1", reset2="b0", cautions="x00", unknown="x000")

    def testConstructionFromDefinition_ReadOnlyField(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        with self.assertRaises(InvalidFieldException):
            OUTPUTS(reset1="b1", reset2="b0", cautions="x00", unused="x000")

    def testAllMessageProductionMethods(self):
        builder = MessageBuilder(msg_fmts)

        data = "x001600089999999900000000"
        wrt_req_1 = builder.build_message(data)
        wrt_req_2 = builder.WRITE_REGISTER_REQUEST.from_data(data)
        wrt_req_3 = builder.WRITE_REGISTER_REQUEST(addr="x99999999", data="x00000000")

        self.assertTrue(isinstance(wrt_req_1, builder.WRITE_REGISTER_REQUEST))
        self.assertTrue(isinstance(wrt_req_2, builder.WRITE_REGISTER_REQUEST))
        self.assertTrue(isinstance(wrt_req_3, builder.WRITE_REGISTER_REQUEST))

        self.assertEqual(wrt_req_1, wrt_req_2)
        self.assertEqual(wrt_req_2, wrt_req_3)
        self.assertEqual(wrt_req_3, wrt_req_1)

    def testInvalidMessageProduction(self):
        builder = MessageBuilder(msg_fmts)

        with self.assertRaises(InvalidDataFormatException):
            wrt_req_1 = builder.build_message("x0014000899999999000000001")

    def testMessageFieldNames(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        outputs = OUTPUTS.from_data("b11100000000000000000000000000000")
        self.assertEqual(outputs.reset1.name, "reset1")
        self.assertEqual(outputs.reset2.name, "reset2")
        self.assertEqual(outputs.cautions.name, "cautions")
        self.assertEqual(outputs.unused.name, "unused")
