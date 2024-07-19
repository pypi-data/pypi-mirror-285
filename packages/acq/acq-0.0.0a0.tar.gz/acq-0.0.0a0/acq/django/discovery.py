from django.conf import settings

from acq import discovery

DEFAULT_MODULES_SETTING_NAME = 'INSTALLED_APPS'


def discover(
    *module_names: str,
    packages_setting_name: str = DEFAULT_MODULES_SETTING_NAME,
):
    """ Discover modules from packages listed in INSTALLED_APPS

    Provides a function to detect modules within INSTALLED_APPS or a given
    setting name. When provided, the setting with a name matching
    packages_setting_name will be searched instead of INSTALLED_APPS.

    TODO: Add support for AppConfig

    """

    packages = getattr(settings, packages_setting_name, [])
    return discovery.discover(*module_names, package_names=packages)
