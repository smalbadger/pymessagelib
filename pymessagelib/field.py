"""
This module contains the Field class which is what Messages are made of. It
also contains subclasses of Field.

Created on Feb 18, 2021

@author: smalb
"""

import copy
import math
import inspect
import operator
from abc import ABC
from enum import Enum

from pymessagelib._exceptions import (
    InvalidDataFormatException,
    ContextDataMismatchException,
    InvalidFieldDataException,
    InvalidFormatException,
)
from pickle import FALSE


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
        self._nested_msg = None
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
        elif isinstance(value, str) and value[0] not in Field.bases():
            raise InvalidDataFormatException(f"value of '{value}' is not correctly formatted.")
        elif value is not None and not inspect.isfunction(value):
            self._format = Field.get_format(value)
        else:
            self._format = Field.Format.Bin if "Bit" in type(self).__name__ else Field.Format.Hex

        # Determine if the value is a function or an actual value.
        if inspect.isfunction(value):
            self._value_function = value
        elif value is not None:
            if not self.value_is_valid(value):
                raise InvalidFieldDataException(f"The value {value} is not valid for field {self}")
            self._value = self.render(value=value, fmt=Field.Format.Bin, pad_to_length=self._bit_length)

    def render(self, value=None, fmt=None, pad_to_length=0) -> str:
        """
        Renders the field in the format specified.
        """
        from pymessagelib.message import Message

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
        This function cannot raise exceptions. It will always return True or False
        """
        from pymessagelib.message import Message

        try:
            if not any([isinstance(value, str), isinstance(value, Message)]):
                return False

            if isinstance(value, str):
                if value[0] not in Field.bases():
                    return False

                chars_left_over = value[1:]
                for char in Field.get_valid_chars(Field.get_format(value)):
                    chars_left_over = chars_left_over.replace(char, "")

                if chars_left_over:
                    return False

            bin_value = self.render(value=value, fmt=Field.Format.Bin, pad_to_length=self._bit_length)[1:]
            if len(bin_value) == self._bit_length:
                return True
            return False
        except:
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
        from pymessagelib.message import Message

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
            raise InvalidFieldDataException(f"{value} is not a valid value for this field")

    @property
    def context(self):
        """If this is a nested field, return the class of the inner Message."""
        return self._context

    @context.setter
    def context(self, context):
        """Sets the context of the field."""
        from pymessagelib.message import Message

        assert context is None or Message in inspect.getmro(context)

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

    def __len__(self):
        """Return the number of bits in the field"""
        return self._bit_length

    ########################################
    #  --  Conversion Special Methods  --  #
    ########################################

    def __int__(self):
        """Converts the field to an integer"""
        return int(self.render(fmt=Field.Format.Bin)[1:], 2)

    def __index__(self):
        """Converts the field to a hexadecimal string"""
        return int(self)

    def __format__(self, fmt):
        """Converts the field to a string. If fmt is not supported, the default representation is returned."""
        if fmt in Field.bases():
            return self.render(fmt=Field.bases()[fmt])
        return repr(self)

    ########################################
    #  --  Comparison Special Methods  --  #
    ########################################

    def __eq__(self, other):
        """Returns True if self equals other. False otherwise."""
        if isinstance(other, Field):
            return self == other.render()

        self_prefix, self_numeric_value = self._value[0], self._value[1:]
        self_int_val = int(self_numeric_value, Field.bases()[self_prefix].value)

        other_prefix, other_numeric_value = other[0], other[1:]
        other_int_val = int(other_numeric_value, Field.bases()[other_prefix].value)

        return self_int_val == other_int_val

    def __lt__(self, other):
        """Return True if self is less than other. False otherwise"""
        if isinstance(other, str):
            other_prefix, other_numeric_value = other[0], other[1:]
            return self < int(other_numeric_value, Field.bases()[other_prefix].value)

        if not isinstance(other, int):
            return self < int(other)

        return int(self) < other

    def __ne__(self, other):
        """Returns False if self equals other. True otherwise."""
        return not self == other

    def __gt__(self, other):
        """Return True if self is greater than other. False otherwise"""
        return not (self < other or self == other)

    def __ge__(self, other):
        """Return True if self is greater than or equal to other. False otherwise"""
        return self > other or self == other

    def __le__(self, other):
        """Return True if self is less than or equal to other. False otherwise"""
        return self < other or self == other

    #     def __bytes__(self):
    #         pass

    ###############################################
    #  --  Bitwise Operation Special Methods  --  #
    ###############################################

    #     def __bitwise_helper(self, other, operator):
    #         ops = {
    #             "&": operator.and_,
    #             "|": operator.or_,
    #             "^": operator.xor,
    #         }
    #         op = ops[operator]
    #
    #         if isinstance(other, str):
    #             other_prefix, other_numeric_value = other[0], other[1:]
    #             return self.__bitwise_helper(int(other_numeric_value, Field.get_format(other).value), operator)
    #
    #         elif not isinstance(other, int):
    #             return self.__bitwise_helper(int(other), operator)
    #
    #         val = format(op(int(self), other), 'b')
    #         fieldCls = Bit if len(val) == 1 else Bits
    #         return fieldCls(length=len(val), value=f"b{val}")

    def __and__(self, other):
        """Returns a new field of the same type 'and'ed with the other field"""
        if isinstance(other, str):
            other_prefix, other_numeric_value = other[0], other[1:]
            return self & int(other_numeric_value, Field.get_format(other).value)

        if not isinstance(other, int):
            return self & int(other)

        val = format(int(self) & other, "b")
        fieldCls = Bit if len(val) == 1 else Bits
        return fieldCls(length=len(val), value=f"b{val}")

    def __or__(self, other):
        """Returns a new field of the same type 'or'ed with the other field"""
        if isinstance(other, str):
            other_prefix, other_numeric_value = other[0], other[1:]
            return self | int(other_numeric_value, Field.get_format(other).value)

        if not isinstance(other, int):
            return self | int(other)

        val = format(int(self) | other, "b")
        fieldCls = Bit if len(val) == 1 else Bits
        return fieldCls(length=len(val), value=f"b{val}")

    def __xor__(self, other):
        """Returns a new field of the same type 'or'ed with the other field"""
        if isinstance(other, str):
            other_prefix, other_numeric_value = other[0], other[1:]
            return self ^ int(other_numeric_value, Field.get_format(other).value)

        if not isinstance(other, int):
            return self ^ int(other)

        val = format(int(self) ^ other, "b")
        fieldCls = Bit if len(val) == 1 else Bits
        return fieldCls(length=len(val), value=f"b{val}")

    __rand__ = __and__
    __rxor__ = __xor__
    __ror__ = __or__

    def __lshift__(self, amount):
        """Shift value to the left by some amount and return another Field object"""
        shifted_bin_val = format(int(self) << amount, "b")
        if len(shifted_bin_val) > len(self):
            shifted_bin_val = shifted_bin_val[-len(self) :]
        return type(self)(length=self._unit_length, value=f"b{shifted_bin_val}")

    def __rshift__(self, amount):
        """Shift value to the right by some amount and return another Field object"""
        shifted_bin_val = format(int(self) >> amount, "b")
        return type(self)(length=self._unit_length, value=f"b{shifted_bin_val}")

    def __invert__(self):
        """Return a new field with a bit-inverted value"""
        bin_val = self.render(fmt=Field.Format.Bin)
        inv_bin_val = bin_val.replace("0", "_").replace("1", "0").replace("_", "1")
        inv_val = Field.render_value(value=inv_bin_val, fmt=Field.Format.Bin, pad_to_length=len(self))
        newfield = type(self)(self.length_as_format(self._format), value=inv_val, fmt=self._format)
        return newfield

    def __neg__(self):
        """Same as __invert__"""
        return self.__invert__()

    def __contains__(self, search):
        """
        Determine if a field or value is contained this field.

        The search value must be a valid formatted string or another value.
        If the search value is a string, boundaries of the selected format will be enforced.
        If the search value is a field, the value will be rendered as a binary string and a bit-comaprison will be performed.
        """
        if isinstance(search, str):
            search_val = search[1:]
            search_in = self.render(fmt=Field.get_format(search))
            return search_val in search_in

        if isinstance(search, Field):
            return self.__contains__(search.render(fmt=Field.Format.Bin))

    def __bool__(self):
        """Return True if the value of the field is non-zero"""
        val_minus_format = self._value[1:]
        return any((False if char == "0" else True for char in val_minus_format))

    def __getitem__(self, subscript):
        """
        Retrieve a field object that contains a subset of data from this field.

        Slice Criteria:
        ---------------
        - Both start and stop must be specified and step must not be specified.
        - Both start and stop are inclusive unlike normal string/list slices where stop is exclusive.
        - If start is less than stop, the bit sequence will be reversed.
        - If start and stop are equal, a normal indexing operation is performed.

        Index Criteria:
        ---------------
        - Negative indecies are not supported
        - The index corresponds to the bit-position starting from the LSB (on the right)
        """
        if isinstance(subscript, slice):
            if subscript.step is not None:
                raise IndexError(f"Field slicing must not include a step value. Invalid step {subscript.step}")
            if subscript.start is None or subscript.stop is None:
                raise IndexError("Start and stop indexes of field slices must be specified.")

            max_ = max(subscript.start, subscript.stop)
            if max_ > len(self) - 1:
                raise IndexError(f"Index value {max_} exceeds the length of field.")
            min_ = min(subscript.start, subscript.stop)
            if min_ < 0:
                raise IndexError(f"Index value {min_} is less than zero.")

            if subscript.start == subscript.stop:
                return self.__getitem__(subscript.start)

            bin_val = format(self, "b")[1:][::-1][min_ : max_ + 1]
            if subscript.start == max_:
                bin_val = bin_val[::-1]

            return Bits(len(bin_val), value=f"b{bin_val}")

        if subscript < 0:
            raise IndexError("Negative indexing not supported in Field class")
        bin_val = format(self, "b")[1:][::-1]
        bit = bin_val[subscript]
        return Bit(value=f"b{bit}")

    def __setitem__(self, subscript, value):
        """
        Set specific bits in the field

        Raises an InvalidFieldDataException if the field is not writable
        Raises an InvalidDataFormatException if the number of bits does not match the start and stop indecies.

        Slice Criteria:
        ---------------
        - Both start and stop must be specified and step must not be specified.
        - Both start and stop are inclusive unlike normal string/list slices where stop is exclusive.
        - If start is less than stop, the bit sequence will be reversed.
        - If start and stop are equal, a normal indexing operation is performed.
        - The number of bits specified must equal the difference between start and stop plus one.

        Index Criteria:
        ---------------
        - Negative indices are not supported
        - The index corresponds to the bit-position starting from the LSB (on the right)
        """

        if not self.is_writable:
            raise InvalidFieldDataException(f"This field is not writable")

        if isinstance(subscript, slice):
            if subscript.step is not None:
                raise IndexError(f"Field slicing must not include a step value. Invalid step {subscript.step}")
            if subscript.start is None or subscript.stop is None:
                raise IndexError("Start and stop indexes of field slices must be specified.")

            max_ = max(subscript.start, subscript.stop)
            if max_ > len(self) - 1:
                raise IndexError(f"Index value {max_} exceeds the length of field.")
            min_ = min(subscript.start, subscript.stop)
            if min_ < 0:
                raise IndexError(f"Index value {min_} is less than zero.")

            if subscript.start == subscript.stop:
                return self.__setitem__(subscript.start, value)

            self_bin_val = format(self, "b")[1:][::-1]
            val_bin_val = Field.render_value(value=value, fmt=Field.Format.Bin, pad_to_length=max_ - min_ + 1)[1:][::-1]
            if subscript.start == min_:
                val_bin_val = val_bin_val[::-1]

            final_val = f"{self_bin_val[:min_]}{val_bin_val}{self_bin_val[max_+1:]}"[::-1]
            self.value = "b" + final_val

        else:
            if subscript < 0:
                raise IndexError("Negative indexing not supported in Field class")
            if subscript >= len(self):
                raise IndexError(f"{subscript} is greater than the most significant bit location of this field.")

            val = Field.render_value(value=value, fmt=Field.Format.Bin, pad_to_length=1)[1]
            self_bin_val = format(self, "b")[1:][::-1]
            rev_val = f"{self_bin_val[:subscript]}{val}{self_bin_val[subscript+1:]}"
            self.value = f"b{rev_val[::-1]}"

    def __add__(self, other):
        """
        If other is a correctly formatted value or another field, concatenate the values and return new field.
        If other is an integer, add the integer to the field value, but truncate to length of original field.
        """

        if isinstance(other, int):
            bin_val = format(int(self) + other, "b")[::-1][: len(self)][::-1]
            return type(self)(self._unit_length, value=f"b{bin_val}")

        if isinstance(other, str):
            fmt = Field.get_format(other)
            other_val = other[1:]
            self_val = self.render(fmt=fmt)[1:]
            final_val = Field.inverted_bases()[fmt] + self_val + other_val
            bit_final_val = Field.render_value(value=final_val, fmt=Field.Format.Bin, pad_to_length=len(final_val) * 4)
            return Bits(len(bit_final_val) - 1, value=bit_final_val)

        if isinstance(other, Field):
            return self.__add__(other.render(fmt=Field.Format.Bin))

        raise ValueError(f"Cannot add {type(other)} to Field type")

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
    def get_valid_chars(fmt):
        if fmt is Field.Format.Hex:
            return list("0123456789abcdefABCDEF")
        if fmt is Field.Format.Dec:
            return list("0123456789")
        if fmt is Field.Format.Oct:
            return list("01234567")
        if fmt is Field.Format.Bin:
            return list("01")


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
