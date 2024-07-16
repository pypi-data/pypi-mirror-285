"""Typing objects."""

from . import lib
from . import typ

__all__ = (
    'ArrayProto',
    'MappingProto',
    'SupportsParams',
    'VariadicArrayProto',
    )


class ArrayProto(lib.t.Protocol, lib.t.Collection[typ.AnyTypeCo]):
    """Protocol for a generic, single-parameter array."""

    def __init__(self, iterable: lib.t.Iterable[typ.AnyTypeCo], /) -> None: ...  # noqa

    def __iter__(self) -> lib.t.Iterator[typ.AnyTypeCo]: ...


class VariadicArrayProto(ArrayProto[tuple[lib.Unpack[typ.ArgsType]]]):  # noqa
    """Protocol for a generic, any-parameter array."""

    @lib.abc.abstractmethod
    def __hash__(self) -> int: ...


class MappingProto(lib.t.Protocol, lib.t.Generic[typ.AnyTypeCo, typ.AnyOtherTypeCo]):  # noqa
    """Protocol for a generic, double-parameter mapping."""

    def __init__(self, *args: lib.t.Any, **kwargs: lib.t.Any) -> None: ...

    def items(self) -> lib.t.ItemsView[typ.AnyTypeCo, typ.AnyOtherTypeCo]: ...  # noqa

    def keys(self) -> lib.t.KeysView[typ.AnyTypeCo]: ...

    def values(self) -> lib.t.ValuesView[typ.AnyOtherTypeCo]: ...


class SupportsParams(lib.t.Protocol, lib.t.Generic[lib.Unpack[typ.ArgsType]]):
    """Protocol for a generic with any number of parameters."""

    @property
    def __args__(self) -> tuple[lib.Unpack[typ.ArgsType]]: ...

    def __hash__(self) -> int: ...
