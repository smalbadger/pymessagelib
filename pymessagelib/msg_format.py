"""
This module ....
"""
import numpy
import inspect
from enum import Enum
from dataclasses import dataclass

############
# Exceptions
############


class InvalidFieldException(Exception):
    pass


class InvalidFieldDataException(Exception):
    pass


class MissingFieldDataException(Exception):
    pass


class InvalidDataFormatException(Exception):
    pass


######################################################################
# Field Classes are dynamically created to avoid repeating similar code
######################################################################


class DataFormat(Enum):
    Bin = 2
    Oct = 8
    Dec = 10
    Hex = 16


bases = {
    "b": DataFormat.Bin,
    "o": DataFormat.Oct,
    "d": DataFormat.Dec,
    "x": DataFormat.Hex,
}

inv_bases = {v: k for k, v in bases.items()}


def convert_to(value, target_format=DataFormat.Hex, pad_to_length=0) -> str:
    """
    A valid value is the following:
        - int (python object)
        - binary string starting with '0b'
        - octal string starting with '0o'
        - decimal string starting with '0d'
        - hexadecimal string starting with '0x'
    """

    if type(value) is int:
        value = f"0d{str(value)}"

    prefix = value[0]
    if prefix not in bases:
        raise InvalidDataFormatException(f"{value} is not in a valid format")

    numeric_value = value[1:]
    int_val = int(numeric_value, bases[prefix].value)
    fmt_str = f'0{pad_to_length if pad_to_length else ""}{inv_bases[target_format]}'
    return inv_bases[target_format] + format(int_val, fmt_str)


def pad_to_length(value, length):
    prefix = value[0]
    numeric_value = value[1:]
    if len(numeric_value) <= length:
        padding = "0" * (length - len(numeric_value))
        return f"{prefix}{padding}{numeric_value}"
    else:
        raise Exception("Value is already longer than padding length")


def get_format(value):
    return bases[value[0]]


class Field:
    def __init__(self, length, value=None):
        self.bit_length = length * type(self).bits_per_unit

        if value is not None and not inspect.isfunction(value):
            original_format = get_format(value)
            value = pad_to_length(value, length)
            assert self.value_is_valid(value)
        self.value = value

    def value_is_valid(self, value):
        bin_value = convert_to(value, DataFormat.Bin, self.bit_length)[1:]
        if len(bin_value) == self.bit_length:
            return True
        return False


# classes of each of the following names (plus plural versions) will be created
units = {"Bit": 1, "Nibble": 4, "Byte": 8, "Word": 16, "DWord": 32, "QWord": 64}

plural_units = {}
for cls_name, num_bits in units.items():
    plural_units[f"{cls_name}s"] = num_bits

units.update(plural_units)
for cls_name, num_bits in units.items():
    vars()[cls_name] = type(cls_name, (Field,), {"bits_per_unit": num_bits})
