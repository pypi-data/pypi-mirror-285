""" automatic acquisition of modules from packages

Provides a simple and convenient way to automatically search packages for
modules and import them without needing project files to manually import them,
which allows for automatic configuration and other useful mechanics within
projects.

"""

__all__ = (
    '__version__',
    'version_string',
    'name',
    'long_description',
    'short_description',
    'discover',
)

__version__ = (0, 0, 2)

import typing

from .discovery import discover

VersionType = typing.Tuple[int, int, int] | typing.Tuple[int, int, int, str]


def version_string(version: VersionType = __version__) -> str:
    """ Provides the version string for this project """

    version_string = '.'.join(map(str, version[:3]))

    if len(version) <= 3:
        return version_string

    return version_string + '-' + version[3]


def name() -> str:
    """ Provides the package name for this project """

    return __name__


def long_description(content: str = ' '.join(__doc__.split('\n')[1:])) -> str:
    """ Provides a human-readable description for this project """

    return content


def short_description() -> str:
    """ Provides a summarized project desription """

    return long_description(content=__doc__.split('\n', 1)[0])
