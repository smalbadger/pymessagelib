import unittest
import copy
from pymessagelib import (
    Field,
    MessageBuilder,
    InvalidFieldDataException,
    CircularDependencyException,
    ConflictingContextsException,
)
from msg_definitions import msg_fmts, register_defs, caution_codes, circular_dep


def remove_whitespace(s):
    return s.replace(" ", "").replace("\t", "").replace("\n", "")


class TestMessageTables(unittest.TestCase):
    def setUp(self):
        self.builder = MessageBuilder()
        self.builder.load_definitions(msg_fmts)
        self.builder.load_definitions(register_defs)
        self.builder.load_definitions(caution_codes)

        WRITE_REGISTER_REQUEST = self.builder.WRITE_REGISTER_REQUEST_V2
        OUTPUTS = self.builder.OUTPUTS
        RANDOM_MEANING = self.builder.RANDOM_MEANING
        CAUTION_CODES = self.builder.CAUTION_CODES

        self.msg = WRITE_REGISTER_REQUEST(addr="x60000001", data="x80000000")
        self.msg.or_field.context = RANDOM_MEANING
        self.msg.data.context = OUTPUTS
        self.msg.data.cautions.context = CAUTION_CODES

    def testExpandedTableRendering(self):
        nested_all_fmts = self.msg.render_table(
            formats=[Field.Format.Hex, Field.Format.Dec, Field.Format.Oct, Field.Format.Bin], expand_nested=True
        )
        self.assertEqual(
            remove_whitespace(nested_all_fmts),
            remove_whitespace(
                """
                    +WRITE_REGISTER_REQUEST_V2---------+-------------+--------------+-----------------------------------+
                    | Field Name           | Hex       | Dec         | Oct          | Bin                               |
                    +----------------------+-----------+-------------+--------------+-----------------------------------+
                    | mid                  | x0016     | d00022      | o000026      | b0000000000010110                 |
                    | or_field.byte_1      | xe0       | d224        | o340         | b11100000                         |
                    | or_field.byte_2      | x00       | d000        | o000         | b00000000                         |
                    | or_field.byte_3      | x00       | d000        | o000         | b00000000                         |
                    | or_field.byte_4      | x01       | d001        | o001         | b00000001                         |
                    | addr                 | x60000001 | d1610612737 | o14000000001 | b01100000000000000000000000000001 |
                    | data.reset1          | x1        | d1          | o1           | b1                                |
                    | data.reset2          | x0        | d0          | o0           | b0                                |
                    | data.cautions.addr   | x0        | d00         | o00          | b0000                             |
                    | data.cautions.access | x0        | d00         | o00          | b0000                             |
                    | data.unused          | x000000   | d0000000    | o00000000    | b0000000000000000000000           |
                    +----------------------+-----------+-------------+--------------+-----------------------------------+
                """
            ),
        )

    def testCollapsedTableRendering(self):
        not_nested_default_fmt = self.msg.render_table(formats=None, expand_nested=False)
        self.assertEqual(
            remove_whitespace(not_nested_default_fmt),
            remove_whitespace(
                """
                    +------------+-----------+
                    | Field Name | Value     |
                    +------------+-----------+
                    | mid        | x0016     |
                    | or_field   | xe0000001 |
                    | addr       | x60000001 |
                    | data       | x80000000 |
                    +------------+-----------+
                """
            ),
        )

    def testCollapsedTableComparisonEqual(self):
        comp = self.msg.compare_tables(self.msg, expand_nested=False)[1]
        self.assertEqual(
            remove_whitespace(comp),
            remove_whitespace(
                """
                    +------------+-----------+      +------------+-----------+
                    | Field Name | Value     |      | Field Name | Value     |
                    +------------+-----------+      +------------+-----------+
                    | mid        | x0016     |  ==  | mid        | x0016     |
                    | or_field   | xe0000001 |  ==  | or_field   | xe0000001 |
                    | addr       | x60000001 |  ==  | addr       | x60000001 |
                    | data       | x80000000 |  ==  | data       | x80000000 |
                    +------------+-----------+      +------------+-----------+
                """
            ),
        )

    def testCollapsedTableComparisonNotEqual(self):
        msg2 = copy.deepcopy(self.msg)
        msg2.data = "x83000000"
        comp = self.msg.compare_tables(msg2, expand_nested=False)[1]
        self.assertEqual(
            remove_whitespace(comp),
            remove_whitespace(
                """
                    +------------+-----------+      +------------+-----------+
                    | Field Name | Value     |      | Field Name | Value     |
                    +------------+-----------+      +------------+-----------+
                    | mid        | x0016     |  ==  | mid        | x0016     |
                    | or_field   | xe0000001 |  !=  | or_field   | xe3000001 |
                    | addr       | x60000001 |  ==  | addr       | x60000001 |
                    | data       | x80000000 |  !=  | data       | x83000000 |
                    +------------+-----------+      +------------+-----------+
                """
            ),
        )

    def testExpandedTableComparisonEqual(self):
        comp = self.msg.compare_tables(self.msg, formats=None, expand_nested=True)[1]
        self.assertEqual(
            remove_whitespace(comp),
            remove_whitespace(
                """
                    +WRITE_REGISTER_REQUEST_V2---------+      +WRITE_REGISTER_REQUEST_V2---------+
                    | Field Name           | Value     |      | Field Name           | Value     |
                    +----------------------+-----------+      +----------------------+-----------+
                    | mid                  | x0016     |  ==  | mid                  | x0016     |
                    | or_field.byte_1      | xe0       |  ==  | or_field.byte_1      | xe0       |
                    | or_field.byte_2      | x00       |  ==  | or_field.byte_2      | x00       |
                    | or_field.byte_3      | x00       |  ==  | or_field.byte_3      | x00       |
                    | or_field.byte_4      | x01       |  ==  | or_field.byte_4      | x01       |
                    | addr                 | x60000001 |  ==  | addr                 | x60000001 |
                    | data.reset1          | b1        |  ==  | data.reset1          | b1        |
                    | data.reset2          | b0        |  ==  | data.reset2          | b0        |
                    | data.cautions.addr   | x0        |  ==  | data.cautions.addr   | x0        |
                    | data.cautions.access | x0        |  ==  | data.cautions.access | x0        |
                    | data.unused          | x000000   |  ==  | data.unused          | x000000   |
                    +----------------------+-----------+      +----------------------+-----------+
                """
            ),
        )

    def testExpandedTableComparisonNotEqual(self):
        msg2 = copy.deepcopy(self.msg)
        msg2.data = "x83000000"
        comp = self.msg.compare_tables(msg2, formats=None, expand_nested=True)[1]
        self.assertEqual(
            remove_whitespace(comp),
            remove_whitespace(
                """
                    +WRITE_REGISTER_REQUEST_V2---------+      +WRITE_REGISTER_REQUEST_V2---------+
                    | Field Name           | Value     |      | Field Name           | Value     |
                    +----------------------+-----------+      +----------------------+-----------+
                    | mid                  | x0016     |  ==  | mid                  | x0016     |
                    | or_field.byte_1      | xe0       |  !=  | or_field.byte_1      | xe3       |
                    | or_field.byte_2      | x00       |  ==  | or_field.byte_2      | x00       |
                    | or_field.byte_3      | x00       |  ==  | or_field.byte_3      | x00       |
                    | or_field.byte_4      | x01       |  ==  | or_field.byte_4      | x01       |
                    | addr                 | x60000001 |  ==  | addr                 | x60000001 |
                    | data.reset1          | b1        |  ==  | data.reset1          | b1        |
                    | data.reset2          | b0        |  ==  | data.reset2          | b0        |
                    | data.cautions.addr   | x0        |  ==  | data.cautions.addr   | x0        |
                    | data.cautions.access | x0        |  !=  | data.cautions.access | xc        |
                    | data.unused          | x000000   |  ==  | data.unused          | x000000   |
                    +----------------------+-----------+      +----------------------+-----------+
                """
            ),
        )

    def testExpandedTableComparisonConflictingContexts(self):
        msg2 = self.builder.WRITE_REGISTER_REQUEST(addr="x60000001", data="x80000000")
        msg2.data.context = self.builder.OUTPUTS

        with self.assertRaises(ConflictingContextsException):
            self.msg.compare_tables(msg2, formats=None, expand_nested=True)

        msg3 = self.builder.WRITE_REGISTER_REQUEST_V2(addr="x60000001", data="x80000000")
        msg3.data.context = self.builder.OUTPUTS

        with self.assertRaises(ConflictingContextsException):
            self.msg.compare_tables(msg3, formats=None, expand_nested=True)

    def testCollapsedTableComparisonConflictingContexts(self):
        msg2 = self.builder.WRITE_REGISTER_REQUEST(addr="x60000001", data="x80000000")
        msg2.data.context = self.builder.OUTPUTS

        with self.assertRaises(ConflictingContextsException):
            self.msg.compare_tables(msg2, formats=None, expand_nested=False)

        msg3 = self.builder.WRITE_REGISTER_REQUEST_V2(addr="x60000001", data="x80000000")
        msg3.data.context = self.builder.OUTPUTS

        comp = self.msg.compare_tables(msg3, formats=None, expand_nested=False)[1]
        self.assertEqual(
            remove_whitespace(comp),
            remove_whitespace(
                """
                    +------------+-----------+      +------------+-----------+
                    | Field Name | Value     |      | Field Name | Value     |
                    +------------+-----------+      +------------+-----------+
                    | mid        | x0016     |  ==  | mid        | x0016     |
                    | or_field   | xe0000001 |  ==  | or_field   | xe0000001 |
                    | addr       | x60000001 |  ==  | addr       | x60000001 |
                    | data       | x80000000 |  ==  | data       | x80000000 |
                    +------------+-----------+      +------------+-----------+
                """
            ),
        )

    def testCollapsedTableComparisonSharingContexts(self):
        msg2 = self.builder.WRITE_REGISTER_REQUEST_V2(addr="x60000001", data="x80000000")
        msg2.or_field.context = self.builder.RANDOM_MEANING

        comp = self.msg.compare_tables(msg2, formats=None, expand_nested=False)[1]
        self.assertEqual(
            remove_whitespace(comp),
            remove_whitespace(
                """
                    +------------+-----------+      +------------+-----------+
                    | Field Name | Value     |      | Field Name | Value     |
                    +------------+-----------+      +------------+-----------+
                    | mid        | x0016     |  ==  | mid        | x0016     |
                    | or_field   | xe0000001 |  ==  | or_field   | xe0000001 |
                    | addr       | x60000001 |  ==  | addr       | x60000001 |
                    | data       | x80000000 |  ==  | data       | x80000000 |
                    +------------+-----------+      +------------+-----------+
                """
            ),
        )

    @unittest.expectedFailure
    def testExpandedTableComparisonSharingContexts(self):
        msg2 = self.builder.WRITE_REGISTER_REQUEST_V2(addr="x60000001", data="x80000000")
        msg2.or_field.context = self.builder.RANDOM_MEANING

        comp = self.msg.compare_tables(msg2, formats=None, expand_nested=True)[1]
