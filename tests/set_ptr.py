"""
Created on Jan 13, 2021

@author: smalbadger
"""


from message import Message
from test.test_xmlrpc import ADDR
from builtins import staticmethod


format = "[id:4x][ptr:8x][addr:11b][5b]"


class SET_PTR(Message):
    """
    Sets a pointer in the device (intentionally vague)
    """

    def __init__(self, id, ptr, addr, padding="00000"):
        """
        :param id: 4x
        :param ptr: 8x
        :param addr: 11b
        :param padding: 5b
        """
        self.id = id
        self.ptr = ptr
        self.addr = addr
        self.padding = padding

        self.form = ["id", "ptr", "addr", "padding"]

    def to_machine(self) -> str:
        id = format(int(self.id, 16), "016b")
        ptr = format(int(self.ptr, 16), "032b")
        addr = format(int(self.addr, 16), "011b")
        padding = self.padding

        all_bits = f"{id} {ptr} {addr} {padding}"
        all_hex = f'{int(all_bits.replace(" ", ""), 2):0x}'

        return all_hex

    @staticmethod
    def from_machine(machine_format):
        bits = format(int(machine_format, 16), "0b")
        print(bits)
        id = bits[0:16]
        ptr = bits[16:48]
        addr = bits[48:59]
        padding = bits[59:62]
        return SET_PTR(id, ptr, addr, padding)

    def to_human(self) -> str:

        longest_varname = len(max(self.form, key=len))

        result = ""
        for v in self.form:
            num_spaces = longest_varname - len(v)
            padded_v = " " * num_spaces + v
            result += (
                f"{padded_v} = {format(int(self.__getattribute__(v), 16), '0b')}\n"
            )
        return result


if __name__ == "__main__":
    msg = SET_PTR("0014", "01006000", "54", "00000")
    print(msg.to_machine())
    print("===================")
    print(msg.to_human())
    print("===================")
    print(SET_PTR.from_machine(msg.to_machine()).to_machine())
