import logging

from django.test import SimpleTestCase

# Create your tests here.
class LoggingInTestsTests(SimpleTestCase):
    def test_assert_logs_works_under_test_settings(self):
        """Regression: test output is silenced via LOGGING, not logging.disable(), so
        assertLogs keeps working in every app's tests."""
        with self.assertLogs('apps.core', level='WARNING') as captured:
            logging.getLogger('apps.core').warning('something happened')
        self.assertEqual(len(captured.output), 1)
        self.assertIn('something happened', captured.output[0])
