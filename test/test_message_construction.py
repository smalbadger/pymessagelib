import unittest
from message_builder import MessageBuilder
from msg_definitions import msg_fmts, register_defs
from _exceptions import InvalidDataFormatException


class TestMessageConstruction(unittest.TestCase):
    def testConstructionFromData_Normal(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        outputs = OUTPUTS.from_data("b11100000000000000000000000000000")
        self.assertTrue(outputs.reset1 == "b1")
        self.assertTrue(outputs.reset2 == "b1")
        self.assertTrue(outputs.cautions == "x80")
        self.assertTrue(outputs.unused == "x0")
        
    def testConstructionFromData_InvalidData(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        with self.assertRaises(InvalidDataFormatException):
            OUTPUTS.from_data("b11100000000000000000000000000000111")
        
    def testAllMessageProductionMethods(self):
        builder = MessageBuilder(msg_fmts)
        
        data = "x001600089999999900000000"
        wrt_req_1 = builder.build_message(data)
        wrt_req_2 = builder.WRITE_REGISTER_REQUEST.from_data(data)
        wrt_req_3 = builder.WRITE_REGISTER_REQUEST(addr='x99999999', data='x00000000')
        
        self.assertTrue(type(wrt_req_1) == builder.WRITE_REGISTER_REQUEST)
        self.assertTrue(type(wrt_req_2) == builder.WRITE_REGISTER_REQUEST)
        self.assertTrue(type(wrt_req_3) == builder.WRITE_REGISTER_REQUEST)
        
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
