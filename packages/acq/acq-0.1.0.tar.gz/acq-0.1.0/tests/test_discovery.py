import unittest

from acq.discovery import discover

from unittest import mock

NOT_A_MODULE = 'Not A Module'
NOT_ANOTHER_MODULE = 'Not Another Module'
NOT_YET_ANOTHER_MODULE = 'Not Yet Another Module'


class DiscoveryTestCase(unittest.TestCase):
    @mock.patch('importlib.import_module')
    def test_discover_imports_expected_module(self, import_module):
        import_module.return_value = NOT_A_MODULE

        modules = discover('example1')

        import_module.assert_called_once_with('example1')
        assert modules[0] == NOT_A_MODULE

    @mock.patch('importlib.import_module')
    def test_discover_imports_multiple_modules(self, import_module):
        import_module.side_effect = [
            NOT_A_MODULE,
            NOT_ANOTHER_MODULE,
            NOT_YET_ANOTHER_MODULE,
        ]

        modules = discover('example1', 'example2', 'example3')

        import_module.assert_has_calls(
            [
                mock.call('example1'),
                mock.call('example2'),
                mock.call('example3'),
            ]
        )

        assert modules[0] == NOT_A_MODULE
        assert modules[1] == NOT_ANOTHER_MODULE

    @mock.patch('importlib.import_module')
    def test_discover_called_with_no_modules(self, import_module):
        assert discover() == []
        assert import_module.call_count == 0

    @mock.patch('importlib.import_module')
    def test_discover_ignores_non_existant_modules(self, import_module):
        import_module.side_effect = [
            NOT_A_MODULE,
            ImportError('That is not a module.'),
            NOT_ANOTHER_MODULE,
        ]
        modules = discover('example1', 'example2', 'example3')
        assert len(modules) == 2

    @mock.patch('importlib.import_module')
    def test_discover_called_with_package_names(self, import_module):
        import_module.side_effect = [
            NOT_A_MODULE,
            NOT_ANOTHER_MODULE,
        ]
        modules = discover(package_names=['example1', 'example2'])

        assert len(modules) == 2
        assert modules[0] == NOT_A_MODULE
        assert modules[1] == NOT_ANOTHER_MODULE

    @mock.patch('importlib.import_module')
    def test_discover_called_with_package_names_and_module_names(
        self, import_module
    ):
        discover(
            'registration',
            'identification',
            package_names=['example1', 'example2'],
        )

        assert import_module.call_count == 4
        import_module.assert_has_calls(
            [
                mock.call('example1.registration'),
                mock.call('example1.identification'),
                mock.call('example2.registration'),
                mock.call('example2.identification'),
            ],
            any_order=True,
        )
