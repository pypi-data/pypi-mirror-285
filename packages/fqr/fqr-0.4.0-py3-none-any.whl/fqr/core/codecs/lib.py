"""Codecs imports."""

from .. import lib

__all__ = (
    'collections',
    'decimal',
    'ipaddress',
    'json',
    'numbers',
    'pathlib',
    'uuid',
    *lib.__all__
    )

import collections.abc
import decimal
import ipaddress
import json
import numbers
import pathlib
import uuid

from .. lib import *
