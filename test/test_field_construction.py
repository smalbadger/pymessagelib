import unittest
from message_builder import MessageBuilder
from msg_definitions import msg_fmts, register_defs
from field import Bit, Bits
from _exceptions import InvalidFormatException


class TestFieldConstruction(unittest.TestCase):
    def testSingularField(self):
        field = Bit()
        with self.assertRaises(InvalidFormatException):
            field = Bit(length=2)

    def testPluralField(self):
        field = Bits(length=2)
        with self.assertRaises(InvalidFormatException):
            field = Bits()
