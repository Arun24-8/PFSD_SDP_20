from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('reports/', views.view_reports, name='view_reports'),
    path('security/', views.security_settings, name='security_settings'),
]
