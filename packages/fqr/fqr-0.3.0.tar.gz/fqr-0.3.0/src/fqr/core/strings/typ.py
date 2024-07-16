"""Strings typing."""

from .. import typ

__all__ = (
    'camelCase',
    'datetime',
    'numeric',
    'snake_case',
    'string',
    'Casing',
    'StringFormat',
    'StringType',
    *typ.__all__
    )

from .. typ import *

from . import lib

camelCase = lib.t.NewType('camelCase', str)
snake_case = lib.t.NewType('snake_case', str)
datetime = lib.t.NewType('datetime', str)
numeric = lib.t.NewType('numeric', str)

Casing = (
    camelCase
    | snake_case
    )

StringFormat = (
    camelCase
    | snake_case
    | datetime
    | numeric
    )

StringType = lib.t.TypeVar('StringType', bound=StringFormat)


class string(str, lib.t.Generic[StringType]):
    """Protocol for a generic `str`."""
