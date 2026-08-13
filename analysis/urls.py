from django.urls import path

from . import views

app_name = 'analysis'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('submit/', views.submit_url, name='submit'),
    path('history/', views.analysis_history, name='history'),
    path('profile/', views.profile_view, name='profile'),
    path('<int:pk>/', views.analysis_result, name='result'),
]