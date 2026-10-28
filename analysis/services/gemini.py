import json
import os
import time

from google import genai
from google.genai import errors
from google.genai import types

from .prompt import build_analysis_prompt

client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5


def analyze_with_gemini(content: dict, industry_sector: str = '') -> dict:
    prompt = build_analysis_prompt(content, industry_sector)

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