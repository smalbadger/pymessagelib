"""
Created on Jan 9, 2021

@author: smalbadger
"""

from abc import ABC
import inspect


class Message(ABC):
    """
    classdocs
    """

    def __init__(self, human=None, machine=None):
        """Constructor"""
        self._private_fields = (
            {}
        )  # maps field names to values - used by setters/getters

    @staticmethod
    def _create_setter(name, field):
        """Used for dynamically creating setters for field properties of subclasses."""

        def set_field(self, value):
            assert field.value_is_valid(value)
            self._private_fields[name] = value

        return set_field

    @staticmethod
    def _create_getter(name):
        """Used for dynamically creating getters for field properties of subclasses."""

        def get_field(self):
            field_val = self._private_fields[name]
            if inspect.isfunction(field_val):
                field_val = field_val(
                    *[
                        self._private_fields[arg]
                        for arg in inspect.getfullargspec(field_val)[0]
                    ]
                )

            # TODO: Assert that the field value is valid.

            return field_val

        return get_field

    def machine_form(self):
        """Converts the message to a machine-readable format"""
        pass

    def human_form(self):
        """Converts the message to a human-readable format"""
        pass
