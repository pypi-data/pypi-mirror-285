"""Type checking utility functions."""

__all__ = (
    'get_args',
    'get_checkable_types',
    'expand_types',
    'is_array',
    'is_array_type',
    'is_bool_type',
    'is_date_type',
    'is_datetime_type',
    'is_literal',
    'is_mapping',
    'is_mapping_type',
    'is_none_type',
    'is_number_type',
    'is_params_type',
    'is_primitive',
    'is_serialized_mapping',
    'is_typevar',
    'is_union',
    'is_variadic_array_type',
    )

from .. import lib
from .. import obj
from .. import typ


def get_args(tp: lib.t.Any) -> tuple[lib.t.Any, ...]:
    """Wrapper for `lib.t.get_args`."""

    return lib.t.get_args(tp)


@lib.t.overload
def get_type_args(
    tp: obj.SupportsParams[lib.Unpack[typ.ArgsType]]
    ) -> tuple[lib.Unpack[typ.ArgsType]]: ...
@lib.t.overload
def get_type_args(
    tp: type[lib.t.Any]
    ) -> tuple[lib.t.Any, ...]: ...
def get_type_args(
    tp: (
        obj.SupportsParams[lib.Unpack[typ.ArgsType]]
        | type[lib.t.Any]
        )
    ) -> (
        tuple[lib.Unpack[typ.ArgsType]]
        | tuple[lib.t.Any, ...]
        ):
    """
    Get generic arguments for `type[Any]`.

    ---

    `Literals` will be returned as the types of their values.

    #### Examples

    ```py
    get_type_args(Literal[1])
    (int, )

    get_type_args(tuple[str, int])
    (str, int, )

    ```

    """

    return tuple(
        type(arg)
        if is_literal(tp)
        else arg
        for arg
        in get_args(tp)
        )


@lib.t.overload
def get_checkable_types(
    any_tp: type[typ.AnyType]
    ) -> tuple[type[typ.AnyType] | type, ...]: ...
@lib.t.overload
def get_checkable_types(
    any_tp: lib.t.Any
    ) -> tuple[type, ...]: ...
def get_checkable_types(
    any_tp: type[typ.AnyType] | type[lib.t.Any] | lib.t.Any
    ) -> tuple[typ.AnyType | type, ...] | tuple[type, ...]:
    """
    Get checkable origin lib.types, handling `Union` and `TypeVar` \
    expansions automatically.

    ---

    `Literals` will be returned as their values.

    """

    checkable_types = {
        otp
        for tp
        in expand_types(any_tp)
        if isinstance((otp := lib.t.get_origin(tp) or tp), type)
        }

    return tuple(checkable_types)


@lib.t.overload
def expand_types(
    any_tp: type[typ.AnyType]
    ) -> tuple[type[typ.AnyType] | type[lib.t.Any], ...]: ...
@lib.t.overload
def expand_types(
    any_tp: lib.t.Any
    ) -> tuple[type[lib.t.Any], ...]: ...
def expand_types(
    any_tp: type[typ.AnyType] | lib.t.Any
    ) ->(
        tuple[type[typ.AnyType] | type[lib.t.Any], ...]
        | tuple[type[lib.t.Any], ...]
        ):
    """
    Recursively get valid subtypes into flattened `tuple` from a \
    passed `type`, `Union`, or `TypeVar`.

    ---

    `Literals` will be returned as their values.

    """

    if is_union(any_tp):
        return tuple(
            tp
            for tp
            in set(
                lib.itertools.chain.from_iterable(
                    expand_types(sub_tp)
                    for sub_tp
                    in get_type_args(any_tp)
                    )
                )
            )
    elif is_typevar(any_tp):
        if any_tp.__constraints__:
            return tuple(
                tp
                for tp
                in set(
                    lib.itertools.chain.from_iterable(
                        expand_types(sub_tp)
                        for sub_tp
                        in any_tp.__constraints__
                        )
                    )
                )
        elif any_tp.__bound__:
            return expand_types(any_tp.__bound__)
        else:
            return (object, )
    elif is_literal(any_tp):
        return (type(get_args(any_tp)[0]), )
    else:
        return (any_tp, )


@lib.t.overload
def is_params_type(
    tp: obj.SupportsParams[lib.Unpack[typ.ArgsType]],
    ) -> lib.t.TypeGuard[
        obj.SupportsParams[lib.Unpack[typ.ArgsType]]
        ]: ...
@lib.t.overload
def is_params_type(
    tp: lib.t.Any
    ) -> lib.t.TypeGuard[
        obj.SupportsParams[lib.Unpack[tuple[lib.t.Any, ...]]]
        ]: ...
def is_params_type(
    tp: obj.SupportsParams[lib.Unpack[typ.ArgsType]] | lib.t.Any
    ) -> lib.t.TypeGuard[
        obj.SupportsParams[lib.Unpack[typ.ArgsType]]
        | obj.SupportsParams[lib.Unpack[tuple[lib.t.Any, ...]]]
        ]:
    """Return `True` if `tp` has type args."""

    return bool(get_args(tp))


def is_typevar(
    obj: lib.t.Any
    ) -> lib.t.TypeGuard[lib.t.TypeVar]:
    """Return `True` if obj is a `TypeVar`."""

    return isinstance(obj, lib.t.TypeVar)


def is_union(
    obj: lib.t.Any
    ) -> lib.t.TypeGuard[lib.lib.types.UnionType]:
    """Return `True` if obj is a `UnionType`."""

    return isinstance(obj, (typ.UnionGenericAlias, lib.types.UnionType))


@lib.t.overload
def is_bool_type(
    tp: type[typ.AnyType]
    ) -> lib.t.TypeGuard[type[typ.AnyType]]: ...
@lib.t.overload
def is_bool_type(
    tp: type[lib.t.Any] | lib.t.Any
    ) -> lib.t.TypeGuard[type[bool]]: ...
def is_bool_type(
    tp: type[typ.AnyType] | type[lib.t.Any] | lib.t.Any
    ) -> lib.t.TypeGuard[lib.t.Union[type[bool], type[typ.AnyType]]]:
    """Return `True` if `tp` is `type[bool]`."""

    otps = get_checkable_types(tp)

    if otps:
        return issubclass(otps[0], bool)
    else:
        return False


@lib.t.overload
def is_number_type(
    tp: type[typ.NumberType]
    ) -> lib.t.TypeGuard[type[typ.NumberType]]: ...
@lib.t.overload
def is_number_type(
    tp: type[lib.t.Any] | lib.t.Any
    ) -> lib.t.TypeGuard[type[lib.numbers.Number]]: ...
def is_number_type(
    tp: type[typ.NumberType] | type[lib.t.Any] | lib.t.Any
    ) -> lib.t.TypeGuard[type[lib.numbers.Number] | type[typ.NumberType]]:
    """Return `True` if tp is `numbers.Number`."""

    otps = get_checkable_types(tp)

    if otps:
        return issubclass(tp, get_checkable_types(lib.numbers.Number))
    else:
        return False


def is_ellipsis(
    tp: type[lib.t.Any] | lib.t.Any
    ) -> lib.t.TypeGuard[lib.types.EllipsisType]:
    """Return `True` if `tp` is `[...]`."""

    otps = get_checkable_types(type(tp))

    if otps:
        return issubclass(otps[0], lib.types.EllipsisType)
    else:  # pragma: no cover
        return False


def is_literal(
    tp: type[lib.t.Any] | lib.t.Any
    ) -> lib.t.TypeGuard[typ.Literal]:
    """Return `True` if `tp` is a `Literal`."""

    otp = lib.t.get_origin(tp) or tp

    return (
        getattr(otp, '__name__', '') == 'Literal'
        and getattr(otp, '__module__', '') == 'typing'
        )


def is_date_type(
    tp: type[lib.t.Any] | lib.t.Any,
    ) -> lib.t.TypeGuard[type[lib.datetime.date]]:
    """Return `True` if `tp` is `datetime.date`."""

    otps = get_checkable_types(tp)

    if otps:
        return issubclass(otps[0], lib.datetime.date)
    else:
        return False


def is_datetime_type(
    tp: type[lib.t.Any] | lib.t.Any,
    ) -> lib.t.TypeGuard[type[lib.datetime.datetime]]:
    """Return `True` if `tp` is `datetime.datetime`."""

    otps = get_checkable_types(tp)

    if otps:
        return issubclass(otps[0], lib.datetime.datetime)
    else:
        return False


def is_none_type(
    tp: type[lib.t.Any] | lib.t.Any,
    ) -> lib.t.TypeGuard[type[typ.NoneType]]:
    """Return `True` if `tp` is `NoneType`."""

    otps = get_checkable_types(tp)

    if otps:
        return issubclass(otps[0], None.__class__)
    else:
        return False


def is_primitive(
    obj: lib.t.Any
    ) -> lib.t.TypeGuard[typ.Primitive]:
    """Return `True` if `obj` is a `Primitive`."""

    return isinstance(obj, get_checkable_types(typ.Primitive))


def is_serialized_mapping(
    obj: lib.t.Any | type[lib.t.Any]
    ) -> lib.t.TypeGuard['typ.Mapping[typ.Primitive, typ.Serial]']:
    """
    Return `True` if `obj` is `MappingProto[typ.Primitive, typ.Serial]`.

    """

    return (
        isinstance(obj, lib.t.Mapping)
        and all(
            (
                is_primitive(k)
                and isinstance(v, get_checkable_types(typ.Serial))
                )
            for k, v
            in obj.items()
            )
        )


def is_mapping(
    obj: typ.MappingType | lib.t.Any
    ) -> lib.t.TypeGuard[
        typ.MappingType
        | 'typ.Mapping[lib.t.Any, lib.t.Any]'
        ]:
    """Return `True` if `obj` is `Mapping[lib.t.Any, lib.t.Any]`."""

    return isinstance(obj, lib.t.Mapping)


def is_mapping_type(
    tp: type[typ.MappingType] | type[lib.t.Any] | lib.t.Any
    ) -> lib.t.TypeGuard[type[typ.MappingType]]:
    """Return `True` if `tp` is `type[Mapping[lib.t.Any, lib.t.Any]]`."""

    otps = get_checkable_types(tp)

    if otps:
        return issubclass(otps[0], lib.t.Mapping)
    else:
        return False


@lib.t.overload
def is_array(
    obj: 'typ.Array[typ.AnyType]',
    ) -> lib.t.TypeGuard['typ.Array[typ.AnyType]']: ...
@lib.t.overload
def is_array(
    obj: lib.t.Any,
    ) -> lib.t.TypeGuard['typ.Array[lib.t.Any]']: ...
def is_array(
    obj: 'typ.Array[typ.AnyType | lib.t.Any] | lib.t.Any'
    ) -> lib.t.TypeGuard['typ.Array[typ.AnyType | lib.t.Any]']:
    """Return `True` if `obj` is `Array[lib.t.Any]`."""

    return (
        isinstance(obj, lib.t.Collection)
        and not isinstance(obj, (str, lib.t.Mapping))
        )


def is_array_type(
    tp: type[typ.ArrayType] | type[lib.t.Any] | lib.t.Any
    ) -> lib.t.TypeGuard[type[typ.ArrayType]]:
    """Return `True` if `tp` is `type[Array[lib.t.Any]]`."""

    otps = get_checkable_types(tp)

    if otps:
        return (
            issubclass(otps[0], lib.t.Collection)
            and not issubclass(otps[0], (str, lib.t.Mapping))
            )
    else:
        return False


def is_variadic_array_type(
    tp: type[typ.VariadicArrayType] | type[lib.t.Any] | lib.t.Any
    ) -> lib.t.TypeGuard[type[typ.VariadicArrayType]]:
    """Return `True` if `tp` is `type[VariadicArray]`."""

    otps = get_checkable_types(tp)

    if otps:
        return issubclass(otps[0], tuple)
    else:
        return False
