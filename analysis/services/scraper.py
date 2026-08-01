import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup


def fetch_page_content(url: str) -> dict:
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )
    }

    session = requests.Session()
    retries = Retry(total=2, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    response = session.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else ''

    meta_desc = ''
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_tag and meta_tag.get('content'):
        meta_desc = meta_tag['content'].strip()

    headings = []
    for level in range(1, 7):
        for h in soup.find_all(f'h{level}'):
            headings.append(h.get_text(strip=True))

    body = soup.find('body')
    body_text = body.get_text(separator=' ', strip=True) if body else ''

    structured_data = []
    for script in soup.find_all('script', type='application/ld+json'):
        if script.string:
            structured_data.append(script.string)

    return {
        'title': title,
        'meta_description': meta_desc,
        'headings': headings,
        'body_text': body_text[:5000],
        'structured_data': structured_data,
    }
