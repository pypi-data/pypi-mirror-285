"""Tests for the `send_notification` function."""

from django.conf import settings
from django.core import mail
from django.test import override_settings, TestCase

from apps.notifications.models import Notification
from apps.notifications.shortcuts import send_notification
from apps.users.models import User


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EmailSending(TestCase):
    """Test sending emails via the `send_notification` function"""

    def setUp(self) -> None:
        """Send an email notification to a dummy user"""

        self.user = User.objects.create_user(
            email='test@example.com',
            username='foobar',
            first_name='Foo',
            last_name='Bar',
            password='foobar123'
        )

        self.subject = 'Test Subject'
        self.plain_text = 'This is a plain text message.'
        self.html_text = '<p>This is an HTML message.</p>'
        self.notification_type = Notification.NotificationType.general_message
        self.notification_metadata = {'key': 'value'}

        send_notification(
            self.user,
            self.subject,
            self.plain_text,
            self.html_text,
            self.notification_type,
            self.notification_metadata)

    def test_email_content(self) -> None:
        """Test an email notification is sent with the correct content"""

        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        self.assertEqual(email.subject, self.subject)
        self.assertEqual(email.body, self.plain_text)
        self.assertEqual(email.from_email, settings.EMAIL_FROM_ADDRESS)
        self.assertEqual(email.to, [self.user.email])
        self.assertEqual(email.alternatives, [(self.html_text, 'text/html')])

    def test_database_is_updated(self) -> None:
        """Test a record of the email is stored in the database"""

        notification = Notification.objects.get(user=self.user)
        self.assertEqual(notification.message, self.plain_text)
        self.assertEqual(notification.notification_type, self.notification_type)
        self.assertEqual(notification.metadata, self.notification_metadata)
