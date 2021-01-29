from message import Message
from msg_format import (
    Field,
    InvalidFieldException,
    InvalidFieldDataException,
    MissingFieldDataException,
)


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
        for name, item in fmt.items():
            if isinstance(item, Field):
                all_fields[name] = item
                if item.value is None:
                    writable_fields[name] = item
                else:
                    read_only_fields[name] = item

        def __init__(self, **kwargs):
            super(msg_cls, self).__init__()

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
                        self._private_fields[param] = val
                    else:
                        raise InvalidFieldDataException(
                            f"'{val}' is not a valid value for the field '{param}' in message '{cls_name}'"
                        )
                else:
                    raise InvalidFieldException(
                        f"'{param}' is not a valid field in the {cls_name} message."
                    )

            # Set read-only fields
            for field_name, field in read_only_fields.items():
                self._private_fields[field_name] = field.value

        # Make a getter for all fields and a setter only for writable fields
        for name, field in all_fields.items():
            getter = Message._create_getter(name)
            setter = (
                Message._create_setter(name, field) if name in writable_fields else None
            )
            setattr(msg_cls, name, property(getter, setter))

        msg_cls.__init__ = __init__
        msg_cls.format = fmt
        return msg_cls
