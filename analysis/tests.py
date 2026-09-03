from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Company
from analysis.models import Analysis, Competitor, Recommendation, Score

from unittest.mock import patch

from django.core import mail
from django.test import override_settings

from analysis.services.pipeline import run_analysis


class CompanyReportAccessTests(TestCase):
    def setUp(self):
        self.company_a = Company.objects.create(name='Company A')
        self.company_b = Company.objects.create(name='Company B')

        self.user_a1 = User.objects.create_user(
            username='user_a1',
            password='TestPass123!',
        )
        self.user_a2 = User.objects.create_user(
            username='user_a2',
            password='TestPass123!',
        )
        self.user_b1 = User.objects.create_user(
            username='user_b1',
            password='TestPass123!',
        )

        self.user_a1.profile.company = self.company_a
        self.user_a1.profile.save()

        self.user_a2.profile.company = self.company_a
        self.user_a2.profile.save()

        self.user_b1.profile.company = self.company_b
        self.user_b1.profile.save()

        self.analysis_a1 = Analysis.objects.create(
            user=self.user_a1,
            url='https://company-a.com',
            status='completed',
        )

        self.analysis_b1 = Analysis.objects.create(
            user=self.user_b1,
            url='https://company-b.com',
            status='completed',
        )

    def test_user_can_access_own_company_report(self):
        self.client.login(
            username='user_a1',
            password='TestPass123!',
        )

        response = self.client.get(
            reverse(
                'analysis:result',
                args=[self.analysis_a1.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_user_can_access_report_from_another_member_of_same_company(self):
        self.client.login(
            username='user_a2',
            password='TestPass123!',
        )

        response = self.client.get(
            reverse(
                'analysis:result',
                args=[self.analysis_a1.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_user_cannot_access_report_from_another_company(self):
        self.client.login(
            username='user_b1',
            password='TestPass123!',
        )

        response = self.client.get(
            reverse(
                'analysis:result',
                args=[self.analysis_a1.pk],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_user_without_company_only_sees_own_reports(self):
        user_without_company = User.objects.create_user(
            username='no_company',
            password='TestPass123!',
        )

        own_analysis = Analysis.objects.create(
            user=user_without_company,
            url='https://no-company.com',
            status='completed',
        )

        self.client.login(
            username='no_company',
            password='TestPass123!',
        )

        own_response = self.client.get(
            reverse(
                'analysis:result',
                args=[own_analysis.pk],
            )
        )

        other_response = self.client.get(
            reverse(
                'analysis:result',
                args=[self.analysis_a1.pk],
            )
        )

        self.assertEqual(own_response.status_code, 200)
        self.assertEqual(other_response.status_code, 404)

@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    SITE_URL='http://testserver',
    DEFAULT_FROM_EMAIL='GeoRank <noreply@georank.local>',
)
class AnalysisEmailNotificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='email_test_user',
            email='email-test@example.com',
            password='TestPass123!',
        )

        self.success_result = {
            'visibility_score': 80,
            'readability_score': 75,
            'citability_score': 70,
            'recommendations': [],
            'sector_recommendations': [],
        }

    @patch(
        'analysis.services.pipeline.analyze_with_gemini'
    )
    @patch(
        'analysis.services.pipeline.fetch_page_content'
    )
    def test_completed_analysis_sends_email(
        self,
        mock_fetch,
        mock_gemini,
    ):
        mock_fetch.return_value = {
            'text': 'Test content',
        }
        mock_gemini.return_value = self.success_result

        analysis = run_analysis(
            'https://example.com',
            user=self.user,
        )

        self.assertEqual(
            analysis.status,
            'completed',
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        email = mail.outbox[0]

        self.assertEqual(
            email.subject,
            'Your GeoRank report is ready',
        )

        self.assertEqual(
            email.to,
            ['email-test@example.com'],
        )

        self.assertIn(
            'https://example.com',
            email.body,
        )

        report_path = reverse(
            'analysis:result',
            args=[analysis.pk],
        )

        self.assertIn(
            f'http://testserver{report_path}',
            email.body,
        )

    @patch(
        'analysis.services.pipeline.fetch_page_content'
    )
    def test_failed_analysis_does_not_send_email(
        self,
        mock_fetch,
    ):
        mock_fetch.side_effect = Exception(
            'Scraping failed'
        )

        analysis = run_analysis(
            'https://example.com',
            user=self.user,
        )

        self.assertEqual(
            analysis.status,
            'failed',
        )

        self.assertEqual(
            len(mail.outbox),
            0,
        )

    @patch(
        'analysis.services.pipeline.analyze_with_gemini'
    )
    @patch(
        'analysis.services.pipeline.fetch_page_content'
    )
    def test_competitor_analysis_does_not_send_email(
        self,
        mock_fetch,
        mock_gemini,
    ):
        mock_fetch.return_value = {
            'text': 'Competitor content',
        }
        mock_gemini.return_value = self.success_result

        competitor = Competitor.objects.create(
            user=self.user,
            name='Competitor Test',
            url='https://competitor.com',
        )

        analysis = run_analysis(
            competitor.url,
            user=self.user,
            competitor=competitor,
        )

        self.assertEqual(
            analysis.status,
            'completed',
        )

        self.assertEqual(
            len(mail.outbox),
            0,
        )

    @patch(
        'analysis.services.pipeline.send_analysis_ready_email'
    )
    @patch(
        'analysis.services.pipeline.analyze_with_gemini'
    )
    @patch(
        'analysis.services.pipeline.fetch_page_content'
    )
    def test_email_failure_does_not_fail_analysis(
        self,
        mock_fetch,
        mock_gemini,
        mock_send_email,
    ):
        mock_fetch.return_value = {
            'text': 'Test content',
        }
        mock_gemini.return_value = self.success_result

        mock_send_email.side_effect = Exception(
            'SMTP unavailable'
        )

        analysis = run_analysis(
            'https://example.com',
            user=self.user,
        )

        self.assertEqual(
            analysis.status,
            'completed',
        )

        self.assertTrue(
            hasattr(analysis, 'score')
        )

        mock_send_email.assert_called_once_with(
            analysis
        )

class PdfExportTests(TestCase):
    def setUp(self):
        self.company_a = Company.objects.create(
            name='PDF Company A',
        )

        self.company_b = Company.objects.create(
            name='PDF Company B',
        )

        self.user_a1 = User.objects.create_user(
            username='pdf_user_a1',
            email='pdf-a1@example.com',
            password='TestPass123!',
        )

        self.user_a2 = User.objects.create_user(
            username='pdf_user_a2',
            email='pdf-a2@example.com',
            password='TestPass123!',
        )

        self.user_b1 = User.objects.create_user(
            username='pdf_user_b1',
            email='pdf-b1@example.com',
            password='TestPass123!',
        )

        self.user_a1.profile.company = self.company_a
        self.user_a1.profile.save()

        self.user_a2.profile.company = self.company_a
        self.user_a2.profile.save()

        self.user_b1.profile.company = self.company_b
        self.user_b1.profile.save()

        self.analysis = Analysis.objects.create(
            user=self.user_a1,
            url='https://example.com',
            status='completed',
            industry_sector='Technology',
        )

        Score.objects.create(
            analysis=self.analysis,
            visibility_score=85,
            readability_score=78,
            citability_score=82,
        )

        Recommendation.objects.create(
            analysis=self.analysis,
            priority=1,
            category='content',
            description='Improve the clarity of important website content.',
        )

        Recommendation.objects.create(
            analysis=self.analysis,
            priority=2,
            category='sector',
            description='Add more industry-specific terminology.',
        )

    def test_authorized_user_can_download_pdf(self):
        self.client.login(
            username='pdf_user_a1',
            password='TestPass123!',
        )

        response = self.client.get(
            reverse(
                'analysis:export_pdf',
                args=[self.analysis.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response['Content-Type'],
            'application/pdf',
        )

        self.assertEqual(
            response['Content-Disposition'],
            f'attachment; filename="georank-report-{self.analysis.pk}.pdf"',
        )

        self.assertTrue(
            response.content.startswith(b'%PDF'),
        )

    def test_same_company_member_can_download_pdf(self):
        self.client.login(
            username='pdf_user_a2',
            password='TestPass123!',
        )

        response = self.client.get(
            reverse(
                'analysis:export_pdf',
                args=[self.analysis.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response['Content-Type'],
            'application/pdf',
        )

    def test_other_company_cannot_download_pdf(self):
        self.client.login(
            username='pdf_user_b1',
            password='TestPass123!',
        )

        response = self.client.get(
            reverse(
                'analysis:export_pdf',
                args=[self.analysis.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_failed_analysis_cannot_be_exported(self):
        failed_analysis = Analysis.objects.create(
            user=self.user_a1,
            url='https://failed-example.com',
            status='failed',
            error_message='Test failure',
        )

        self.client.login(
            username='pdf_user_a1',
            password='TestPass123!',
        )

        response = self.client.get(
            reverse(
                'analysis:export_pdf',
                args=[failed_analysis.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )