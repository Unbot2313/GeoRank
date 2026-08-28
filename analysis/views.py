from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import URLAnalysisForm
from .models import Analysis
from .services.pipeline import run_analysis


@login_required
def submit_url(request):
    profile = request.user.profile

    if request.method == 'POST':
        if not profile.can_run_analysis():
            messages.error(
                request,
                'Alcanzaste el límite de tu plan Free (3 análisis por día). '
                'Actualiza a Pro para hacer más análisis.',
            )

            form = URLAnalysisForm()

            return render(
                request,
                'analysis/submit.html',
                {
                    'form': form,
                    'profile': profile,
                },
            )

        form = URLAnalysisForm(request.POST)

        if form.is_valid():
            url = form.cleaned_data['url']
            analysis = run_analysis(url, user=request.user)

            return redirect(
                'analysis:result',
                pk=analysis.pk,
            )
    else:
        form = URLAnalysisForm()

    return render(
        request,
        'analysis/submit.html',
        {
            'form': form,
            'profile': profile,
        },
    )


@login_required
def analysis_result(request, pk):
    analysis = get_object_or_404(
        Analysis,
        pk=pk,
        user=request.user,
    )

    return render(
        request,
        'analysis/result.html',
        {
            'analysis': analysis,
            'general_recommendations': analysis.recommendations.exclude(category='sector'),
            'sector_recommendations': analysis.recommendations.filter(category='sector'),
        },
    )


@login_required
def analysis_history(request):
    analyses = request.user.analyses.all().order_by('-created_at')

    return render(
        request,
        'analysis/history.html',
        {'analyses': analyses},
    )


@login_required
def score_history(request, pk):
    selected_analysis = get_object_or_404(
        Analysis,
        pk=pk,
        user=request.user,
    )

    analyses = (
        Analysis.objects
        .filter(
            user=request.user,
            url=selected_analysis.url,
            status='completed',
        )
        .select_related('score')
        .order_by('-created_at')
    )

    return render(
        request,
        'analysis/score_history.html',
        {
            'selected_analysis': selected_analysis,
            'analyses': analyses,
        },
    )