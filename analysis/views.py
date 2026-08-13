from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .forms import URLAnalysisForm, RegisterForm, LoginForm
from .models import Analysis
from .services.pipeline import run_analysis


def register_view(request):
    if request.user.is_authenticated:
        return redirect('analysis:submit')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cuenta creada correctamente.')
            return redirect('analysis:submit')
    else:
        form = RegisterForm()
    return render(request, 'analysis/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('analysis:submit')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('analysis:submit')
            form.add_error(None, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, 'analysis/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('analysis:login')


@login_required
def submit_url(request):
    profile = request.user.profile

    if request.method == 'POST':
        if not profile.can_run_analysis():
            messages.error(
                request,
                'Alcanzaste el límite de tu plan Free (1 análisis por día). '
                'Actualiza a Pro para hacer más análisis.',
            )
            form = URLAnalysisForm()
            return render(request, 'analysis/submit.html', {'form': form, 'profile': profile})

        form = URLAnalysisForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            analysis = run_analysis(url, user=request.user)
            return redirect('analysis:result', pk=analysis.pk)
    else:
        form = URLAnalysisForm()
    return render(request, 'analysis/submit.html', {'form': form, 'profile': profile})


@login_required
def analysis_result(request, pk):
    analysis = get_object_or_404(Analysis, pk=pk, user=request.user)
    return render(request, 'analysis/result.html', {'analysis': analysis})


@login_required
def analysis_history(request):
    analyses = request.user.analyses.all().order_by('-created_at')
    return render(request, 'analysis/history.html', {'analyses': analyses})


@login_required
def profile_view(request):
    return render(request, 'analysis/profile.html', {'profile': request.user.profile})