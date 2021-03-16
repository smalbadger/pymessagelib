import unittest
from pymessagelib import MessageBuilder
from msg_definitions import msg_fmts, register_defs


class TestMessageLength(unittest.TestCase):
    def testMessageClassLength(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        self.assertTrue(len(OUTPUTS) == 32)

    def testMessageObjectLength(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        outputs = OUTPUTS(reset1="b1", reset2="b0", cautions="x00")
        self.assertTrue(len(outputs.reset1) == 1)
        self.assertTrue(len(outputs.reset2) == 1)
        self.assertTrue(len(outputs.cautions) == 8)
        self.assertTrue(len(outputs.unused) == 22)
        self.assertTrue(OUTPUTS.bit_length == 32)
