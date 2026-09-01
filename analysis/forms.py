from django import forms

from .models import Competitor


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
        max_length=500,
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
        url = self.cleaned_data['url']
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        if self.user and Competitor.objects.filter(user=self.user, url=url).exists():
            raise forms.ValidationError('You already registered this competitor.')
        return url
