from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


def send_analysis_ready_email(analysis):
    if analysis.user is None:
        return

    if not analysis.user.email:
        return

    report_path = reverse(
        'analysis:result',
        args=[analysis.pk],
    )

    site_url = settings.SITE_URL.rstrip('/')
    report_url = f'{site_url}{report_path}'

    subject = 'Your GeoRank report is ready'

    message = (
        f'Hello {analysis.user.username},\n\n'
        f'Your GeoRank analysis for {analysis.url} is ready.\n\n'
        f'View your report:\n'
        f'{report_url}\n\n'
        f'GeoRank'
    )

    send_mail(
        subject='Your GeoRank report is ready',
        message=(
            f'Hello {analysis.user.username},\n\n'
            f'Your GeoRank analysis for {analysis.url} is ready.\n\n'
            f'View your report:\n{report_url}\n\nGeoRank'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[analysis.user.email],
        fail_silently=False,
    )