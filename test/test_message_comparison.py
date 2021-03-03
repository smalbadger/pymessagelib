import unittest
from message_builder import MessageBuilder
from msg_definitions import msg_fmts, register_defs


class TestMessageComparison(unittest.TestCase):
    def setUp(self):
        builder = MessageBuilder()
        OUTPUTS = builder.build_message_class("OUTPUTS", register_defs["OUTPUTS"])
        self.outputs_1 = OUTPUTS.from_data("b11100000000000000000000000000000")
        self.outputs_2 = OUTPUTS.from_data("b11101000000000000000000000000000")
        
    def testEqual(self):
        self.assertTrue(self.outputs_1 == self.outputs_1)
        
    def testNotEqual(self):
        self.assertTrue(self.outputs_1 != self.outputs_2)
        
    def testTableComparison(self):
        result, table_comparison = self.outputs_1.compare_tables(self.outputs_2)
        compare_to = """
        +==========+=========+=========================+      +==========+=========+=========================+
        |  Field   |   Hex   |           Bin           |      |  Field   |   Hex   |           Bin           |
        +==========+=========+=========================+      +==========+=========+=========================+
        | reset1   | x1      | b1                      |  ==  | reset1   | x1      | b1                      |
        +----------+---------+-------------------------+      +----------+---------+-------------------------+
        | reset2   | x1      | b1                      |  ==  | reset2   | x1      | b1                      |
        +----------+---------+-------------------------+      +----------+---------+-------------------------+
        | cautions | x80     | b10000000               |  !=  | cautions | xa0     | b10100000               |
        +----------+---------+-------------------------+      +----------+---------+-------------------------+
        | unused   | x000000 | b0000000000000000000000 |  ==  | unused   | x000000 | b0000000000000000000000 |
        +----------+---------+-------------------------+      +----------+---------+-------------------------+
        """.strip().replace("\n        ", "\n")
        self.assertTrue(table_comparison.strip() == compare_to)
