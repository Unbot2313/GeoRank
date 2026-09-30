from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse

from .forms import CompetitorForm, URLAnalysisForm
from .models import Analysis, Competitor
from .services.pipeline import run_analysis


def accessible_reports(user):
    """
    Return the reports that the authenticated user is allowed to access.

    If the user belongs to a company, they can access reports created by
    any member of that same company.

    If the user has no company assigned, they can only access their own
    reports. This prevents users with company=NULL from sharing access.
    """
    reports = Analysis.objects.filter(
        competitor__isnull=True,
    )

    if user.profile.company_id:
        return reports.filter(
            user__profile__company_id=user.profile.company_id,
        )

    return reports.filter(user=user)


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
            analysis = run_analysis(
                url,
                user=request.user,
            )

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
        accessible_reports(request.user),
        pk=pk,
    )

    return render(
        request,
        'analysis/result.html',
        {
            'analysis': analysis,
            'general_recommendations': analysis.recommendations.exclude(
                category='sector',
            ),
            'sector_recommendations': analysis.recommendations.filter(
                category='sector',
            ),
        },
    )



@login_required
def analysis_history(request):
    analyses = (
        accessible_reports(request.user)
        .select_related(
            'user',
            'user__profile',
        )
        .order_by('-created_at')
    )

    return render(
        request,
        'analysis/history.html',
        {
            'analyses': analyses,
        },
    )


@login_required
def score_history(request, pk):
    selected_analysis = get_object_or_404(
        accessible_reports(request.user),
        pk=pk,
    )

    analyses = (
        accessible_reports(request.user)
        .filter(
            url=selected_analysis.url,
            status='completed',
        )
        .select_related(
            'score',
            'user',
            'user__profile',
        )
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
    competitor_count = request.user.competitors.count()
    limit_reached = competitor_count >= Competitor.MAX_PER_USER

    if request.method == 'POST':
        if limit_reached:
            messages.error(
                request,
                'You reached the limit of '
                f'{Competitor.MAX_PER_USER} competitors.',
            )

            return redirect('analysis:competitors')

        form = CompetitorForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():
            try:
                competitor = Competitor.objects.create(
                    user=request.user,
                    name=form.cleaned_data['name'],
                    url=form.cleaned_data['url'],
                )

            except IntegrityError:
                form.add_error(
                    'url',
                    'You already registered this competitor.',
                )

            else:
                analysis = run_analysis(
                    competitor.url,
                    user=request.user,
                    competitor=competitor,
                )

                if analysis.status == 'failed':
                    messages.warning(
                        request,
                        'Competitor registered, but we could not '
                        'analyze its site yet.',
                    )
                else:
                    messages.success(
                        request,
                        'Competitor registered and analyzed.',
                    )

                return redirect('analysis:competitors')
    else:
        form = CompetitorForm(
            user=request.user,
        )

    competitors = [
        {
            'competitor': competitor,
            'analysis': competitor.latest_analysis(),
        }
        for competitor in request.user.competitors.all()
    ]

    return render(
        request,
        'analysis/competitors.html',
        {
            'form': form,
            'competitors': competitors,
            'competitor_count': competitor_count,
            'competitor_limit': Competitor.MAX_PER_USER,
            'limit_reached': limit_reached,
        },
    )


@login_required
def comparison(request, pk):
    analysis = get_object_or_404(
        accessible_reports(request.user),
        pk=pk,
    )

    rows = [
        {
            'name': 'Your website',
            'url': analysis.url,
            'score': (
                analysis.score.visibility_score
                if hasattr(analysis, 'score')
                else None
            ),
            'is_own': True,
        }
    ]

    # Use the competitors associated with the owner of the report.
    # This also works when another member of the same company
    # accesses the report.
    competitors = list(
        analysis.user.competitors.all()
    )

    for competitor in competitors:
        latest = competitor.latest_analysis()

        rows.append(
            {
                'name': str(competitor),
                'url': competitor.url,
                'score': (
                    latest.score.visibility_score
                    if latest
                    else None
                ),
                'is_own': False,
            }
        )

    ranked = sorted(
        [
            row
            for row in rows
            if row['score'] is not None
        ],
        key=lambda row: row['score'],
        reverse=True,
    )

    unscored = [
        row
        for row in rows
        if row['score'] is None
    ]

    return render(
        request,
        'analysis/comparison.html',
        {
            'analysis': analysis,
            'ranked': ranked,
            'unscored': unscored,
            'has_competitors': bool(competitors),
        },
    )