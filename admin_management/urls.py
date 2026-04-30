from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('add-user/', views.add_user, name='add_user'),
    path('view-user/<int:user_id>/', views.view_user, name='view_user'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('reports/', views.view_reports, name='view_reports'),
    path('security/', views.security_settings, name='security_settings'),
]
