[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


# PyMessageLib
A simple Python library for constructing/dissecting messages


## Introduction
This project defines a system for extracting/packaging information into custom message formats. It's intended to be a flexible framework that bridges the gap between computer-talk and human-talk. For example, if I send a message of `0x8472FEF7ABC94838925146DEA` to a device, and I'm expecting a response of either `0x00023000` or `0x89000000` - that's cool, but speaking in hexidecimal sucks! It would be so much better if I could describe the values messages (requests and responses) in human-readable terms.

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

In some cases, undefined fields will cause issues with representing the message in machine form. For example, assume you want to describe the following message:

GET_SERVICE_REQ (4-bit message) with the following fields:

- NO_POWER (1 bit)
- INVALID_CRC (1 bit)
- TIMER_STOPPED (1 bit)
- DETECTED_THREAT (1 bit)

Assume the machine-form of this message must be a single hexadecimal digit. If any of the fields are undefined, multiple hexadecimal values will satisfy the data contained in the message. In this case, a `MessageNotSufficientlyDefinedException` will be raised.

## Message Format Structure

{
	"GET_ADDR": {
		"id": Nibbles(4, value="0014"),
		"ptr": Bytes(4),
		"addr": Bits(11),
		"pad": Bits(3, value="000"),
		"crc": lambda ptr, addr, pad: EKMS32Bit(ptr, addr, pad)
	},
	"FILL_KEY": {
		"id": Nibbles(4, value="0015"),
		"ptr": Bytes(3),
		"addr": Bits(2),
		"pad": Bits(4, value="0000"),
		"crc": lambda ptr, addr, pad: EKMS32Bit(ptr, addr, pad)
	}
}

## Comparator Class

For complicated message comparison, `Comparator` classes can be created and linked to compatible `Message` classes. Here is an example of a complicated comparison:

Assume we have 2 message objects of the same type with 4 fields. We want to verify that field 1 is not equal, field 2 is equal, and field 3 is only equal if field 4 is not equal.