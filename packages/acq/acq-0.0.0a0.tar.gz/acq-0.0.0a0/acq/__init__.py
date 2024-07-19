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
)

__version__ = (0, 0, 0, 'alpha')


def version_string(version=__version__):
    """ Provides the version string for this project """

    version_string = '.'.join(map(str, version[:3]))

    if len(version) <= 3:
        return version_string

    return version_string + '-' + '-'.join(version[3:])


def name():
    """ Provides the package name for this project """

    return __name__


def long_description(content=' '.join(__doc__.split('\n')[1:])):
    """ Provides a human-readable description for this project """

    return content


def short_description():
    """ Provides a summarized project desription """

    return long_description(content=__doc__.split('\n', 1)[0])
