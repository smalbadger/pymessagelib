"""
This module contains the MessageBuilder class which generates Message subclasses from message format definitions.

Created on Feb 18, 2021

@author: smalb
"""

import inspect
from abc import ABCMeta
from typing import Dict

from pymessagelib.message import Message
from pymessagelib.field import Field
from pymessagelib._exceptions import (
    MissingFieldDataException,
    InvalidFieldException,
    InvalidFieldDataException,
    InvalidDataFormatException,
    CircularDependencyException,
    MultipleMatchingMessageDefinitionsException,
)
from pymessagelib.dependency_graph import DependencyGraph


class MessageBuilder:
    """
    The message builder dynamically creates message classes when given valid message formats.

    To load definitions, either provide them in the constructor, or call the load_definitions method.
    Multiple calls to the load_definitions method will add to the existing loaded definitions.

    All message definitions that are loaded will become accessible by message name as an attribute of
    the builder. For example, if a definition for a message called "GET_ADDR" is loaded into an object
    called `builder`, the generated class could be accessed via `builder.GET_ADDR`
    """

    def __init__(self, definitions={}):
        """Constructs a MessageBuilder class and loads the provided definitions."""
        self.message_classes = []
        self.load_definitions(definitions)

    def load_definitions(self, definitions: Dict):
        """Loads the provided definitions into this MessageBuilder object."""

        for name, definition in definitions.items():
            cls = self.build_message_class(name, definition)
            self.__dict__[name] = cls
            self.message_classes.append(cls)

    def build_message_class(self, cls_name, fmt):
        """
        Builds a message class when given the name of the message and a dictionary mapping field names
        to field objects.
        """

        # Categorize the fields to generate methods appropriately
        all_fields = {}
        writable_fields = {}
        readable_fields = {}
        auto_updated_fields = {}
        for name, item in fmt.items():
            if isinstance(item, Field):
                all_fields[name] = item
                if item.is_writable:
                    writable_fields[name] = item
                if item.is_readable:
                    readable_fields[name] = item
                if item.is_auto_updated:
                    auto_updated_fields[name] = item
            else:
                raise InvalidFieldException(f"cls_name: {name} must be a Field object.")

        # Define the metaclass to use
        class MessageType(ABCMeta):
            """This is a dynamically-created Metaclass that will be the type of all Message subclasses"""

            def __len__(self):
                """Return the length of the Message class. If any fields have non-positive lengths, return 0"""
                length = 0
                for field in all_fields.values():
                    length += len(field)
                return length

        # Create an empty class with the appropriate name that inherits from Message.
        msg_cls = MessageType(cls_name, (Message,), {})

        def __init__(self, **kwargs):
            """Constructor for generated Message subclasses."""
            Message.__init__(self, all_fields)

            # Verify values for all writable fields were provided via params
            for field_name in writable_fields:
                if field_name not in kwargs:
                    raise MissingFieldDataException(
                        f"A value must be provided for the '{field_name}' field upon instantiation"
                    )

            # initialize writable fields from parameters
            for param, val in kwargs.items():

                if param in all_fields and param not in writable_fields:
                    raise InvalidFieldException(f"Cannot specify a value for read-only field '{param}'.")
                elif param in all_fields:
                    context = None
                    if isinstance(val, Message):
                        context = type(val)
                        val = val.render()

                    if msg_cls.format[param].value_is_valid(val):
                        self._fields[param].value = val
                        if context:
                            self._fields[param].context = context
                    else:
                        raise InvalidFieldDataException(
                            f"'{val}' is not a valid value for the field '{param}' in message '{cls_name}'"
                        )
                else:
                    raise InvalidFieldException(f"'{param}' is not a valid field in the {cls_name} message.")

            self.update_fields()

        # Construct a graph of all dependencies - used for detecting circular imports and choosing order of updates.
        msg_cls.dependency_graph = DependencyGraph()
        for name, field in auto_updated_fields.items():
            dependencies = inspect.getfullargspec(field.value_updater)[0]
            for dependency in dependencies:
                msg_cls.dependency_graph.addEdge(name, dependency)

        # Verify no cycles exist in auto-update fields
        if msg_cls.dependency_graph.cycle is not None:
            raise CircularDependencyException(
                f"Detected cycle in auto-update fields: {' -> '.join(msg_cls.dependency_graph.cycle)}"
            )

        # Make a getter for all fields and a setter only for writable fields. Set each field name.
        for name, field in all_fields.items():
            getter = Message._create_getter(name)
            setter = Message._create_setter(name, field) if name in writable_fields else None
            setattr(msg_cls, name, property(getter, setter))
            field._name = name

        msg_cls.__init__ = __init__
        msg_cls.format = fmt
        msg_cls.bit_length = sum((len(field) for field in fmt.values()))

        return msg_cls

    def build_message(self, data):
        matches = []
        message = None
        for msg_cls in self.message_classes:
            try:
                msg = msg_cls.from_data(data)
            except InvalidDataFormatException as e:
                pass
            else:
                matches.append(msg_cls)
                message = msg

        if len(matches) == 0:
            msg_list = "\n".join([f"\t- {msg_cls.__name__}" for msg_cls in self.message_classes])
            raise InvalidDataFormatException(
                f"Data '{data}' could not be resolved to any of the following message types:\n{msg_list}"
            )
        elif len(matches) == 1:
            return message
        else:
            msg_list = "\n".join([f"\t- {msg_cls.__name__}" for msg_cls in matches])
            raise MultipleMatchingMessageDefinitionsException(
                f"Detected multiple message definitions that match the data '{data}':\n{msg_list}"
            )
