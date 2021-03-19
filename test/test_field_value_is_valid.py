import unittest
from pymessagelib import MessageBuilder, Field
from msg_definitions import msg_fmts, register_defs, circular_dep


class TestFieldValueIsValid(unittest.TestCase):
    def setUp(self):
        self.builder = MessageBuilder(definitions=msg_fmts)

    def testValidChars_Hex(self):
        self.assertEqual("".join(Field.get_valid_chars(Field.Format.Hex)), "0123456789abcdefABCDEF")

    def testValidChars_Dec(self):
        self.assertEqual("".join(Field.get_valid_chars(Field.Format.Dec)), "0123456789")

    def testValidChars_Oct(self):
        self.assertEqual("".join(Field.get_valid_chars(Field.Format.Oct)), "01234567")

    def testValidChars_Bin(self):
        self.assertEqual("".join(Field.get_valid_chars(Field.Format.Bin)), "01")

    def testNoFormatSpecifier(self):
        msg1 = self.builder.GET_ADDR(ptr="x00000054", addr="b10001101001")
        self.assertEqual(msg1.ptr.value_is_valid("00000054"), False)

    def testInvalidType(self):
        msg1 = self.builder.GET_ADDR(ptr="x00000054", addr="b10001101001")
        self.assertEqual(msg1.ptr.value_is_valid(False), False)

    def testInvalidValue(self):
        msg1 = self.builder.GET_ADDR(ptr="x00000054", addr="b10001101001")
        self.assertEqual(msg1.ptr.value_is_valid("xfjskjfjfj"), False)
