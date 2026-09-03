import json
import os
import time

from google import genai
from google.genai import errors
from google.genai import types

client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5

ANALYSIS_PROMPT = """You are an AI visibility analyst. A website wants to be cited by AI assistants like ChatGPT, Perplexity, and Gemini.

The website belongs to the "{industry_sector}" industry sector. Take that into account when scoring: weigh the criteria that matter most for that specific sector (for example, an insurance site benefits from clear policy details and trust signals; a retail or shopping center site benefits from up-to-date listings and local information). If the sector is "unspecified", score generically without sector bias.

Analyze this website content and return ONLY a JSON object with these fields:
- visibility_score (0-100): How likely an AI is to cite this content
- readability_score (0-100): How easy the text is to understand
- citability_score (0-100): How referenceable the information is
- recommendations: Array of up to 5 objects with priority (1=high, 3=low), category ("content"/"structure"/"metadata"/"authority"), and description
- sector_recommendations: Array of up to 3 objects with priority (1=high, 3=low) and description, containing recommendations specialized for the "{industry_sector}" sector. If the sector is "unspecified", return an empty array.

Website: {title}
Description: {meta_description}
Headings: {headings}
Content: {body_text}
"""


def analyze_with_gemini(content: dict, industry_sector: str = '') -> dict:
    prompt = ANALYSIS_PROMPT.format(
        title=content['title'],
        meta_description=content['meta_description'],
        headings=', '.join(content['headings'][:10]),
        body_text=content['body_text'][:3000],
        industry_sector=industry_sector.strip() or 'unspecified',
    )

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                ),
            )
            return json.loads(response.text)

        except errors.ServerError as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)

    raise last_error