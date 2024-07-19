import unittest

from acq.django import discover
from django.conf import settings
from unittest import mock

settings.configure(AUTOLOAD_PACKAGES=[])

MOCK_INSTALLED_APPS = [
    'django.contrib.flatpages',
    'django.contrib.admin',
]


class DiscoveryTestCase(unittest.TestCase):
    @mock.patch('acq.discovery.discover')
    def test_discover_imports_from_installed_apps(self, base_discover):
        with mock.patch('django.conf.settings.INSTALLED_APPS',
                        MOCK_INSTALLED_APPS):
            discover('views')

        base_discover.assert_called_once_with(
            'views',
            package_names=MOCK_INSTALLED_APPS,
        )

    @mock.patch('acq.discovery.discover')
    def test_discover_imports_from_provided_setting(self, base_discover):
        with mock.patch('django.conf.settings.AUTOLOAD_PACKAGES',
                        MOCK_INSTALLED_APPS):
            discover('views', packages_setting_name='AUTOLOAD_PACKAGES')

        base_discover.assert_called_once_with(
            'views',
            package_names=MOCK_INSTALLED_APPS,
        )

    @mock.patch('acq.discovery.discover')
    def test_discover_fails_if_setting_does_not_exist(self, base_discover):
        expected_msg = (
            "module 'django.conf.global_settings' has no "
            "attribute 'NON_EXISTANT_SETTING'"
        )

        with self.assertRaises(AttributeError, msg=expected_msg):
            discover(packages_setting_name='NON_EXISTANT_SETTING')
