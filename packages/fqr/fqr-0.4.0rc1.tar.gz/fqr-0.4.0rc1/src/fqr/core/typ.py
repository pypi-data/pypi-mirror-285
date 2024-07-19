"""Core typing."""

__all__ = (
    'AnyDict',
    'AnyOtherType',
    'AnyOtherTypeCo',
    'AnyType',
    'AnyTypeCo',
    'ArgsType',
    'Literal',
    'NoneType',
    'OptionalAnyDict',
    'Primitive',
    'PackageExceptionType',
    'Serial',
    )

from . import lib

if lib.t.TYPE_CHECKING:  # pragma: no cover
    from . import exc  # noqa: F401

AnyDict = dict[str, lib.t.Any]
Literal = lib.t.Literal['*']
NoneType = lib.types.NoneType  # type: ignore[valid-type]
OptionalAnyDict = lib.t.Optional[dict[str, lib.t.Any]]
Primitive = bool | float | int | NoneType | str
Serial = Primitive | dict[Primitive, 'Serial'] | list['Serial']

AnyType = lib.t.TypeVar('AnyType')
AnyOtherType = lib.t.TypeVar('AnyOtherType')
AnyTypeCo = lib.t.TypeVar('AnyTypeCo', covariant=True)
AnyOtherTypeCo = lib.t.TypeVar('AnyOtherTypeCo', covariant=True)
ArgsType = lib.TypeVarTuple('ArgsType')

PackageExceptionType = lib.t.TypeVar(
    'PackageExceptionType',
    bound='exc.BasePackageException',
    covariant=True,
    )
