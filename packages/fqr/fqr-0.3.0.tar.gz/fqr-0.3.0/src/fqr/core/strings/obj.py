"""Strings objects."""

from . import lib

__all__ = (
    'Pattern',
    )


class Pattern:
    """Compiled regex patterns."""

    SnakeToCamelReplacements = lib.re.compile(r'(_[a-z0-9])')
    """
    Matches all lower case alphanumeric characters following any \
    non-leading underscore.

    ---

    Note: match is inclusive of underscores to improve substitution \
    performance.

    """

    CamelToSnakeReplacements = lib.re.compile(
        r'[A-Z0-9]([0-9]+|[a-z]+|([0-9][a-z])+)'
        )
    """Matches all Title Case and numeric components."""

    camelCase = lib.re.compile(r'^[a-z]+((\d)|([A-Z0-9][a-z0-9]{1,128})){0,32}$')
    """
    Matches strict [lower] camelCase (i.e. RESTful casing) according to \
    the [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html#s5.3-camel-case).

    ---

    Unlike Google, does NOT allow for an optional uppercase character at \
    the end of the string.

    Strings with more than32IndividualWords or \
    withWordsLongerThan128Characters will not be matched.

    """

    snake_case = lib.re.compile(r'^[a-z0-9_]{1,4096}$')
    """
    Matches strict [lower] snake_case (i.e. python casing).

    ---

    Strings longer than 4096 characters will not be matched.

    """

    DateTime = lib.re.compile(
        r'[0-9]{4}-[0-9]{2}-[0-9]{2}'
        '('
            r'[ T][0-9]{2}:[0-9]{2}:[0-9]{2}'
            r'(\.([0-9]{1,6}))?'
        ')?'
        r'([+-][0-9]{2}:[0-9]{2})?'
        )
    """
    Matches valid python `datetime` strings.

    ---

    Note: validity is determined by parsability `fromisoformat()`.

    """

    Number = lib.re.compile(
        '^'
        '('
            r'[+-]?'
            r'([0-9](_?[0-9]){0,63})?'
            r'(\.)?'
            r'[0-9](_?[0-9]){0,63}'
            r'(e[+-]?[0-9](_?[0-9]){0,63})?'
        ')'
        '('
            'j'
            '|'
            '('
                r'[+-]'
                r'([0-9](_?[0-9]){0,63})?'
                r'(\.)?'
                r'[0-9](_?[0-9]){0,63}'
                r'(e[+-]?[0-9](_?[0-9]){0,63})?'
                'j'
            ')'
        ')?'
        '$'
        )
    """
    Matches integers, floats, scientific notation, and complex numbers.

    ---

    Supports precision up to 64 digits either side of a decimal point.

    Recognizes valid, pythonic underscore usage as well.

    """
