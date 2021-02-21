"""
Created on Jan 9, 2021

@author: smalbadger
"""

from abc import ABC
import inspect
from typing import Dict
from copy import deepcopy

from field import Field
from _exceptions import InvalidDataFormatException


class Message(ABC):
    """
    classdocs
    """

    def __init__(self, fields: Dict):
        """Constructor"""

        # Fields need to be deep copied so the same field objects aren't shared
        # across all message instances of the same type.
        self._fields = deepcopy(fields)  # maps field names to field objects
        self._parent_field = None

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
            if field.context is not None:
                msg = field.value
                msg._parent_field = field
                return msg
            else:
                return field

        return get_field

    @property
    def context(self):
        if self._parent_field is not None:
            return self._parent_field.context
        else:
            return None

    @context.setter
    def context(self, context):
        assert self._parent_field is not None
        self._parent_field.context = context

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

    def render(self):
        bin_data = f"b{''.join([data.render(fmt=Field.Format.Bin)[1:] for data in self._fields.values()])}"
        return Field.render_value(value=bin_data, fmt=Field.Format.Hex, pad_to_length=len(self) // 4)

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
        # 1. Convert the data to binary
        binary_data = Field.render_value(value=data, fmt=Field.Format.Bin, pad_to_length=cls.bit_length)[1:]

        # 2. chunk into fields
        writable_field_data = {}
        for fieldname, field in cls.format.items():
            if field.is_writable:
                writable_field_data[fieldname] = f"b{binary_data[:len(field)]}"
            binary_data = binary_data[len(field) :]

        # 3. Construct a new message providing data only for writable fields.
        try:
            return cls(**writable_field_data)
        except Exception as e:  # TODO: Narrow exception handling
            raise InvalidDataFormatException(f"the data '{data}' doesn't fit the format for '{cls.__name__}'")
