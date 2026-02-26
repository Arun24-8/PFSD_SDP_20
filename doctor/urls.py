from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('patients/', views.doctor_patients, name='doctor_patients'),
    path('consultations/', views.doctor_consultations, name='doctor_consultations'),
    path('e-prescriptions/', views.doctor_e_prescriptions, name='doctor_e_prescriptions'),
    path('notifications/', views.doctor_notifications, name='doctor_notifications'),
    path('reports/', views.doctor_reports, name='doctor_reports'),
    path('profile/', views.doctor_profile, name='doctor_profile'),
]
