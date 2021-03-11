import unittest
from field import Field, Bit, Bits, Byte, Bytes, Nibbles


class TestFieldOperators(unittest.TestCase):
    def testInvert(self):
        field = Bits(7, value="b0011011")
        self.assertEqual(~field, "b1100100")

    def testNeg(self):
        field = Bits(7, value="b0011011")
        self.assertEqual(-field, "b1100100")

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

    def testLessThanGreaterThan(self):
        f1 = Bits(10, value="b0000000000")
        f2 = Byte(value="xF0")
        f3 = Nibbles(3, value="x100")
        self.assertTrue(f3 > f1)
        self.assertTrue(f2 < f3)
        self.assertTrue(f1 < 1)
        self.assertTrue(f1 < "b1")
        self.assertTrue("b1" > f1)
        self.assertTrue("b0" < f2)
        self.assertTrue("b0" >= f1)
        self.assertTrue("b0" <= f1)

    def testAnd(self):
        f1 = Bytes(2, value="b000011000010")
        f2 = Bits(3, value="b100")
        f3 = f1 & f2
        self.assertEqual(f3, "b0")
        f4 = f2 & f1
        self.assertEqual(f4, "b0")
        f5 = f1 & f1
        self.assertEqual(f5, "b11000010")
        f6 = f2 & f2
        self.assertEqual(f6, "b100")
        self.assertEqual(f1 & Byte(value="x2"), "x2")
        self.assertEqual(f1 & "b10000010", "b10000010")
        self.assertEqual("b10000010" & f1, "b10000010")
        self.assertEqual(f1 & 2, "b10")
        self.assertEqual(2 & f1, "b10")

    def testOr(self):
        f1 = Bytes(2, value="b000011000010")
        f2 = Bits(3, value="b100")
        f3 = f1 | f2
        self.assertEqual(f3, "b000011000110")
        f4 = f2 | f1
        self.assertEqual(f4, "b000011000110")
        f5 = f1 | f1
        self.assertEqual(f5, "b000011000010")
        f6 = f2 | f2
        self.assertEqual(f6, "b100")
        self.assertEqual(f1 | "b10000011", "b11000011")
        self.assertEqual("b10000011" | f1, "b11000011")
        self.assertEqual(f1 | 15, "b11001111")
        self.assertEqual(15 | f1, "b11001111")

    def testXor(self):
        f1 = Bytes(2, value="b000011000010")
        f2 = Bits(3, value="b100")
        f3 = f1 ^ f2
        self.assertEqual(f3, "b000011000110")
        f4 = f2 ^ f1
        self.assertEqual(f4, "b000011000110")
        f5 = f1 ^ f1
        self.assertEqual(f5, "b000000000000")
        f6 = f2 ^ f2
        self.assertEqual(f6, "b000")
        self.assertEqual(f1 ^ "b10000011", "b01000001")
        self.assertEqual("b10000011" ^ f1, "b01000001")
        self.assertEqual(f1 ^ 15, "b11001101")
        self.assertEqual(15 ^ f1, "b11001101")

    def testContains(self):
        """
        Determine if a string or another field is contained in this field.
        If comparing with a string, the data format of the string will be used for the search.
        If comparing with another Field, a binary search will be performed.
        """
        f1 = Bytes(2, value="x1234")
        self.assertTrue("b10010" in f1)
        self.assertTrue("x8" not in f1)
        self.assertTrue("b1000" in f1)
        self.assertTrue("b11111" not in f1)
        self.assertTrue(Byte(value="x23") in f1)
        self.assertTrue(Byte(value="x8") not in f1)

    @unittest.expectedFailure
    def testGetItem(self):
        f1 = Bytes(2, value="x2345")

        # test getting single bits
        self.assertTrue(f1[0] == "b1")
        self.assertTrue(f1[1] == "b0")
        self.assertTrue(f1[2] == "b1")
        self.assertTrue(f1[3] == "b0")
        self.assertTrue(f1[4] == "b0")
        self.assertTrue(f1[5] == "b0")
        self.assertTrue(f1[6] == "b1")
        self.assertTrue(f1[7] == "b0")
        self.assertTrue(f1[8] == "b1")
        self.assertTrue(f1[9] == "b1")
        self.assertTrue(f1[10] == "b0")
        self.assertTrue(f1[11] == "b0")
        self.assertTrue(f1[12] == "b1")
        self.assertTrue(f1[13] == "b0")
        self.assertTrue(f1[14] == "b0")
        self.assertTrue(f1[15] == "b0")

        # test the bounds
        with self.assertRaises(IndexError):
            f1[-1]
        with self.assertRaises(IndexError):
            f1[16]

    @unittest.expectedFailure
    def testGetSlice(self):
        f1 = Bytes(2, value="x2345")

        self.assertTrue(f1[15:0] == "x2345")
        self.assertTrue(f1[15:8] == "x23")
        self.assertTrue(f1[7:0] == "x45")
        self.assertTrue(f1[0:0] == "b1")

        self.assertTrue(f1[0:15] == "xA2C4")
        self.assertTrue(f1[0:7] == "xA2")
        self.assertTrue(f1[8:15] == "xC4")

        with self.assertRaises(IndexError):
            f1[16:0]
        with self.assertRaises(IndexError):
            f1[15:-1]
        with self.assertRaises(IndexError):
            f1[16:-1]

    @unittest.expectedFailure
    def testSetItem(self):
        f1 = Bytes(2, value="x2345")

        f1[0] = "b0"
        self.assertTrue(f1 == "x2344")
        f1[15] = "b1"
        self.assertTrue(f1 == "x6344")

        with self.assertRaises(IndexError):
            f1[-1] = "b1"
        with self.assertRaises(IndexError):
            f1[16] = "b1"

        # TODO: Try setting a bit that can't be set (constant or auto-update field) and see error

    @unittest.expectedFailure
    def testSetSlice(self):
        f1 = Bytes(2, value="x2345")

        f1[15:8] = "x23"
        self.assertTrue(f1 == "x2323")
        f1[0:7] = "x21"
        self.assertTrue(f1 == "x2384")

        # TODO: Try setting a bit that can't be set (constant or auto-update field) and see error

    @unittest.expectedFailure
    def testAdd(self):
        f1 = Bytes(2, value="x0002")
        f2 = Bytes(2, value="x0010")
        self.assertTrue((f1 + "x10") == "x12")
        self.assertTrue((f1 + 16) == "x12")
        self.assertTrue((f1 + f2) == "x12")

    @unittest.expectedFailure
    def testSub(self):
        f1 = Bytes(2, value="x0002")
        f2 = Bytes(2, value="x0010")
        self.assertTrue((f2 - "x2") == "xE")
        self.assertTrue((f2 - 2) == "xE")
        self.assertTrue((f2 - f1) == "xE")

        # Test 2's complement
        self.assertTrue((f2 - "x1F") == "x1101")

    def testLeftShift(self):
        f1 = Bytes(2, value="x0002")
        self.assertTrue((f1 << 5) == "x0040")
        self.assertTrue((f1 << 32) == "x0000")

    def testRightShift(self):
        f1 = Bytes(2, value="x0002")
        self.assertTrue((f1 >> 1) == "x0001")
        self.assertTrue((f1 >> 2) == "x0000")
