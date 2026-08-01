from django.shortcuts import render, redirect, get_object_or_404

from .forms import URLAnalysisForm
from .models import Analysis
from .services.pipeline import run_analysis


def submit_url(request):
    if request.method == 'POST':
        form = URLAnalysisForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            analysis = run_analysis(url)
            return redirect('analysis:result', pk=analysis.pk)
    else:
        form = URLAnalysisForm()
    return render(request, 'analysis/submit.html', {'form': form})


def analysis_result(request, pk):
    analysis = get_object_or_404(Analysis, pk=pk)
    return render(request, 'analysis/result.html', {'analysis': analysis})
