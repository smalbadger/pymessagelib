[![Build Status](https://travis-ci.com/smalbadger/pymessagelib.svg?branch=main)](https://travis-ci.com/smalbadger/pymessagelib)
[![codecov](https://codecov.io/gh/smalbadger/pymessagelib/branch/main/graph/badge.svg?token=QJ5EOBJ0P6)](https://codecov.io/gh/smalbadger/pymessagelib)
[![Interrogate](https://raw.githubusercontent.com/smalbadger/pymessagelib/main/badges/interrogate_badge.svg)](https://github.com/smalbadger/pymessagelib/blob/main/badges/interrogate_badge.svg)
[![CodeFactor](https://www.codefactor.io/repository/github/smalbadger/pymessagelib/badge)](https://www.codefactor.io/repository/github/smalbadger/pymessagelib)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# PyMessageLib
A simple Python library for constructing/dissecting hexadecimal, decimal, octal, or binary data in a meaningful way. "Message" is in the name because this package was designed for communicating with devices by sending hexadecimal values that have very specific meaning.

## Introduction
This project defines a system for extracting/packaging information into custom message formats. It's intended to be a flexible framework that bridges the gap between computer-talk and human-talk. For example, if I send a message of `0x8472FEF7ABC94838925146DEA` to a device, and I'm expecting a response of either `0x00023000` or `0x89000000` - that's cool, but speaking in hexidecimal sucks! It would be so much better if I could describe the message formats in human-readable terms and generate the hex codes automatically.

## Alternative Packages
The `struct` package is already heavily used for this, but lacks the following features:

- Auto-updating fields
- Nested field contexts

## Our Solution at a High Level
PyMessageLib dynamically creates functional classes based on user-defined message formats. The generated classes allow us to work with messages in a human-readable, modular form. When instantiated, message objects are made up of fields that were specified in the original message format definitions.

## Quick Start Guide

### Installation

To install, simply use this command:

`pip install pymessagelib`


### Message Definitions

At the highest level, we have a set of Message Definitions. A set of message definitions is represented as a Python dictionary where each key is the message name and the corresponding value is a dictionary mapping field names to field format definitions. Each message definition specifies a single level in the message hierarchy. Later, we'll get into nesting messages, but at the message definition level, keep it simple.

For example, suppose the unit I'm communicating with supports a command called `GET_ADDR` with the following fields:

- A 2-byte field with constant value `x0014` called "id"
- A 4-byte field of any value called "ptr"
- An 11-bit field of any value called "addr" where the first 3 bytes specify a device and the last byte specifies a location.
- 3 bits of padding (`b000`) called "pad"
- A CRC that is calculated over the ptr, addr, and pad fields.

We would start out by creating a message definition that describes the top-level of complexity and then we can define more messages to add more meaning to specific fields. In this case, the message definitions would look like:

```python
>>> msg_fmts = {
... 	"GET_ADDR": {
... 		"id": Nibbles(4, value="0014"),
... 		"ptr": Bytes(4),
... 		"addr": Bits(11),
... 		"pad": Bits(3, value="000"),
... 		"crc": lambda ptr, addr, pad: EKMS32Bit(ptr, addr, pad)
... 	},
... 	"ADDR_FORMAT": {
... 		"device": Bits(3),
... 		"location": Byte(),
... 	}
... }
```

#### Field Definitions

When mapping field names to field format definitions, the following classes are available:

- Bit
- Bits
- Nibble
- Nibbles
- Byte
- Bytes
- Word
- Words
- DWord
- DWords
- QWord
- QWords
	
You can use any of the classes above that result in the exact number of bits being defined, making use of the first arugment which specifies length in units. For example, if I have a field that's 32 bits long, I could specify it as:

- Bits(32)
- Nibbles(8)
- Bytes(4)
- Words(2)
- DWord()

Note that `DWords(1)` is invalid as is `Word(2)` because the singular or plural variant would better suit the situation.
	
When specifying a field value, the following rules apply:

1. If a string value is given for a specific field in the message definition, that field will be read-only and cannot be changed. The string must conform to the [value-specifier form](#value-specifier-form).
1. If no value is specified, the field will be writable. 
1. If the value is set to be a function, the field is considered an "auto-update" field. The argument names of the function must match field names of the same message and the function must be able to process Field objects.

### Generating Message Classes

Highly-functional Message classes can be generated from the [message definitions](message-definitions) using a `MessageBuilder`. A MessageBuilder stores a set of message definitions and provides the following functionality:

- Generates Message subclasses from message definitions
- Constructs Message objects from raw data

To use the message builder, at least one set of message definitions must be provided. More sets of message definitions can be loaded after instantiation.

```python
>>> builder = MessageBuilder(definitions=msg_fmts)
>>> builder.load_definitions(more_fmts)
```

Once message definitions are loaded, Message subclasses corresponding to the message definitions can be accessed using the dot-notation and the message names. To instantiate the message objects, values for all writable fields must be provided.

```python
>>> get_addr = builder.GET_ADDR(ptr="x0012", addr='x11')
```

Once a message object has been instantiated, fields can be accessed and nested meaning can be given by setting the `context` of a specific field:

```python
>>> get_addr.addr
'b00000010010'
>>> get_addr.addr.context = builder.ADDR_FORMAT # allows us to access further levels of information
>>> get_addr.addr.device
'b000'
>>> get_addr.addr.location
'b00010010'
```

Fields and messages can be rendered in different formats:

```python
>>> get_addr.addr.render(fmt=Field.Format.Hex)
'x012'
>>> get_addr.addr.render(fmt=Field.Format.Dec)
'd018'
>>> get_addr.addr.render(fmt=Field.Format.Oct)
'o0022'
>>> get_addr.addr.render(fmt=Field.Format.Bin)
'b0000010010'
```

Writable fields can be set easily:

```python
>>> get_addr.addr = 'b11100000001'
>>> get_addr.addr.devie = 'b001'
```

Messages can be rendered as tables. They can also be compared as tables using the compare_tables() function

```python
>>> get_addr.addr.render_table(expand_nested=True)[1]
+GET_ADDR-------+-----------+
| Field Name    | Value     |
+---------------+-----------+
| id            | x0014     |
| ptr           | x00000012 |
| addr.device   | b000      |
| addr.location | x12       |
| pad           | b000      |
| crc           | xe45129da |
+---------------+-----------+
```


### Value Specifier Form

This library is intended to work well with string values that follow a specific form which we call "Value Specifier Form". This form has 2 parts:

1. A format specifier. Valid format specifiers are:
	- `x` for hexadecimal
	- `d` for decimal
	- `o` for octal
	- `b` for binary
2. A value. The value must contain only characters that are valid according to the format specifier. For hexadecimal values, the characters can be upper or lower case.

Here are some strings that conform to value-specifier form:

- `"x00FF"`
- `"d908984"`
- `"b00100101011"`
- `"o07154"`

Here are some strings that do not conform:

- `"x 00FF"` - ' ' is not a valid character
- `"x_00FF"` - '_' is not a valid character
- `"bFF"` - 'FF' isn't valid binary
- `"o99"` - '99' isn't valid octal form
- `"99"` - missing format specifier
