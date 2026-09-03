from django.urls import path

from . import views

app_name = 'analysis'

urlpatterns = [
    path('submit/', views.submit_url, name='submit'),
    path('history/', views.analysis_history, name='history'),
    path('competitors/', views.competitor_list, name='competitors'),
    path('score-history/<int:pk>/', views.score_history, name='score_history'),
    path('compare/<int:pk>/', views.comparison, name='comparison'),

    # FR12 - PDF export
    path('<int:pk>/pdf/', views.export_pdf, name='export_pdf'),

    path('<int:pk>/', views.analysis_result, name='result'),
]