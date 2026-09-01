from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CompetitorForm, URLAnalysisForm
from .models import Analysis, Competitor
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
    analyses = (
        request.user.analyses
        .filter(competitor__isnull=True)
        .order_by('-created_at')
    )

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
            competitor__isnull=True,
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

@login_required
def competitor_list(request):
    if request.method == 'POST':
        form = CompetitorForm(request.POST, user=request.user)

        if form.is_valid():
            competitor = Competitor.objects.create(
                user=request.user,
                name=form.cleaned_data['name'],
                url=form.cleaned_data['url'],
            )
            run_analysis(
                competitor.url,
                user=request.user,
                competitor=competitor,
            )
            messages.success(request, 'Competitor registered and analyzed.')

            return redirect('analysis:competitors')
    else:
        form = CompetitorForm(user=request.user)

    competitors = [
        {'competitor': c, 'analysis': c.latest_analysis()}
        for c in request.user.competitors.all()
    ]

    return render(
        request,
        'analysis/competitors.html',
        {
            'form': form,
            'competitors': competitors,
        },
    )


@login_required
def comparison(request, pk):
    analysis = get_object_or_404(
        Analysis,
        pk=pk,
        user=request.user,
        competitor__isnull=True,
    )

    rows = [{
        'name': 'Your website',
        'url': analysis.url,
        'score': analysis.score.visibility_score if hasattr(analysis, 'score') else None,
        'is_own': True,
    }]

    for competitor in request.user.competitors.all():
        latest = competitor.latest_analysis()
        rows.append({
            'name': str(competitor),
            'url': competitor.url,
            'score': latest.score.visibility_score if latest else None,
            'is_own': False,
        })

    ranked = sorted(
        [r for r in rows if r['score'] is not None],
        key=lambda r: r['score'],
        reverse=True,
    )
    unscored = [r for r in rows if r['score'] is None]

    return render(
        request,
        'analysis/comparison.html',
        {
            'analysis': analysis,
            'ranked': ranked,
            'unscored': unscored,
        },
    )
