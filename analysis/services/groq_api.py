import json
import os
import time

import requests

from .prompt import build_analysis_prompt

# Groq exposes several open models behind one API key (OpenAI-compatible endpoint).
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'
GROQ_MODELS = {
    'gpt-oss': 'openai/gpt-oss-120b',
    'qwen': 'qwen/qwen3.8-27b',
}

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5
REQUEST_TIMEOUT_SECONDS = 60


class GroqError(Exception):
    """The Groq API did not return a usable analysis."""


def analyze_with_groq(content: dict, industry_sector: str = '', model: str = 'gpt-oss') -> dict:
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        raise GroqError('GROQ_API_KEY is not set.')

    payload = {
        'model': GROQ_MODELS[model],
        'messages': [{'role': 'user', 'content': build_analysis_prompt(content, industry_sector)}],
        'response_format': {'type': 'json_object'},
    }
    headers = {'Authorization': f'Bearer {api_key}'}

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(GROQ_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        except requests.RequestException as e:
            last_error = GroqError(f'Could not reach Groq: {e}')
        else:
            # Rate limits and server errors are worth retrying; other errors are not.
            if response.status_code == 429 or response.status_code >= 500:
                last_error = GroqError(f'Groq returned {response.status_code}.')
            elif not response.ok:
                raise GroqError(f'Groq returned {response.status_code}: {response.text[:200]}')
            else:
                text = response.json()['choices'][0]['message']['content']
                try:
                    return json.loads(text)
                except json.JSONDecodeError as e:
                    raise GroqError('Groq did not return valid JSON.') from e

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)

    raise last_error
