"""
This module contains the Field class which is what Messages are made of. It
also contains subclasses of Field.

Created on Feb 18, 2021

@author: smalb
"""

from abc import ABC
from enum import Enum
import math
import inspect

from _exceptions import (
    InvalidDataFormatException,
    ContextDataMismatchException,
    InvalidFieldDataException,
    InvalidFormatException,
)


class Field(ABC):
    """
    Messages are made up of Fields. The field class is essentially a container to store binary values in.

    There are 3 types of fields:
        - Constant: The value of the field will never change
        - Writable: The value of the field can be changed by simply setting it.
        - Auto-Update: The value of the field updates automatically. It can depend on other fields.

    The value of each field is stored internally as binary, but can be rendered in binary, octal, hexadecimal,
    or decimal.

    """

    class Format(Enum):
        """Defines the number of states in a character for each format."""

        Bin = 2
        Oct = 8
        Dec = 10
        Hex = 16

    def __init__(self, length=1, value=None, fmt=None, context=None):
        """Constructs a Field object"""

        if length <= 1 and type(self).__name__.endswith("s"):
            raise InvalidFormatException(f"Length for plural field type {type(self).__name__} must be greater than 1.")
        elif length != 1 and not type(self).__name__.endswith("s"):
            raise InvalidFormatException(f"Length for singular field type {type(self).__name__} must be 1.")

        self._name = ""
        self._parent_message = None
        self._context = context
        self._unit_length = length
        self._bit_length = length * type(self).bits_per_unit
        self._format = None
        self._value_function = None
        self._value = None
        self._access = {
            "Read": True,
            "Write": True if value is None else False,
            "Auto Update": inspect.isfunction(value),
        }

        # Determine the format the value will be rendered as
        if fmt:
            self._format = fmt
        elif value is not None and not inspect.isfunction(value):
            self._format = Field.get_format(value)
        else:
            self._format = Field.Format.Bin if "Bit" in type(self).__name__ else Field.Format.Hex

        # Determine if the value is a function or an actual value.
        if inspect.isfunction(value):
            self._value_function = value
        elif value is not None:
            assert self.value_is_valid(value)
            self._value = self.render(value=value, fmt=Field.Format.Bin, pad_to_length=self._bit_length)
            assert len(self._value) - 1 == self._bit_length

    def render(self, value=None, fmt=None, pad_to_length=0) -> str:
        """
        Renders the field in the format specified.
        """
        from message import Message

        if not value:
            value = self.value
        if not fmt:
            fmt = self._format
        pad_to_length = pad_to_length if pad_to_length > 0 else math.ceil(self._bit_length / math.log2(fmt.value))
        if isinstance(value, Message):
            return value.render(fmt=fmt, pad_to_length=pad_to_length)
        return Field.render_value(value=value, fmt=fmt, pad_to_length=pad_to_length)

    @staticmethod
    def render_value(*, value, fmt, pad_to_length, check_length=False):
        """
        Render any value in a different format
        """
        prefix, numeric_value = value[0], value[1:]
        if check_length and len(numeric_value) > pad_to_length:
            raise InvalidDataFormatException(f"{value} is longer than specified length of {pad_to_length}.")
        int_val = int(numeric_value, Field.bases()[prefix].value)
        fmt_str = f"0{pad_to_length}{Field.inverted_bases()[fmt]}"
        return Field.inverted_bases()[fmt] + format(int_val, fmt_str)

    def value_is_valid(self, value):
        """
        Determine if a value is valid in this field.
        """
        bin_value = self.render(value=value, fmt=Field.Format.Bin, pad_to_length=self._bit_length)[1:]
        if len(bin_value) == self._bit_length:
            return True
        return False

    def length_as_format(self, fmt):
        """Return the character length if rendered in the specific format."""
        return math.ceil(self._bit_length / math.log2(fmt.value))

    @property
    def name(self):
        """Returns the name of the field. If no name is stored, an empty string will be returned."""
        return self._name

    @property
    def value_updater(self):
        """Return the function to be used for auto-updating the field. None if not an auto-update field."""
        return self._value_function

    @property
    def is_readable(self):
        """Return True if the field is readable and False otherwise"""
        return self._access["Read"]

    @property
    def is_writable(self):
        """Return True if the field is writable and False otherwise"""
        return self._access["Write"]

    @property
    def is_auto_updated(self):
        """Return True if the field is auto-updatable and False otherwise"""
        return self._access["Auto Update"]

    @property
    def value(self):
        """Return the value of the field. If this is a nested field, a Message-subclass object will be returned."""
        if self.context:
            return self._nested_msg
        return self._value

    @value.setter
    def value(self, value):
        """
        Sets the value of the field. If it's a nested field, a Message can be the value.

        :raises: InvalidFieldDataException if the value is too big to fit in the field.
        """
        from message import Message

        is_msg = False
        if isinstance(value, Message):
            is_msg = True
            context = type(value)
            value = value.render()
        if self.value_is_valid(value):
            self._value = value
            if is_msg:
                self.context = context
            if self.context:
                self._nested_msg.update(value)
        else:
            raise InvalidFieldDataException(f"{value} is not a valid value for {self}")

    @property
    def context(self):
        """If this is a nested field, return the class of the inner Message."""
        return self._context

    @context.setter
    def context(self, context):
        """Sets the context of the field."""
        from message import Message

        assert Message in inspect.getmro(context) or context is None

        if context is None:
            self._context = None
            self._nested_msg = None
        else:
            try:
                msg = context.from_data(self._value)
            except InvalidDataFormatException:
                raise ContextDataMismatchException(
                    f"The data '{self._value}' is not compatible with context {context.__name__}"
                )
            else:
                self._context = context
                self._nested_msg = msg

    def __repr__(self):
        """If the field has a value, render it in its default format. Else, return a summary of empty field"""
        if self.value:
            return self.render()
        return f"<{type(self).__name__} Field, length={self._unit_length} ({len(self)} bits), value=undefined>"

    def __eq__(self, other):
        """Compares this field with another field or a rendered value."""
        if isinstance(other, Field):
            return self.__eq__(other._value)

        self_prefix, self_numeric_value = self._value[0], self._value[1:]
        self_int_val = int(self_numeric_value, Field.bases()[self_prefix].value)

        other_prefix, other_numeric_value = other[0], other[1:]
        other_int_val = int(other_numeric_value, Field.bases()[other_prefix].value)

        return self_int_val == other_int_val

    def __len__(self):
        """Return the number of bits in the field"""
        return self._bit_length

    #     def __lt__(self, other):
    #         pass
    #
    #     def __bytes__(self):
    #         pass
    #
    #     def __call__(self):
    #         pass
    #
    #     def __contains__(self):
    #         pass
    #
    #     def __getitem__(self):
    #         pass
    #
    #     def __setitem__(self, value):
    #         pass
    #
    #     def __add__(self, other):
    #         pass
    #
    #     def __sub__(self, other):
    #         pass
    #
    #     def __lshift__(self, amount):
    #         pass
    #
    #     def __rshift__(self, amount):
    #         pass
    #
    #     def __and__(self, other):
    #         pass
    #
    #     def __rand__(self, other):
    #         pass
    #
    #     def __xor__(self, other):
    #         pass
    #
    #     def __rxor__(self, other):
    #         pass
    #
    #     def __or__(self, other):
    #         pass
    #
    #     def __ror__(self, other):
    #         pass
    #
    #     def __int__(self):
    #         pass

    def __invert__(self):
        """Return a new field with a bit-inverted value"""
        bin_val = self.render(fmt=Field.Format.Bin)
        inv_bin_val = bin_val.replace("0", "_").replace("1", "0").replace("_", "0")
        inv_val = Field.render(value=inv_bin_val, fmt=self._format)
        newfield = type(self).__new__()
        newfield.__init__(self.length_as_format(self._format), value=inv_val, fmt=self._format)
        return newfield

    def __bool__(self):
        """Return True if the value of the field is non-zero"""
        val_minus_format = self._value[1:]
        return any((False if char == "0" else True for char in val_minus_format))

    ######################################################
    # Static Methods
    ######################################################

    @staticmethod
    def bases():
        """Returns a dictionary mapping value prefixes to associated formats."""
        return {
            "b": Field.Format.Bin,
            "o": Field.Format.Oct,
            "d": Field.Format.Dec,
            "x": Field.Format.Hex,
        }

    @staticmethod
    def inverted_bases():
        """Returns a dictionary mapping formats to associated value prefixes."""
        return {v: k for k, v in Field.bases().items()}

    @staticmethod
    def get_format(value):
        """Returns the format of a value"""
        return Field.bases()[value[0]]

    @staticmethod
    def pad_to_length(value, length):
        """Adds the appropriate number of zeros to a value to achieve a specific width."""
        prefix = value[0]
        numeric_value = value[1:]
        if len(numeric_value) <= length:
            padding = "0" * (length - len(numeric_value))
            return f"{prefix}{padding}{numeric_value}"
        raise InvalidDataFormatException("Value is already longer than padding length")


class Bit(Field):
    """1 Bit = 1 Bit"""

    bits_per_unit = 1


class Bits(Field):
    """1 Bit = 1 Bit"""

    bits_per_unit = 1


class Nibble(Field):
    """1 Nibble = 4 Bits"""

    bits_per_unit = 4


class Nibbles(Field):
    """1 Nibble = 4 Bits"""

    bits_per_unit = 4


class Byte(Field):
    """1 Byte = 8 Bits"""

    bits_per_unit = 8


class Bytes(Field):
    """1 Byte = 8 Bits"""

    bits_per_unit = 8


class Word(Field):
    """1 Word = 16 Bits"""

    bits_per_unit = 16


class Words(Field):
    """1 Word = 16 Bits"""

    bits_per_unit = 16


class DWord(Field):
    """1 D-Word = 32 Bits"""

    bits_per_unit = 32


class DWords(Field):
    """1 D-Word = 32 Bits"""

    bits_per_unit = 32


class QWord(Field):
    """1 Q-Word = 64 Bits"""

    bits_per_unit = 64


class QWords(Field):
    """1 Q-Word = 64 Bits"""

    bits_per_unit = 64
