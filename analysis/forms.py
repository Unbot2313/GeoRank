from urllib.parse import urlparse, urlunparse

from django import forms
from django.core.validators import URLValidator

from .models import Competitor


def normalize_url(raw: str) -> str:
    """Normalise a user-supplied URL so the same site is not stored twice."""
    url = raw.strip()
    if not url.lower().startswith(('http://', 'https://')):
        url = 'https://' + url

    parsed = urlparse(url)
    if not parsed.netloc:
        raise forms.ValidationError('Enter a valid URL.')

    url = urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path.rstrip('/'),
        parsed.params,
        parsed.query,
        '',
    ))

    URLValidator()(url)
    return url


class URLAnalysisForm(forms.Form):
    url = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'placeholder': 'https://example.com',
            'class': (
                'w-full px-4 py-3 border border-gray-300 rounded-lg '
                'focus:ring-2 focus:ring-blue-500 focus:border-transparent '
                'outline-none transition'
            ),
        }),
    )

    def clean_url(self):
        url = self.cleaned_data['url']
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url

class CompetitorForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Competitor name (optional)',
            'class': (
                'w-full px-4 py-3 border border-gray-300 rounded-lg '
                'focus:ring-2 focus:ring-blue-500 focus:border-transparent '
                'outline-none transition'
            ),
        }),
    )
    url = forms.CharField(
        max_length=480,
        widget=forms.TextInput(attrs={
            'placeholder': 'https://competitor.com',
            'class': (
                'w-full px-4 py-3 border border-gray-300 rounded-lg '
                'focus:ring-2 focus:ring-blue-500 focus:border-transparent '
                'outline-none transition'
            ),
        }),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_url(self):
        url = normalize_url(self.cleaned_data['url'])
        if self.user and Competitor.objects.filter(user=self.user, url=url).exists():
            raise forms.ValidationError('You already registered this competitor.')
        return url
