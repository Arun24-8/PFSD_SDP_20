from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('patients/', views.doctor_patients, name='doctor_patients'),
    path('e-prescriptions/', views.doctor_e_prescriptions,
         name='doctor_e_prescriptions'),
    path('reports/', views.doctor_reports, name='doctor_reports'),
]
