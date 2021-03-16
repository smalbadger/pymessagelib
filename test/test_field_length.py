import unittest
from pymessagelib import Field, Bit, Bits


class TestFieldLength(unittest.TestCase):
    def testNonDWordAlignedField(self):
        field = Bits(7)
        self.assertTrue(field.length_as_format(Field.Format.Hex), 2)
        self.assertTrue(field.length_as_format(Field.Format.Dec), 1)
        self.assertTrue(field.length_as_format(Field.Format.Oct), 3)
        self.assertTrue(field.length_as_format(Field.Format.Bin), 7)

    def testDWordAlignedField(self):
        field = Bits(8)
        self.assertTrue(field.length_as_format(Field.Format.Hex), 2)
        self.assertTrue(field.length_as_format(Field.Format.Dec), 1)
        self.assertTrue(field.length_as_format(Field.Format.Oct), 3)
        self.assertTrue(field.length_as_format(Field.Format.Bin), 8)
