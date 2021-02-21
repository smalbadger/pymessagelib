import unittest
from message_builder import MessageBuilder
from msg_definitions import msg_fmts, register_defs


class TestMessageBuilder(unittest.TestCase):
    def testInstantiaion(self):
        builder = MessageBuilder()

    @unittest.expectedFailure
    def testDefinitionLoading(self):
        builder = MessageBuilder()
        builder.load_definitions(msg_fmts)
        GET_ADDR = builder.GET_ADDR
        assert type(GET_ADDR) == type
