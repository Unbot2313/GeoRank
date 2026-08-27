from django.urls import path

from . import views

app_name = 'analysis'

urlpatterns = [
    path('submit/', views.submit_url, name='submit'),
    path('history/', views.analysis_history, name='history'),
    path('score-history/<int:pk>/', views.score_history, name='score_history'),
    path('<int:pk>/', views.analysis_result, name='result'),
]