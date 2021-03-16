import unittest
from pymessagelib import MessageBuilder
from msg_definitions import msg_fmts, register_defs


class TestFieldComparison(unittest.TestCase):
    def testFieldEquals(self):
        builder = MessageBuilder(definitions=msg_fmts)
        msg1 = builder.GET_ADDR(ptr="x00000054", addr="b10001101001")
        self.assertTrue(msg1.id != "x4")
        self.assertTrue(msg1.id == "x14")
        self.assertTrue(msg1.id == "x014")
        self.assertTrue(msg1.id == "x0014")
        self.assertTrue(msg1.id == "x00014")
        self.assertTrue(msg1.id != "b0100")
        self.assertTrue(msg1.id == "b10100")
        self.assertTrue(msg1.id == "b010100")
        self.assertTrue(msg1.id != "o4")
        self.assertTrue(msg1.id == "o24")
        self.assertTrue(msg1.id == "o024")
        self.assertTrue(msg1.id == "o0024")
        self.assertTrue(msg1.id == "o00024")
        self.assertTrue(msg1.id != "d0")
        self.assertTrue(msg1.id == "d20")
        self.assertTrue(msg1.id == "d020")
        self.assertTrue(msg1.id == "d0020")
        self.assertTrue(msg1.id == "d00020")
