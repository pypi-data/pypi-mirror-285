"""Module exceptions unit tests."""

import pickle
import unittest

import fqr

from . import cns


class Constants(cns.Constants):
    """Constant values specific to unit tests in this file."""


class TestExceptions(unittest.TestCase):
    """Fixture for testing."""

    def test_01_serialization(self):
        """Test multi-arg exc serializes correctly."""

        exc = fqr.core.strings.exc.StringCasingError(
            Constants.INVALID_STRING_CASING_EXAMPLE,
            fqr.core.strings.typ.camelCase
            )
        dump = pickle.dumps(exc)
        deserialized_exc: fqr.core.strings.exc.StringCasingError = (
            pickle.loads(dump)
            )
        self.assertTupleEqual(exc.args, deserialized_exc.args)
