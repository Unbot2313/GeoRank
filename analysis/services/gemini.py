import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

ANALYSIS_PROMPT = """You are an AI visibility analyst. A website wants to be cited by AI assistants like ChatGPT, Perplexity, and Gemini.

Analyze this website content and return ONLY a JSON object with these fields:
- visibility_score (0-100): How likely an AI is to cite this content
- readability_score (0-100): How easy the text is to understand
- citability_score (0-100): How referenceable the information is
- recommendations: Array of up to 5 objects with priority (1=high, 3=low), category ("content"/"structure"/"metadata"/"authority"), and description

Website: {title}
Description: {meta_description}
Headings: {headings}
Content: {body_text}
"""


def analyze_with_gemini(content: dict) -> dict:
    prompt = ANALYSIS_PROMPT.format(
        title=content['title'],
        meta_description=content['meta_description'],
        headings=', '.join(content['headings'][:10]),
        body_text=content['body_text'][:3000],
    )

    response = client.models.generate_content(
        model='gemini-flash-latest',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
        ),
    )

    return json.loads(response.text)
