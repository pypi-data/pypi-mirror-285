"""Strings utility functions."""

__all__ = (
    'camel_case_to_snake_case',
    'cname_for',
    'is_snake_case_iterable',
    'is_snake_case_string',
    'is_valid_datetime_str',
    'is_valid_number_str',
    'isCamelCaseIterable',
    'isCamelCaseString',
    'snake_case_to_camel_case',
    'validate_casing',
    )

from . import typ
from . import enm
from . import exc
from . import lib
from . import obj


def isCamelCaseString(
    string: str
    ) -> lib.t.TypeGuard[typ.string[typ.camelCase]]:
    """
    Check if `string` is valid `camelCase`.

    ---

    Checks for strict [lower] `camelCase` (i.e. `RESTful casing`) \
    according to the [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html#s5.3-camel-case).

    Unlike Google, does *NOT* allow for an optional uppercase character \
    at the end of the `string`.

    """

    return _isCamelCaseString(string)


@lib.functools.cache
def _isCamelCaseString(string: str) -> bool:
    return bool(obj.Pattern.camelCase.match(string))


def is_snake_case_string(
    string: str
    ) -> lib.t.TypeGuard[typ.string[typ.snake_case]]:
    """
    Check if `string` is valid `snake_case`.

    ---

    Checks for strict [lower] `snake_case` (i.e. `python casing`).

    """

    return _is_snake_case_string(string)


@lib.functools.cache
def _is_snake_case_string(string: str) -> bool:
    return bool(obj.Pattern.snake_case.match(string))


@lib.functools.cache
def validate_casing(
    value: lib.t.Any,
    casing: typ.Casing
    ) -> lib.t.Optional[lib.Never]:
    """
    Assert value is `str` and of correct `Casing`.

    ---

    Raises `TypeError` if not `str`.

    Raises `StringCasingError` if `str` of incorrect `Casing`.

    """

    if not isinstance(value, str):
        raise TypeError(
            f'{value!s} is not a valid `str`.'
            )
    elif (
        casing == enm.SupportedCasing.snake_case.value
        and not is_snake_case_string(value)
        ):
        raise exc.StringCasingError(value, casing)
    elif (
        casing == enm.SupportedCasing.camelCase.value
        and not isCamelCaseString(value)
        ):
        raise exc.StringCasingError(value, casing)
    else:
        return None


@lib.functools.cache
def snake_case_to_camel_case(
    snake_case_string: typ.string[typ.snake_case]
    ) -> typ.string[typ.camelCase]:
    """Convert a valid `str[snake_case]` to `str[camelCase]`."""

    camelCaseString: typ.string[typ.camelCase] = (
        obj.Pattern.SnakeToCamelReplacements.sub(
            lambda match: match.group()[-1].upper(),
            snake_case_string
            )
        )

    return camelCaseString


@lib.functools.cache
def camel_case_to_snake_case(
    camelCaseString: typ.string[typ.camelCase]
    ) -> typ.string[typ.snake_case]:
    """Convert a valid `str[camelCase]` to `str[snake_case]`."""

    snake_case_string: typ.string[typ.snake_case] = (
        obj.Pattern.CamelToSnakeReplacements.sub(
            lambda match: '_' + match.group().lower(),
            camelCaseString
            )
        )

    return snake_case_string


def is_snake_case_iterable(
    strings: lib.t.Iterable[str]
    ) -> lib.t.TypeGuard[lib.t.Iterable[typ.string[typ.snake_case]]]:
    """
    Check if all `strings` are `str[snake_case]`.

    ---

    Ignores leading and / or trailing underscores.

    """

    return all(
        is_snake_case_string(string)
        for _string
        in strings
        if (string := _string.strip('_'))
        )


def isCamelCaseIterable(
    strings: lib.t.Iterable[str]
    ) -> lib.t.TypeGuard[lib.t.Iterable[typ.string[typ.camelCase]]]:
    """
    Check if all `strings` are `str[camelCase]`.

    ---

    Ignores leading and / or trailing underscores.

    """

    return all(
        isCamelCaseString(string)
        for _string
        in strings
        if (string := _string.strip('_'))
        )


def cname_for(
    string: str,
    container: lib.t.Container[str]
    ) -> lib.t.Optional[str]:
    """
    Get the actual, canonical name for valid `string`, as contained in \
    an arbitrary, valid `Container[str]`, agnostic of `string` casing \
    and / or underscores.

    ---

    ### Example Usage

    ```py
    d = {
        '_id': 123,
        '_meaning_of_life': 42
        }

    cname_for(d, 'id')
    '_id'

    cname_for(d, 'meaningOfLife')
    42

    ```

    """

    if (
        (k := (_k := string.strip('_'))) in container
        or (k := '_' + _k) in container
        or (k := _k + '_') in container
        or (k := '_' + _k + '_') in container
        ):
        return k
    elif (
        is_snake_case_string(string)
        and (
            (
                camel_k := (
                    _camel_k := snake_case_to_camel_case(
                        string.strip('_')
                        )
                    )
                ) in container
            or (camel_k := '_' + _camel_k) in container
            or (camel_k := _camel_k + '_') in container
            or (camel_k := '_' + _camel_k + '_') in container
            )
        ):
        return camel_k
    else:
        return None


def is_valid_number_str(
    any_str: str
    ) -> lib.t.TypeGuard[typ.string[typ.numeric]]:
    """
    Return `True` if python `str` is parsable as a valid \
    `numbers.Number`.

    """

    return bool(obj.Pattern.Number.match(any_str))


def is_valid_datetime_str(
    any_str: str
    ) -> lib.t.TypeGuard[typ.string[typ.datetime]]:
    """
    Return `True` if python `str` is parsable as a valid \
    `datetime`.

    """

    return bool(obj.Pattern.DateTime.match(any_str))
