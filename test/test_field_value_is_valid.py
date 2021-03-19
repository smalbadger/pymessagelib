import unittest
from pymessagelib import MessageBuilder, InvalidFieldDataException, CircularDependencyException
from msg_definitions import msg_fmts, register_defs, circular_dep


class TestFieldValueIsValid(unittest.TestCase):
    def setUp(self):
        self.builder = MessageBuilder(definitions=msg_fmts)

    def testNoFormatSpecifier(self):
        msg1 = self.builder.GET_ADDR(ptr="x00000054", addr="b10001101001")
        self.assertEqual(msg1.ptr.value_is_valid("00000054"), False)

    def testInvalidType(self):
        msg1 = self.builder.GET_ADDR(ptr="x00000054", addr="b10001101001")
        self.assertEqual(msg1.ptr.value_is_valid(False), False)

    def testInvalidValue(self):
        msg1 = self.builder.GET_ADDR(ptr="x00000054", addr="b10001101001")
        self.assertEqual(msg1.ptr.value_is_valid("xfjskjfjfj"), False)
