from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def build_analysis_pdf(analysis):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f'GeoRank Report - {analysis.url}',
        author='GeoRank',
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'GeoRankTitle',
        parent=styles['Title'],
        alignment=TA_CENTER,
        fontSize=22,
        leading=26,
        spaceAfter=18,
    )

    subtitle_style = ParagraphStyle(
        'GeoRankSubtitle',
        parent=styles['Heading2'],
        fontSize=15,
        leading=19,
        spaceBefore=14,
        spaceAfter=10,
    )

    normal_style = ParagraphStyle(
        'GeoRankNormal',
        parent=styles['BodyText'],
        fontSize=10,
        leading=15,
        spaceAfter=6,
    )

    story = []

    story.append(
        Paragraph(
            'GeoRank Analysis Report',
            title_style,
        )
    )

    story.append(
        Paragraph(
            f'<b>Website:</b> {escape(analysis.url)}',
            normal_style,
        )
    )

    story.append(
        Paragraph(
            f'<b>Analysis date:</b> '
            f'{analysis.created_at.strftime("%Y-%m-%d %H:%M")}',
            normal_style,
        )
    )

    if analysis.industry_sector:
        story.append(
            Paragraph(
                f'<b>Industry:</b> '
                f'{escape(analysis.industry_sector)}',
                normal_style,
            )
        )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            'Scores',
            subtitle_style,
        )
    )

    score = analysis.score

    score_data = [
        [
            'Visibility',
            'Readability',
            'Citability',
        ],
        [
            f'{score.visibility_score}/100',
            f'{score.readability_score}/100',
            f'{score.citability_score}/100',
        ],
    ]

    score_table = Table(
        score_data,
        colWidths=[5 * cm, 5 * cm, 5 * cm],
    )

    score_table.setStyle(
        TableStyle(
            [
                (
                    'BACKGROUND',
                    (0, 0),
                    (-1, 0),
                    colors.HexColor('#F3F4F6'),
                ),
                (
                    'TEXTCOLOR',
                    (0, 0),
                    (-1, 0),
                    colors.HexColor('#374151'),
                ),
                (
                    'ALIGN',
                    (0, 0),
                    (-1, -1),
                    'CENTER',
                ),
                (
                    'FONTNAME',
                    (0, 0),
                    (-1, 0),
                    'Helvetica-Bold',
                ),
                (
                    'FONTNAME',
                    (0, 1),
                    (-1, 1),
                    'Helvetica-Bold',
                ),
                (
                    'FONTSIZE',
                    (0, 1),
                    (-1, 1),
                    15,
                ),
                (
                    'GRID',
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor('#D1D5DB'),
                ),
                (
                    'TOPPADDING',
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    'BOTTOMPADDING',
                    (0, 0),
                    (-1, -1),
                    10,
                ),
            ]
        )
    )

    story.append(score_table)

    general_recommendations = analysis.recommendations.exclude(
        category='sector'
    )

    story.append(
        Paragraph(
            'Recommendations',
            subtitle_style,
        )
    )

    if general_recommendations.exists():
        for recommendation in general_recommendations:
            priority = recommendation.get_priority_display()

            story.append(
                Paragraph(
                    f'<b>{escape(priority)} - '
                    f'{escape(recommendation.category.title())}</b>',
                    normal_style,
                )
            )

            story.append(
                Paragraph(
                    escape(recommendation.description),
                    normal_style,
                )
            )

            story.append(Spacer(1, 5))
    else:
        story.append(
            Paragraph(
                'No recommendations were generated.',
                normal_style,
            )
        )

    sector_recommendations = analysis.recommendations.filter(
        category='sector'
    )

    if sector_recommendations.exists():
        story.append(
            Paragraph(
                'Industry Recommendations',
                subtitle_style,
            )
        )

        for recommendation in sector_recommendations:
            priority = recommendation.get_priority_display()

            story.append(
                Paragraph(
                    f'<b>{escape(priority)}</b>',
                    normal_style,
                )
            )

            story.append(
                Paragraph(
                    escape(recommendation.description),
                    normal_style,
                )
            )

            story.append(Spacer(1, 5))

    story.append(Spacer(1, 18))

    story.append(
        Paragraph(
            'Generated by GeoRank - Generative Engine Optimization',
            ParagraphStyle(
                'Footer',
                parent=styles['BodyText'],
                alignment=TA_CENTER,
                fontSize=8,
                textColor=colors.HexColor('#6B7280'),
            ),
        )
    )

    document.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf