import acq
import unittest


class PublishingTestCase(unittest.TestCase):
    def test_name_is_correct(self):
        assert acq.name() == 'acq'

    def test_version_is_correct(self):
        assert acq.version_string() == '.'.join(
            map(
                str, [
                    acq.__version__[0],
                    acq.__version__[1],
                    acq.__version__[2],
                ]
            )
        )

    def test_version_string_with_release(self):
        new_version = (0, 0, 1, 'a0')
        assert acq.version_string(new_version) == '0.0.1-a0'

    def test_long_description_is_non_empty(self):
        assert len(acq.long_description().strip())

    def test_short_description_is_non_empty(self):
        assert len(acq.short_description().strip())
