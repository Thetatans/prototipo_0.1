from django.urls import path
from . import views

urlpatterns = [
    path('', views.status_check, name='status_check'),
    path('health/', views.health_check, name='health_check'),
    path('version/', views.version_info, name='version_info'),
    path('database/', views.database_status, name='database_status'),
]