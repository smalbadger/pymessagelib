import unittest
from pymessagelib import MessageBuilder, InvalidDataFormatException
from msg_definitions import msg_fmts, register_defs


class TestMessageOperators(unittest.TestCase):
    def testRepr(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        outputs = OUTPUTS.from_data("b11100000000000000000000000000000")

        self.assertEqual("<OUTPUTS: xe0000000>", repr(outputs))
