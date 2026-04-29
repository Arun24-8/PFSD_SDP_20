"""
URL configuration for mediconnect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from doctor import views as doctor_views

urlpatterns = [
    path('', doctor_views.home, name='home'),
    path('features/', doctor_views.features, name='features'),
    path('login/', doctor_views.login, name='login'),
    path('signout/', doctor_views.signout, name='signout'),

    # patient routes
    path('patient/dashboard/', doctor_views.patient_dashboard, name='patient_dashboard'),
    path('patient/appointments/', doctor_views.patient_appointments,
         name='patient_appointments'),
    path('patient/appointments/book/', doctor_views.patient_appointment_doctors,
         name='patient_appointment_doctors'),
    path('patient/prescriptions/', doctor_views.patient_prescriptions,
         name='patient_prescriptions'),
    path('patient/prescriptions/download/<int:prescription_index>/', doctor_views.patient_download_prescription,
         name='patient_download_prescription'),
    path('patient/prescriptions/<int:prescription_index>/', doctor_views.patient_prescription_detail,
         name='patient_prescription_detail'),

    # doctor app urls
    path('doctor/', include('doctor.urls')),

    path('admin/', include('admin_management.urls')),
    path('admin-panel/', admin.site.urls),
]
