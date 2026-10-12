from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

from notifications.services.n8n import trigger_workflow
from reports.services.pdf import build_analysis_pdf


def send_analysis_ready_email(analysis):
    if analysis.user is None or not analysis.user.email:
        return

    report_path = reverse('analysis:result', args=[analysis.pk])
    site_url = settings.SITE_URL.rstrip('/')
    report_url = f'{site_url}{report_path}'

    if settings.N8N_ANALYSIS_WEBHOOK_URL:
        pdf = build_analysis_pdf(analysis)
        filename = f'georank-report-{analysis.pk}.pdf'

        trigger_workflow(
            'analysis.ready',
            {
                'to': analysis.user.email,
                'username': analysis.user.username,
                'analysis_url': analysis.url,
                'report_url': report_url,
            },
            url=settings.N8N_ANALYSIS_WEBHOOK_URL,
            files={'report': (filename, pdf, 'application/pdf')},
            timeout=20,
        )
        return

    # Fallback: Django's email backend (console in development)
    subject = 'Your GeoRank report is ready'
    message = (
        f'Hello {analysis.user.username},\n\n'
        f'Your GeoRank analysis for {analysis.url} is ready.\n\n'
        f'View your report:\n'
        f'{report_url}\n\n'
        f'GeoRank'
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[analysis.user.email],
        fail_silently=False,
    )