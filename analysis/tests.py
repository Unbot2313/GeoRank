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

class MultiAIAnalysisTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='multi_ai_user',
            email='multi-ai@example.com',
            password='TestPass123!',
        )
        self.content = {
            'title': 'Example',
            'meta_description': 'An example site',
            'headings': ['Welcome'],
            'body_text': 'Some content',
        }
        self.success_result = {
            'visibility_score': 60,
            'readability_score': 70,
            'citability_score': 50,
            'recommendations': [],
            'sector_recommendations': [],
        }

    @patch('analysis.services.pipeline.analyze_with_groq')
    @patch('analysis.services.pipeline.analyze_with_gemini')
    @patch('analysis.services.pipeline.fetch_page_content')
    def test_groq_model_is_used_when_selected(self, mock_fetch, mock_gemini, mock_groq):
        mock_fetch.return_value = self.content
        mock_groq.return_value = self.success_result

        analysis = run_analysis('https://example.com', user=self.user, ai_model='qwen')

        self.assertEqual(analysis.status, 'completed')
        self.assertEqual(analysis.ai_model, 'qwen')
        mock_gemini.assert_not_called()
        self.assertEqual(mock_groq.call_args.kwargs['model'], 'qwen')

    @patch('analysis.services.pipeline.analyze_with_groq')
    @patch('analysis.services.pipeline.analyze_with_gemini')
    @patch('analysis.services.pipeline.fetch_page_content')
    def test_gemini_is_the_default_model(self, mock_fetch, mock_gemini, mock_groq):
        mock_fetch.return_value = self.content
        mock_gemini.return_value = self.success_result

        analysis = run_analysis('https://example.com', user=self.user)

        self.assertEqual(analysis.ai_model, 'gemini')
        mock_groq.assert_not_called()

    @patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'})
    @patch('analysis.services.groq_api.requests.post')
    def test_groq_request_uses_model_id_and_parses_json(self, mock_post):
        from analysis.services.groq_api import analyze_with_groq

        mock_post.return_value.status_code = 200
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {
            'choices': [{'message': {'content': '{"visibility_score": 60}'}}],
        }

        result = analyze_with_groq(self.content, model='gpt-oss')

        self.assertEqual(result, {'visibility_score': 60})
        payload = mock_post.call_args.kwargs['json']
        self.assertEqual(payload['model'], 'openai/gpt-oss-120b')
        self.assertEqual(payload['response_format'], {'type': 'json_object'})
        self.assertEqual(mock_post.call_args.kwargs['headers']['Authorization'], 'Bearer test-key')

    @patch.dict('os.environ', {'GROQ_API_KEY': ''})
    @patch('analysis.services.pipeline.fetch_page_content')
    def test_missing_groq_key_marks_analysis_as_failed(self, mock_fetch):
        mock_fetch.return_value = self.content

        analysis = run_analysis('https://example.com', user=self.user, ai_model='gpt-oss')

        self.assertEqual(analysis.status, 'failed')
        self.assertIn('GROQ_API_KEY', analysis.error_message)

    def test_form_defaults_to_gemini_and_rejects_unknown_models(self):
        from analysis.forms import URLAnalysisForm

        form = URLAnalysisForm(data={'url': 'example.com'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['ai_model'], 'gemini')

        form = URLAnalysisForm(data={'url': 'example.com', 'ai_model': 'unknown'})
        self.assertFalse(form.is_valid())
