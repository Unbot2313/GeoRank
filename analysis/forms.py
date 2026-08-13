from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

INPUT_CLASSES = (
    'w-full px-4 py-3 border border-gray-300 rounded-lg '
    'focus:ring-2 focus:ring-blue-500 focus:border-transparent '
    'outline-none transition'
)



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


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'you@example.com'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': INPUT_CLASSES, 'placeholder': 'username',
        })
        self.fields['password1'].widget.attrs.update({
            'class': INPUT_CLASSES, 'placeholder': '••••••••',
        })
        self.fields['password2'].widget.attrs.update({
            'class': INPUT_CLASSES, 'placeholder': '••••••••',
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'username'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': INPUT_CLASSES, 'placeholder': '••••••••'}),
    )