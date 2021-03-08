import unittest
from message_builder import MessageBuilder
from msg_definitions import msg_fmts, register_defs


class TestMessageComparison(unittest.TestCase):
    def setUp(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        self.outputs_1 = OUTPUTS.from_data("b11100000000000000000000000000000")
        self.outputs_2 = OUTPUTS.from_data("b11101000000000000000000000000000")

    def testEqual(self):
        self.assertTrue(self.outputs_1 == self.outputs_1)

    def testNotEqual(self):
        self.assertTrue(self.outputs_1 != self.outputs_2)