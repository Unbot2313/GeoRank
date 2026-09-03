import logging

from ..models import Analysis, Recommendation, Score
from .email import send_analysis_ready_email
from .gemini import analyze_with_gemini
from .scraper import fetch_page_content


logger = logging.getLogger(__name__)


def run_analysis(url: str, user=None, competitor=None) -> Analysis:
    industry_sector = ''

    if user is not None and hasattr(user, 'profile'):
        industry_sector = user.profile.industry_sector or ''

    analysis = Analysis.objects.create(
        url=url,
        status='pending',
        user=user,
        competitor=competitor,
        industry_sector=industry_sector,
    )

    try:
        content = fetch_page_content(url)

        analysis.raw_content = str(content)
        analysis.save()

        result = analyze_with_gemini(
            content,
            industry_sector=industry_sector,
        )

        Score.objects.create(
            analysis=analysis,
            visibility_score=result['visibility_score'],
            readability_score=result['readability_score'],
            citability_score=result['citability_score'],
        )

        for rec in result.get('recommendations', []):
            Recommendation.objects.create(
                analysis=analysis,
                priority=rec['priority'],
                category=rec['category'],
                description=rec['description'],
            )

        for rec in result.get('sector_recommendations', []):
            Recommendation.objects.create(
                analysis=analysis,
                priority=rec['priority'],
                category='sector',
                description=rec['description'],
            )

        analysis.status = 'completed'
        analysis.save()

    except Exception as exc:
        analysis.status = 'failed'
        analysis.error_message = str(exc)
        analysis.save()

        return analysis

    # FR17:
    # Notify only when the main website analysis finishes successfully.
    # Competitor analyses do not generate notification emails.
    if competitor is None:
        try:
            send_analysis_ready_email(analysis)
        except Exception:
            logger.exception(
                'Could not send analysis-ready email for analysis %s.',
                analysis.pk,
            )

    return analysis