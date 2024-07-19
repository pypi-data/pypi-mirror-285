"""Module utils unit tests."""

import unittest

import fqr

from . import cns


class Constants(cns.Constants):
    """Constant values specific to unit tests in this file."""

    VALID_CAMEL_STRING_EXAMPLES = (
        'upperSnakeCaseString100SureFift337aGood',
        '_privateValidCamelCaseString'
        )
    VALID_SNAKE_STRING_EXAMPLES = (
        'upper_snake_case_string_100_sure_fift_337a_good',
        '_snake_case_string_'
        )


class TestUtils(unittest.TestCase):
    """Fixture for testing."""

    def test_01_camel_case_check(self):
        """Test camelCase validation."""

        self.assertFalse(
            fqr.core.strings.utl.isCamelCaseString(
                Constants.VALID_CAMEL_STRING_EXAMPLES[-1]
                )
            )

    def test_02_case_conversion(self):
        """Test case conversion."""

        self.assertTrue(
            fqr.core.strings.utl.is_snake_case_iterable(
                [
                    fqr.core.strings.utl.camel_case_to_snake_case(string)
                    for string
                    in Constants.VALID_CAMEL_STRING_EXAMPLES
                    ]
                )
            )

    def test_03_str_validation(self):
        """Test case validation asserts `type[str]`."""

        self.assertRaises(
            TypeError,
            lambda: fqr.core.strings.utl.validate_casing(
                123,
                fqr.core.strings.enm.SupportedCasing.snake_case.value
                )
            )

    def test_04_case_validation(self):
        """Test case validation asserts snake casing."""

        self.assertRaises(
            fqr.core.strings.exc.StringCasingError,
            lambda: fqr.core.strings.utl.validate_casing(
                Constants.INVALID_STRING_CASING_EXAMPLE,
                fqr.core.strings.enm.SupportedCasing.snake_case.value
                )
            )

    def test_05_case_validation(self):
        """Test case validation asserts camel casing."""

        self.assertRaises(
            fqr.core.strings.exc.StringCasingError,
            lambda: fqr.core.strings.utl.validate_casing(
                Constants.INVALID_STRING_CASING_EXAMPLE,
                fqr.core.strings.enm.SupportedCasing.camelCase.value
                )
            )

    def test_06_snake_iterable_check(self):
        """Test snake_case validation."""

        self.assertTrue(
            fqr.core.strings.utl.is_snake_case_iterable(
                Constants.VALID_SNAKE_STRING_EXAMPLES
                )
            )

    def test_07_camel_iterable_check(self):
        """Test camelCase validation."""

        self.assertTrue(
            fqr.core.strings.utl.isCamelCaseIterable(
                Constants.VALID_CAMEL_STRING_EXAMPLES
                )
            )

    def test_08_get_cname(self):
        """Test cname retrieval."""

        self.assertEqual(
            fqr.core.strings.utl.cname_for(
                Constants.VALID_CAMEL_STRING_EXAMPLES[-1].strip('_'),
                Constants.VALID_CAMEL_STRING_EXAMPLES
                ),
                Constants.VALID_CAMEL_STRING_EXAMPLES[-1]
            )

    def test_09_get_cname(self):
        """Test cname retrieval for a snake_case string."""

        self.assertEqual(
            fqr.core.strings.utl.cname_for(
                Constants.VALID_SNAKE_STRING_EXAMPLES[0],
                Constants.VALID_CAMEL_STRING_EXAMPLES
                ),
                Constants.VALID_CAMEL_STRING_EXAMPLES[0]
            )

    def test_10_get_cname(self):
        """Test cname retrieval negative case returns None."""

        self.assertIsNone(
            fqr.core.strings.utl.cname_for(
                Constants.INVALID_STRING_CASING_EXAMPLE,
                Constants.VALID_CAMEL_STRING_EXAMPLES
                )
            )

    def test_11_validation_success(self):
        """Test validation succeeds."""

        self.assertIsNone(
            fqr.core.strings.utl.validate_casing(
                Constants.VALID_SNAKE_STRING_EXAMPLES[0],
                fqr.core.strings.enm.SupportedCasing.snake_case.value
                )
            )
