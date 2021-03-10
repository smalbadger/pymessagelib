import unittest
from field import Field, Bit, Bits, Byte, Bytes, Nibbles


class TestFieldOperators(unittest.TestCase):
    def testInvert(self):
        field = Bits(7, value="b0011011")
        self.assertEqual(~field, "b1100100")

    def testBool_True(self):
        field = Bits(10, value="b0000000001")
        self.assertTrue(field)

    def testBool_False(self):
        field = Bits(10, value="b0000000000")
        self.assertFalse(field)
        
    def testInt(self):
        field = Bits(10, value="b0000000000")
        self.assertTrue(int(field) == 0)
        field = Byte(value="x0F")
        self.assertTrue(int(field) == 15)
        field = Bytes(10, value="o12")
        self.assertTrue(int(field) == 10)
        
    def testLessThan(self):
        f1 = Bits(10, value="b0000000000")
        f2 = Byte(value="xF0")
        f3 = Nibbles(3, value='x100')
        self.assertTrue(f3>f1)
        self.assertTrue(f2<f3)
        self.assertTrue(f1<1)
        
    def testAnd(self):
        f1 = Bytes(2, value="b000011000010")
        f2 = Bits(3, value="b100")
        f3 = f1 & f2
        self.assertEqual(f3, 'b0')
        f4 = f2 & f1
        self.assertEqual(f4, 'b0')
        f5 = f1 & f1
        self.assertEqual(f5, 'b11000010')
        f6 = f2 & f2
        self.assertEqual(f6, 'b100')
        self.assertEqual(f1 & Byte(value='x2'), 'x2')
        
        
