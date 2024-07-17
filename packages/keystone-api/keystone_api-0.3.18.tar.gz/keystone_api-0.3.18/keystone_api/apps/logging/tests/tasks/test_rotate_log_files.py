"""Tests for the `rotate_log_files` task."""

from time import sleep

from django.test import override_settings, TestCase

from apps.logging.models import *
from apps.logging.tasks import rotate_log_files


class LogFileDeletion(TestCase):
    """Test the deletion of log records"""

    def create_dummy_records(self) -> None:
        """Create a single record in each logging database table"""

        AppLog.objects.create(
            name='mock.log.test',
            level=10,
            pathname='/test',
            lineno=100,
            message='This is a log'
        )
        RequestLog.objects.create(
            endpoint='/api',
            response_code=200,
            body_request='',
            body_response=''
        )

    @override_settings(LOG_RECORD_ROTATION=4)
    def test_log_files_rotated(self) -> None:
        """Test expired log files are deleted"""

        # Create a set of older and younger records
        self.create_dummy_records()
        sleep(2)
        self.create_dummy_records()

        # Make sure records exist
        self.assertEqual(2, AppLog.objects.count())
        self.assertEqual(2, RequestLog.objects.count())

        # Wait for first set of records to expire
        # Assert only the expired records are removed
        sleep(2)
        rotate_log_files()
        self.assertEqual(1, AppLog.objects.count())
        self.assertEqual(1, RequestLog.objects.count())

    @override_settings(LOG_RECORD_ROTATION=0)
    def test_rotation_disabled(self) -> None:
        """Test log files are not deleted when rotation is disabled"""

        self.create_dummy_records()

        rotate_log_files()
        self.assertEqual(1, AppLog.objects.count())
        self.assertEqual(1, RequestLog.objects.count())
