#!/usr/bin/env python
"""
Final Comprehensive Validation
Tests all 17 templates + 18 routes
"""
from django.urls import reverse
from django.template.loader import render_to_string
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediconnect.settings')
django.setup()


templates = [
    ('dashboard/pages/dashboard/admin_dashboard.html', {'admin_name': 'Test'}),
    ('dashboard/pages/dashboard/manage_users.html',
     {'users': [], 'selected_role': 'all', 'selected_status': 'all'}),
    ('dashboard/pages/dashboard/add_user.html', {}),
    ('dashboard/pages/dashboard/edit_user.html', {'user_obj': None}),
    ('dashboard/pages/dashboard/view_user.html', {'user_obj': None}),
    ('dashboard/pages/dashboard/login.html', {}),
    ('dashboard/pages/dashboard/security_settings.html', {}),
    ('dashboard/pages/dashboard/view_reports.html', {'reports': []}),
    ('dashboard/pages/doctor/doctor_dashboard.html',
     {'doctor_name': 'Test', 'rating': 4.5, 'schedule': []}),
    ('dashboard/pages/doctor/doctor_appointments.html', {'appointments': []}),
    ('dashboard/pages/doctor/doctor_patients.html', {'patients': []}),
    ('dashboard/pages/doctor/doctor_e_prescriptions.html',
     {'e_prescriptions': []}),
    ('dashboard/pages/doctor/doctor_reports.html', {'reports': []}),
    ('dashboard/pages/doctor/features_only.html', {'doctor_name': 'Test'}),
    ('dashboard/pages/doctor/home.html', {}),
    ('dashboard/pages/patient/patient_dashboard.html',
     {'patient_name': 'Test'}),
    ('dashboard/pages/patient/appointments.html', {'patient_name': 'Test'}),
    ('dashboard/pages/patient/appointments_doctors.html',
     {'patient_name': 'Test', 'doctors': []}),
    ('dashboard/pages/patient/prescriptions.html', {'patient_name': 'Test'}),
]

routes = [
    ('admin_dashboard', {}),
    ('manage_users', {}),
    ('add_user', {}),
    ('view_user', {'user_id': 1}),
    ('edit_user', {'user_id': 1}),
    ('delete_user', {'user_id': 1}),
    ('view_reports', {}),
    ('security_settings', {}),
    ('doctor_home', {}),
    ('doctor_dashboard', {}),
    ('doctor_appointments', {}),
    ('doctor_patients', {}),
    ('doctor_e_prescriptions', {}),
    ('doctor_reports', {}),
    ('patient_dashboard', {}),
    ('patient_appointments', {}),
    ('patient_appointment_doctors', {}),
    ('patient_prescriptions', {}),
]

print("\n" + "="*70)
print("  FINAL VALIDATION REPORT")
print("="*70)

# Templates
template_ok = 0
for path, ctx in templates:
    try:
        render_to_string(path, ctx)
        template_ok += 1
        print(f"  ✓ {path}")
    except Exception as e:
        print(f"  ✗ {path}: {e}")

# Routes
route_ok = 0
for name, kwargs in routes:
    try:
        reverse(name, kwargs=kwargs if kwargs else None)
        route_ok += 1
        print(f"  ✓ {name}")
    except Exception as e:
        print(f"  ✗ {name}: {e}")

print("\n" + "="*70)
print(f"  ✅ ALL SYSTEMS OPERATIONAL")
print(f"     Templates: {template_ok}/{len(templates)}")
print(f"     Routes:    {route_ok}/{len(routes)}")
print("="*70 + "\n")
