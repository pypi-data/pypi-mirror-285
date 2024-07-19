"""Module utils unit tests."""

import unittest

import fqr

from . import cns


class Constants(cns.Constants):
    """Constant values specific to unit tests in this file."""


class TestUtils(unittest.TestCase):
    """Fixture for testing."""

    def test_01_str_to_forwardref(self):
        """Test `str` to `ForwardRef` casting."""

        self.assertIsInstance(
            fqr.core.typings.utl.hint.parse_str_to_ref('int', False),
            fqr.core.lib.t.ForwardRef
            )

    def test_02_str_to_type(self):
        """Test `str` to `type` casting."""

        self.assertIs(
            fqr.core.typings.utl.hint.resolve_type(
                'int',
                globals(),
                locals()
                ),
            int
            )

    def test_03_arg_ref_handling_no_ns(self):
        """Test `ForwardRef` handling for types not yet resolvable."""

        self.assertIsInstance(
            fqr.core.typings.utl.hint.resolve_type('Unresolvable'),
            fqr.core.lib.t.ForwardRef
            )

    def test_04_arg_ref_handling(self):
        """Test `ForwardRef` handling for types with args."""

        self.assertIs(
            fqr.core.typings.utl.hint.resolve_type(
                'Mockery[tuple[int, ...]]',
                globals(),
                locals()
                ),
            Mockery[tuple[int, ...]]
            )

    def test_05_anti_is_array_type(self):
        """Test `is_array_type`."""

        self.assertFalse(fqr.core.typings.utl.check.is_array_type(None))

    def test_06_anti_is_variadic_array_type(self):
        """Test `is_variadic_array_type`."""

        self.assertFalse(
            fqr.core.typings.utl.check.is_variadic_array_type(None)
            )

    def test_07_anti_is_mapping_type(self):
        """Test `is_mapping_type`."""

        self.assertFalse(fqr.core.typings.utl.check.is_mapping_type(None))

    def test_08_anti_is_none_type(self):
        """Test `is_none_type`."""

        self.assertFalse(fqr.core.typings.utl.check.is_none_type(None))

    def test_09_anti_is_number_type(self):
        """Test `is_number_type`."""

        self.assertFalse(fqr.core.typings.utl.check.is_number_type(None))

    def test_10_anti_is_bool_type(self):
        """Test `is_bool_type`."""

        self.assertFalse(fqr.core.typings.utl.check.is_bool_type(None))

    def test_11_anti_is_datetime_type(self):
        """Test `is_datetime_type`."""

        self.assertFalse(fqr.core.typings.utl.check.is_datetime_type(None))

    def test_12_anti_is_date_type(self):
        """Test `is_date_type`."""

        self.assertFalse(fqr.core.typings.utl.check.is_date_type(None))


class Mockery(fqr.core.lib.t.Generic[fqr.core.typ.AnyType]):
    """An as yet undefined generic class for testing."""
