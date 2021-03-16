import unittest
from pymessagelib import MessageBuilder
from msg_definitions import msg_fmts, register_defs, caution_codes


class TestMessageComparison(unittest.TestCase):
    def setUp(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        INPUTS = builder.build_message_class("INPUTS", register_defs["INPUTS"])
        self.outputs_1 = OUTPUTS.from_data("b11100000000000000000000000000000")
        self.outputs_1_copy = OUTPUTS.from_data("b11100000000000000000000000000000")
        self.outputs_2 = OUTPUTS.from_data("b11101000000000000000000000000000")
        self.inputs_1 = INPUTS.from_data("b11100000000000000000000000000000")

    def testSelfEqual(self):
        self.assertTrue(self.outputs_1 == self.outputs_1)
        self.assertTrue(self.outputs_1 == self.outputs_1.render())

    def testCopyOfSelfEqual(self):
        self.assertTrue(self.outputs_1 == self.outputs_1_copy)
        self.assertTrue(self.outputs_1 == self.outputs_1_copy.render())

    def testDifferentStructureSameDataEqual(self):
        self.builder = MessageBuilder()
        self.builder.load_definitions(msg_fmts)
        self.builder.load_definitions(register_defs)
        self.builder.load_definitions(caution_codes)

        WRITE_REGISTER_REQUEST = self.builder.WRITE_REGISTER_REQUEST_V2
        OUTPUTS = self.builder.OUTPUTS
        RANDOM_MEANING = self.builder.RANDOM_MEANING
        CAUTION_CODES = self.builder.CAUTION_CODES

        msg1 = WRITE_REGISTER_REQUEST(addr="x60000001", data="x80000000")
        msg1.or_field.context = RANDOM_MEANING
        msg1.data.context = OUTPUTS
        msg1.data.cautions.context = CAUTION_CODES

        msg2 = WRITE_REGISTER_REQUEST(addr="x60000001", data="x80000000")
        msg1.data.context = OUTPUTS

        self.assertEqual(msg1, msg2)
        self.assertEqual(msg1, msg2.render())

    def testDifferentMessageSameDataNotEqual(self):
        self.assertNotEqual(self.outputs_1, self.inputs_1)
        self.assertEqual(self.outputs_1, self.inputs_1.render())

    def testNotEqual(self):
        self.assertTrue(self.outputs_1 != self.outputs_2)
        self.assertTrue(self.outputs_1 != self.outputs_2.render())
