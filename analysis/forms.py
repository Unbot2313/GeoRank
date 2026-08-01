from django import forms


class URLAnalysisForm(forms.Form):
    url = forms.URLField(
        max_length=500,
        widget=forms.URLInput(attrs={
            'placeholder': 'https://example.com',
            'class': (
                'w-full px-4 py-3 border border-gray-300 rounded-lg '
                'focus:ring-2 focus:ring-blue-500 focus:border-transparent '
                'outline-none transition'
            ),
        }),
    )
