"""
Created on Feb 18, 2021

@author: smalb
"""

from message import Message
from field import Field
import inspect

from _exceptions import MissingFieldDataException, InvalidFieldException, InvalidFieldDataException,\
    CircularDependencyException
from dependency_graph import DependencyGraph


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
            
        self.dependency_graph = DependencyGraph(len(auto_updated_fields))
        for name, field in auto_updated_fields.items():
            dependencies = inspect.getfullargspec(field.value_updater)[0]
            for dependency in dependencies:
                self.dependency_graph.addEdge(name, dependency)
                
        if self.dependency_graph.cycle is not None:
            raise CircularDependencyException(f"Detected cycle in auto-update fields: {' -> '.join(self.dependency_graph.cycle)}")

        # Make a getter for all fields and a setter only for writable fields
        for name, field in all_fields.items():
            getter = Message._create_getter(name)
            setter = Message._create_setter(name, field) if name in writable_fields else None
            setattr(msg_cls, name, property(getter, setter))

        msg_cls.__init__ = __init__
        msg_cls.format = fmt
        msg_cls.bit_length = sum((len(field) for field in fmt.values()))

        return msg_cls
