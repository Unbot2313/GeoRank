from ..models import Analysis, Score, Recommendation
from .scraper import fetch_page_content
from .gemini import analyze_with_gemini


def run_analysis(url: str) -> Analysis:
    analysis = Analysis.objects.create(url=url, status='pending')

    try:
        content = fetch_page_content(url)
        analysis.raw_content = str(content)
        analysis.save()

        result = analyze_with_gemini(content)

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

        analysis.status = 'completed'
        analysis.save()

    except Exception as e:
        analysis.status = 'failed'
        analysis.error_message = str(e)
        analysis.save()

    return analysis
