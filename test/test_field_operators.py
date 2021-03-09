import unittest
from field import Field, Bit, Bits


class TestFieldOperators(unittest.TestCase):
    def testInvert(self):
        field = Bits(7, value='b0011011')
        self.assertEqual(~field, 'b1100100')

    def testBoolTrue(self):
        field = Bits(10, value='b0000000001')
        self.assertTrue(field)
        
    def testBoolFalse(self):
        field = Bits(10, value='b0000000000')
        self.assertFalse(field)
        
