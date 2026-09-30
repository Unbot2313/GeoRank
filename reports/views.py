from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from analysis.views import accessible_reports

from .services.pdf import build_analysis_pdf


@login_required
def export_pdf(request, pk):
    analysis = get_object_or_404(
        accessible_reports(request.user).select_related('score'),
        pk=pk,
        status='completed',
    )

    pdf = build_analysis_pdf(analysis)

    response = HttpResponse(
        pdf,
        content_type='application/pdf',
    )

    response['Content-Disposition'] = (
        f'attachment; filename="georank-report-{analysis.pk}.pdf"'
    )

    return response