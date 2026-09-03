from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Company
from analysis.models import Analysis


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