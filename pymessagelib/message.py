"""
Created on Jan 9, 2021

@author: smalbadger
"""

from abc import ABC
import inspect
from enum import Enum
from typing import Dict
from copy import deepcopy
import math

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


class ContextDataMismatchException(Exception):
    pass


###########################################################################
# Field Class
###########################################################################


class Field(ABC):
    class Format(Enum):
        Bin = 2
        Oct = 8
        Dec = 10
        Hex = 16

    def __init__(self, length, value=None, format=None, context=None):
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

        # Determine the format the value will be rendered
        if format:
            self._format = format
        elif value is not None and not inspect.isfunction(value):
            self._format = Field.get_format(value)
        else:
            self._format = Field.Format.Bin if "Bit" in type(self).__name__ else Field.Format.Hex

        # Determine how many characters to display when displaying in default format
        self._character_length = math.ceil(self._bit_length / math.log2(self._format.value))

        # Determine if the value is a function or an actual value.
        if inspect.isfunction(value):
            self._value_function = value
        elif value is not None:
            assert self.value_is_valid(value)
            self._value = self.render(value=value, fmt=Field.Format.Bin, pad_to_length=self._bit_length)
            assert len(self._value) - 1 == self._bit_length

    def render(self, value=None, fmt=None, pad_to_length=0) -> str:
        if not value:
            value = self.value
        if not fmt:
            fmt = self._format
        pad_to_length = pad_to_length if pad_to_length > 0 else self._character_length
        return Field.render_value(value=value, fmt=fmt, pad_to_length=pad_to_length)
    
    @staticmethod
    def render_value(*, value, fmt, pad_to_length):
        prefix, numeric_value = value[0], value[1:]
        int_val = int(numeric_value, Field.bases()[prefix].value)
        fmt_str = f"0{pad_to_length}{Field.inverted_bases()[fmt]}"
        return Field.inverted_bases()[fmt] + format(int_val, fmt_str)

    def value_is_valid(self, value):
        bin_value = self.render(value=value, fmt=Field.Format.Bin, pad_to_length=self._bit_length)[1:]
        if len(bin_value) == self._bit_length:
            return True
        return False

    @property
    def value_updater(self):
        return self._value_function

    @property
    def is_readable(self):
        return self._access["Read"]

    @property
    def is_writable(self):
        return self._access["Write"]

    @property
    def is_auto_updated(self):
        return self._access["Auto Update"]

    @property
    def value(self):
        if self.context:
            return self.context.from_data(self._value)
        return self._value

    @value.setter
    def value(self, value):
        assert self.value_is_valid(value)
        self._value = value

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context):
        assert isinstance(context, Message)
        try:
            self.context.from_data(self._value)
        except InvalidDataFormatException:
            raise ContextDataMismatchException(
                f"The data '{self._value}' is not compatible with context {context.__name__}"
            )

    def __repr__(self):
        if self.value:
            return self.render()
        else:
            return f'<{type(self).__name__} Field, length={self._unit_length} ({len(self)} bits), value=undefined>'

    def __eq__(self, other):

        if isinstance(other, Field):
            return self.__eq__(other._value)

        self_prefix, self_numeric_value = self._value[0], self._value[1:]
        self_int_val = int(self_numeric_value, Field.bases()[self_prefix].value)

        other_prefix, other_numeric_value = other[0], other[1:]
        other_int_val = int(other_numeric_value, Field.bases()[other_prefix].value)

        return self_int_val == other_int_val

    def __lt__(self, other):
        pass

    def __bytes__(self):
        pass

    def __call__(self):
        pass

    def __len__(self):
        return self._bit_length

    def __contains__(self):
        pass

    def __getitem__(self):
        pass

    def __setitem__(self, value):
        pass

    def __add__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __lshift__(self, amount):
        pass

    def __rshift__(self, amount):
        pass

    def __and__(self, other):
        pass

    def __rand__(self, other):
        pass

    def __xor__(self, other):
        pass

    def __rxor__(self, other):
        pass

    def __or__(self, other):
        pass

    def __ror__(self, other):
        pass

    def __int__(self):
        pass

    def __invert__(self):
        bin_val = self.render(fmt=Field.Format.Bin)
        inv_bin_val = bin_val.replace("0", "_").replace("1", "0").replace("_", "0")
        inv_val = Field.render(value=inv_bin_val, fmt=self._format)
        newfield = type(self).__new__()
        newfield.__init__(self._character_length, value=inv_val, format=self._format)
        return newfield

    def __bool__(self):
        return "1" in self.render(Field.Format.Bin)

    ######################################################
    # Static Methods
    ######################################################

    @staticmethod
    def bases():
        return {
            "b": Field.Format.Bin,
            "o": Field.Format.Oct,
            "d": Field.Format.Dec,
            "x": Field.Format.Hex,
        }

    @staticmethod
    def inverted_bases():
        return {v: k for k, v in Field.bases().items()}

    @staticmethod
    def get_format(value):
        return Field.bases()[value[0]]

    @staticmethod
    def pad_to_length(value, length):
        prefix = value[0]
        numeric_value = value[1:]
        if len(numeric_value) <= length:
            padding = "0" * (length - len(numeric_value))
            return f"{prefix}{padding}{numeric_value}"
        else:
            raise Exception("Value is already longer than padding length")


class Bits(Field):
    bits_per_unit = 1


class Nibbles(Field):
    bits_per_unit = 4


class Bytes(Field):
    bits_per_unit = 8


class Words(Field):
    bits_per_unit = 16


class DWords(Field):
    bits_per_unit = 32


class QWords(Field):
    bits_per_unit = 64


Bit = Bits
Nibble = Nibbles
Byte = Bytes
Word = Words
DWord = DWords
QWord = QWords

###########################################################################
# Message Class
###########################################################################


class Message(ABC):
    """
    classdocs
    """

    def __init__(self, fields: Dict):
        """Constructor"""

        # Fields need to be deep copied so the same field objects aren't shared
        # across all message instances of the same type.
        self._fields = deepcopy(fields)  # maps field names to field objects

    @staticmethod
    def _create_setter(name, field):
        """Used for dynamically creating setters for field properties of subclasses."""

        def set_field(self, value):
            assert field.value_is_valid(value)
            self._fields[name].value = value
            self.update_fields()

        return set_field

    @staticmethod
    def _create_getter(name):
        """Used for dynamically creating getters for field properties of subclasses."""

        def get_field(self):
            field = self._fields[name]
            return field

        return get_field

    def update_fields(self):
        # Update all auto-update fields
        auto_update_fields = [f for f in self._fields.values() if f.is_auto_updated]

        for field in auto_update_fields:
            field._value = None  # erase old values

        for i in range(len(auto_update_fields)):
            try_again = False
            for field in auto_update_fields:
                field.value = field.value_updater(
                    *[self._fields[arg].value for arg in inspect.getfullargspec(field.value_updater)[0]]
                )
                if field._value is None:
                    try_again = True

            if i == len(auto_update_fields) - 1 and try_again:
                raise Exception("Circular field dependency detected!")
            elif not try_again:
                break

    def render_table(self, formats=(Field.Format.Hex, Field.Format.Bin)) -> str:

        # Calculate column widths based on max lengths
        max_field_name_length = len(max(self._fields.keys(), key=len))
        max_format_lens = []
        for fmt in formats:
            max_format_lens.append(len(max([f.render(fmt=fmt) for f in self._fields.values()], key=len)))

        # Build header
        name_col_fmt = "| {:^" + str(max_field_name_length) + "s} |"
        hdr = name_col_fmt.format("Field")
        for fmt, l in zip(formats, max_format_lens):
            column_fmt = " {:^" + str(l) + "s} |"
            hdr += column_fmt.format(fmt.name)

        hdr_bars = f"+={'='*max_field_name_length}=+"
        for l in max_format_lens:
            hdr_bars += f"={'='*l}=+"
        row_separator = hdr_bars.replace("=", "-")

        ascii_table = f"{hdr_bars}\n{hdr}\n{hdr_bars}"

        # Build field rows
        for fieldname, field in self._fields.items():

            name_col_fmt = "| {:<" + str(max_field_name_length) + "s} |"
            row = name_col_fmt.format(fieldname)

            for fmt, l in zip(formats, max_format_lens):
                column_fmt = " {:<" + str(l) + "s} |"
                row += column_fmt.format(field.render(fmt=fmt))

            ascii_table += f"\n{row}\n{row_separator}"

        return ascii_table

    def compare_tables(self, other_message):

        my_table = self.render_table().split("\n")
        other_table = other_message.render_table().split("\n")

        comps = {}
        counter = 3
        for field1, field2 in zip(self._fields.values(), other_message._fields.values()):
            comps[counter] = field1.value == field2.value
            counter += 2

        counter = 0
        for my_line, other_line in zip(my_table, other_table):
            if counter in comps:
                comp = "==" if comps[counter] is True else "!="
            else:
                comp = "  "

            print(f"{my_line}  {comp}  {other_line}")
            counter += 1

        return False in comps
    
    def __len__(self):
        return type(self).bit_length

    @classmethod
    def from_data(cls, data):
        # TODO: Chunk up the data and instantiate a new object with populated fields.
        # 1. Convert the data to binary
        binary_data = Field.render_value(value=data, fmt=Field.Format.Bin, pad_to_length=cls.bit_length)[1:]
        
        # 2. chunk into fields
        writable_field_data = {}
        for fieldname, field in cls.format.items():
            print(field)
            if field.is_writable:
                writable_field_data[fieldname] = f'b{binary_data[:len(field)]}'
            binary_data = binary_data[len(field):]
            
        print(writable_field_data)
        
        # 3. Construct a new message providing data only for writable fields.
        return cls(**writable_field_data)
        
        #try:
        #    
        #except:
        #    raise InvalidDataFormatException(f"the data '{data}' doesn't fit the format for '{cls.__name__}'")


###########################################################################
# MessageBuilder Class
###########################################################################


class MessageBuilder:
    """
    The message builder dynamically creates message classes given valid message formats.
    """

    def build_message_classes(self, msg_format_dict):
        """
        :param msg_format_dict: Maps message names to formats. The formats are a dictionary that follows the structure defined in the README.md
        :type msg_format_dict: Dict
        """
        messages = {}
        for msg_name, msg_format in msg_format_dict.items():
            messages[msg_name] = self.build_message_class(msg_name, msg_format)
        return messages

    def build_message_class(self, cls_name, fmt):

        # Create an empty class with the appropriate name that inherits from Message.
        msg_cls = type(cls_name, (Message,), {})

        # Categorize the fields to generate methods appropriately
        all_fields = {}
        writable_fields = {}
        read_only_fields = {}
        auto_updated_fields = {}
        for name, item in fmt.items():
            if isinstance(item, Field):
                all_fields[name] = item
                if item.is_writable:
                    writable_fields[name] = item
                if item.is_readable:
                    read_only_fields[name] = item
                if item.is_auto_updated:
                    auto_updated_fields[name] = item

        def __init__(self, **kwargs):
            Message.__init__(self, all_fields)

            # Verify values for all writable fields were provided via params
            for field_name in writable_fields:
                if field_name not in kwargs:
                    raise MissingFieldDataException(
                        f"A value must be provided for the '{field_name}' field upon instantiation"
                    )

            # initialize writable fields from parameters
            for param, val in kwargs.items():
                if param in all_fields:
                    if msg_cls.format[param].value_is_valid(val):
                        self._fields[param].value = val
                    else:
                        raise InvalidFieldDataException(
                            f"'{val}' is not a valid value for the field '{param}' in message '{cls_name}'"
                        )
                else:
                    raise InvalidFieldException(f"'{param}' is not a valid field in the {cls_name} message.")

            self.update_fields()

        # Make a getter for all fields and a setter only for writable fields
        for name, field in all_fields.items():
            getter = Message._create_getter(name)
            setter = Message._create_setter(name, field) if name in writable_fields else None
            setattr(msg_cls, name, property(getter, setter))

        msg_cls.__init__ = __init__
        msg_cls.format = fmt
        msg_cls.bit_length = sum((len(field) for field in fmt.values()))
        return msg_cls
