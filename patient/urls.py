from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.patient_dashboard, name="patient_dashboard"),
    path("appointments/", views.patient_appointments, name="patient_appointments"),
    path(
        "appointments/book/",
        views.patient_appointment_doctors,
        name="patient_appointment_doctors",
    ),
    path("prescriptions/", views.patient_prescriptions, name="patient_prescriptions"),
    path(
        "prescriptions/download/<int:prescription_index>/",
        views.patient_download_prescription,
        name="patient_download_prescription",
    ),
    path(
        "prescriptions/<int:prescription_index>/",
        views.patient_prescription_detail,
        name="patient_prescription_detail",
    ),
]
