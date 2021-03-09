"""
Created on Feb 18, 2021

@author: smalb
"""


class InvalidFieldException(Exception):
    pass


class InvalidFieldDataException(Exception):
    pass


class MissingFieldDataException(Exception):
    pass


class InvalidFormatException(Exception):
    pass


class InvalidDataFormatException(Exception):
    pass


class MultipleMatchingMessageDefinitionsException(Exception):
    pass


class ContextDataMismatchException(Exception):
    pass


class ConflictingContextsException(Exception):
    pass


class CircularDependencyException(Exception):
    pass
