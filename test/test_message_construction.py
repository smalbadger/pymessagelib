import unittest
from message_builder import MessageBuilder
from msg_definitions import msg_fmts, register_defs


class TestMessageConstruction(unittest.TestCase):
    def testConstruction(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        outputs = OUTPUTS.from_data("b11100000000000000000000000000000")
        self.assertTrue(outputs.reset1 == "b1")
        self.assertTrue(outputs.reset2 == "b1")
        self.assertTrue(outputs.cautions == "x80")
        self.assertTrue(outputs.unused == "x0")
        self.assertEqual(outputs.reset1.name, "reset1")
        self.assertEqual(outputs.reset2.name, "reset2")
        self.assertEqual(outputs.cautions.name, "cautions")
        self.assertEqual(outputs.unused.name, "unused")