from django.urls import path

from . import views

app_name = 'analysis'

urlpatterns = [
    path('submit/', views.submit_url, name='submit'),
    path('<int:pk>/', views.analysis_result, name='result'),
]
