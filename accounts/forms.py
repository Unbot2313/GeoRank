from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

import logging

from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse

from notifications.services.n8n import N8nNotificationError, trigger_workflow



INPUT_CLASSES = (
    'w-full px-4 py-3 bg-input text-fg placeholder:text-fg-muted border border-line rounded-lg '
    'focus:ring-2 focus:ring-brand focus:border-transparent '
    'outline-none transition'
)

logger = logging.getLogger(__name__)


class N8nPasswordResetForm(PasswordResetForm):
    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        # Sin URL de n8n: respaldo con el correo de Django (consola en desarrollo)
        if not settings.N8N_WEBHOOK_URL:
            return super().send_mail(
                subject_template_name,
                email_template_name,
                context,
                from_email,
                to_email,
                html_email_template_name,
            )

        reset_path = reverse(
            'accounts:password_reset_confirm',
            kwargs={'uidb64': context['uid'], 'token': context['token']},
        )
        reset_url = f"{context['protocol']}://{context['domain']}{reset_path}"

        try:
            trigger_workflow('password.reset', {
                'to': to_email,
                'username': context['user'].get_username(),
                'reset_url': reset_url,
                'expires_hours': settings.PASSWORD_RESET_TIMEOUT // 3600,
            })
        except N8nNotificationError:
            # No propagamos el error: la respuesta debe ser igual exista o no el correo.
            logger.exception('Could not send password reset email via n8n.')



class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'you@example.com',
            }
        ),
    )

    industry_sector = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'e.g. Insurance, Retail, Healthcare...',
            }
        ),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': 'username',
        })

        self.fields['password1'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': '••••••••',
        })

        self.fields['password2'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': '••••••••',
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

            # The post_save signal has already created the UserProfile.
            user.profile.industry_sector = self.cleaned_data['industry_sector']
            user.profile.save()

        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'username',
            }
        ),
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': INPUT_CLASSES,
                'placeholder': '••••••••',
            }
        ),
    )


class ProfileUpdateForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'username',
            }
        ),
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'you@example.com',
            }
        ),
    )

    company_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Company name',
            }
        ),
    )

    industry_sector = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Technology, Healthcare, Retail...',
            }
        ),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if user:
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email
            self.fields['company_name'].initial = user.profile.company_name
            self.fields['industry_sector'].initial = user.profile.industry_sector

    def clean_username(self):
        username = self.cleaned_data['username']

        if User.objects.exclude(pk=self.user.pk).filter(
            username=username
        ).exists():
            raise forms.ValidationError(
                'This username is already in use.'
            )

        return username

    def clean_company_name(self):
        return self.cleaned_data['company_name'].strip()

    def clean_industry_sector(self):
        return self.cleaned_data['industry_sector'].strip()

    def save(self):
        user = self.user
        profile = user.profile

        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.save()

        # Editable profile information.
        # IMPORTANT: company_name does NOT determine security membership.
        profile.company_name = self.cleaned_data['company_name']
        profile.industry_sector = self.cleaned_data['industry_sector']
        profile.save()

        return user