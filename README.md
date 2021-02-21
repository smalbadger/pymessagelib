[![Build Status](https://travis-ci.com/smalbadger/pymessagelib.svg?branch=main)](https://travis-ci.com/smalbadger/pymessagelib)
[![codecov](https://codecov.io/gh/smalbadger/pymessagelib/branch/main/graph/badge.svg?token=QJ5EOBJ0P6)](https://codecov.io/gh/smalbadger/pymessagelib)
[![CodeFactor](https://www.codefactor.io/repository/github/smalbadger/pymessagelib/badge)](https://www.codefactor.io/repository/github/smalbadger/pymessagelib)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# PyMessageLib
A simple Python library for constructing/dissecting messages


## Introduction
This project defines a system for extracting/packaging information into custom message formats. It's intended to be a flexible framework that bridges the gap between computer-talk and human-talk. For example, if I send a message of `0x8472FEF7ABC94838925146DEA` to a device, and I'm expecting a response of either `0x00023000` or `0x89000000` - that's cool, but speaking in hexidecimal sucks! It would be so much better if I could describe the message formats in human-readable terms and generate the hex codes automatically.

## Alternative Packages
The `struct` package is already heavily used for this, but lacks the following features:

- Auto-updating fields
- Nested field contexts

## Our Solution at a High Level
PyMessageLib dynamically creates functional classes based on user-defined message formats. The generated classes allow us to work with messages in human-readable, modular form. When instantiated, message objects are made up of fields that were specified in the original message format definitions. Field values can be constants, functions, strings, or other messages.

### Constant Field Values
When defining a message format, a constant can be specified as the field value. This indicates a read-only field.

### String and Message Field Values
If no value is specified for a field in a message format definition, the value must be assigned during instantiation and can be overwritten later. If a string is given as the value, no additional meaning will be given to different portions of the string - it is treated as one value. If another message object is given as the value, the fields of the message will be retained to allow for nested field context.

### Function Field Values
Some fields should auto-update based on other information within the message. Examples of this would be a length field or a CRC field. For auto-updating fields, the names of all arguments of the function need to match the names of field values of the message. The function used for an auto-updating field cannot depend on it's own field, but it can depend on other auto-updating fields within the message with one exception - there can't be circular logic in auto-updating fields.

## Message Class

The `Message` class:

- Describes the message content in both human AND machine readable string formats (yes, both need to be defined for each subclass)
- Defines the conversion process to get between human and machine formats
- Supports comparison with other messages (via `Comparator` class for complex comparisons)
- Allows data fields to be read/written
- Doesn't require all data fields to be defined (treat as "don't care" values)
- (Maybe) Supports inheritance - allows us to group messages based on structure and reduce code duplication.

A `Message` object can be created by:

- Providing human string format to `create` static constructor
- Providing machine string format to `create` static constructor
- Providing field values to `__init__` constructor. Fields not provided will be undefined.

## Message Format Structure
```python
{
	"GET_ADDR": {
		"id": Nibbles(4, value="0014"),
		"ptr": Bytes(4),
		"addr": Bits(11),
		"pad": Bits(3, value="000"),
		"crc": lambda ptr, addr, pad: EKMS32Bit(ptr, addr, pad)
	},
	"SQUIRT_THING": {
		"id": Nibbles(4, value="0015"),
		"ptr": Bytes(3),
		"addr": Bits(2),
		"pad": Bits(4, value="0000"),
		"crc": lambda ptr, addr, pad: CRC32Bit(ptr, addr, pad)
	}
}
```