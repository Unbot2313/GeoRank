import re

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
)
class PasswordRecoveryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='password_test_user',
            email='test@example.com',
            password='OldPassword123!',
        )

    def test_password_reset_sends_email_for_existing_user(self):
        response = self.client.post(
            reverse('accounts:password_reset'),
            {
                'email': 'test@example.com',
            },
        )

        self.assertRedirects(
            response,
            reverse('accounts:password_reset_done'),
        )

        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        self.assertEqual(
            email.subject,
            'Reset your GeoRank password',
        )

        self.assertEqual(
            email.to,
            ['test@example.com'],
        )

        self.assertIn(
            'You requested a password reset for your GeoRank account.',
            email.body,
        )

        self.assertIn(
            '/reset/',
            email.body,
        )

    def test_password_reset_does_not_reveal_unknown_email(self):
        response = self.client.post(
            reverse('accounts:password_reset'),
            {
                'email': 'unknown@example.com',
            },
        )

        self.assertRedirects(
            response,
            reverse('accounts:password_reset_done'),
        )

        self.assertEqual(len(mail.outbox), 0)

    def test_user_can_change_password_using_reset_link(self):
        self.client.post(
            reverse('accounts:password_reset'),
            {
                'email': 'test@example.com',
            },
        )

        self.assertEqual(len(mail.outbox), 1)

        email_body = mail.outbox[0].body

        match = re.search(
            r'http://testserver(?P<path>/reset/[^\s]+/)',
            email_body,
        )

        self.assertIsNotNone(match)

        reset_path = match.group('path')

        # Django first validates the token and redirects to a URL
        # containing "set-password" so the token is not kept in the URL.
        response = self.client.get(reset_path)

        self.assertEqual(response.status_code, 302)

        confirm_path = response.url

        response = self.client.post(
            confirm_path,
            {
                'new_password1': 'NewSecurePassword123!',
                'new_password2': 'NewSecurePassword123!',
            },
        )

        self.assertRedirects(
            response,
            reverse('accounts:password_reset_complete'),
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                'NewSecurePassword123!'
            )
        )

        self.assertFalse(
            self.user.check_password(
                'OldPassword123!'
            )
        )

    def test_reset_link_cannot_be_reused_after_password_change(self):
        self.client.post(
            reverse('accounts:password_reset'),
            {
                'email': 'test@example.com',
            },
        )

        email_body = mail.outbox[0].body

        match = re.search(
            r'http://testserver(?P<path>/reset/[^\s]+/)',
            email_body,
        )

        self.assertIsNotNone(match)

        reset_path = match.group('path')

        first_response = self.client.get(reset_path)

        self.assertEqual(first_response.status_code, 302)

        confirm_path = first_response.url

        self.client.post(
            confirm_path,
            {
                'new_password1': 'NewSecurePassword123!',
                'new_password2': 'NewSecurePassword123!',
            },
        )

        # Try using the original token again.
        reused_response = self.client.get(reset_path)

        self.assertEqual(reused_response.status_code, 200)

        self.assertContains(
            reused_response,
            'Invalid reset link',
        )