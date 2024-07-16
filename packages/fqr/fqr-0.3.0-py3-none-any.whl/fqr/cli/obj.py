"""CLI objects."""

__all__ = (
    'parsers',
    'root_parser',
    )

from .. import __version__

from . import cns
from . import lib


class Constants(cns.Constants):
    """Constant values specific to CLI objs."""


root_parser = lib.argparse.ArgumentParser(
    description='root_parser',
    formatter_class=lib.argparse.ArgumentDefaultsHelpFormatter,
    prog='fqr',
    )
root_parser.add_argument(
    '--version',
    '-v',
    action='version',
    version=__version__,
    )

parsers = root_parser.add_subparsers(
    title='module',
    required=True,
    help='specify a module to access its commands'
    )
