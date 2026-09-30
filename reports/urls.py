from django.urls import path

from . import views

app_name = 'reports'

urlpatterns = [
    path('<int:pk>/pdf/', views.export_pdf, name='export_pdf'),
]