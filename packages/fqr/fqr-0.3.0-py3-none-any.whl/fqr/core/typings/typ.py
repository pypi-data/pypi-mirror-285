"""Typing types."""

from .. import typ

__all__ = (
    'AnyOrForwardRef',
    'Array',
    'ArrayType',
    'Mapping',
    'MappingType',
    'NumberType',
    'VariadicArray',
    'VariadicArrayType',
    'StrOrForwardRef',
    'UnionGenericAlias',
    *typ.__all__
    )

from .. typ import *

from . import lib
from . import obj  # noqa: F401

AnyOrForwardRef = lib.t.ForwardRef | lib.t.Any
StrOrForwardRef = lib.t.ForwardRef | str
UnionGenericAlias = type(int | str)

Array: lib.t.TypeAlias = 'obj.ArrayProto[AnyType]'
NumberType = lib.t.TypeVar('NumberType', bound=lib.numbers.Number)
Mapping: lib.t.TypeAlias = (
    'obj.MappingProto[AnyType, AnyOtherType]'
    )
VariadicArray: lib.t.TypeAlias = (
    'obj.VariadicArrayProto[lib.Unpack[tuple[AnyType, ...]]]'
    )

ArrayType = lib.t.TypeVar('ArrayType', bound=Array)
MappingType = lib.t.TypeVar('MappingType', bound=Mapping)
VariadicArrayType = lib.t.TypeVar('VariadicArrayType', bound=VariadicArray)
