"""Docs enumerations."""

__all__ = (
    'NoCrawlPath',
    'SiteMapChangeFreq',
    'SupportedTheme',
    )

from . import lib


class SiteMapChangeFreq(lib.enum.Enum):
    """Valid site map change frequencies."""

    daily = 'daily'
    weekly = 'weekly'
    monthly = 'monthly'


class SupportedTheme(lib.enum.Enum):
    """Valid sphinx docs themes."""

    agogo = 'agogo'
    alabaster = 'alabaster'
    bizstyle = 'bizstyle'
    classic = 'classic'
    haiku = 'haiku'
    nature = 'nature'
    pyramid = 'pyramid'
    scrolls = 'scrolls'
    sphinxdoc = 'sphinxdoc'
    traditional = 'traditional'


class NoCrawlPath(lib.enum.Enum):
    """Paths to be Disallowed in generated robots.txt files."""

    search = 'Disallow: /search/'
    api = 'Disallow: /api/'
    builds = 'Disallow: /builds/'
