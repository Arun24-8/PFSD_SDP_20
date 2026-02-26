from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-users/add/', views.add_user, name='admin_add_user'),
    path('manage-users/<int:user_id>/edit/', views.edit_user, name='admin_edit_user'),
    path('manage-users/<int:user_id>/view/', views.view_user, name='admin_view_user'),
    path('manage-users/<int:user_id>/delete/', views.delete_user, name='admin_delete_user'),
    path('reports/', views.view_reports, name='view_reports'),
    path('reports/generate/', views.generate_report, name='generate_report'),
    path('reports/export/', views.export_report, name='export_report'),
    path('security/', views.security_settings, name='security_settings'),
]
