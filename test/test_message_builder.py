import unittest
from message_builder import MessageBuilder
from msg_definitions import msg_fmts, register_defs, invalid_def
from _exceptions import InvalidFieldException, MultipleMatchingMessageDefinitionsException


class TestMessageBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = MessageBuilder(msg_fmts)

    def testInstantiaion(self):
        pass  # instantiation is covered in the setup. Just want a simple pass here.

    def testDefinitionLoading(self):
        GET_ADDR = self.builder.GET_ADDR
        self.assertTrue(isinstance(GET_ADDR, type))

    def testInvalidDefinition(self):
        with self.assertRaises(InvalidFieldException):
            self.builder.build_message_class("INVALID_DEF", invalid_def["INVALID_DEF"])

    def testMessageProduction_Normal(self):
        wrt_req_1 = self.builder.build_message("x001600089999999900000000")

    def testMessageProduction_MultipleMatches(self):
        with self.assertRaises(MultipleMatchingMessageDefinitionsException):
            wrt_req_1 = self.builder.build_message("x00150004FFFFFFFF")
