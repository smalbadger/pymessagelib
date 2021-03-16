import unittest
from pymessagelib import MessageBuilder
from msg_definitions import msg_fmts, register_defs


class TestMessageFormats(unittest.TestCase):
    def testFormatFieldRepr(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])

        self.assertTrue("Byte" in repr(OUTPUTS.format["cautions"]))
