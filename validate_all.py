#!/usr/bin/env python
from django.urls import reverse
from django.template.loader import get_template
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediconnect.settings')
django.setup()


print("="*60)
print("VALIDATING ALL TEMPLATES & ROUTES")
print("="*60)

templates = [
    'dashboard/add_user.html',
    'dashboard/admin_dashboard.html',
    'dashboard/edit_user.html',
    'dashboard/login.html',
    'dashboard/manage_users.html',
    'dashboard/security_settings.html',
    'dashboard/view_reports.html',
    'dashboard/view_user.html',
    'doctor/doctor_appointments.html',
    'doctor/doctor_dashboard.html',
    'doctor/doctor_e_prescriptions.html',
    'doctor/doctor_patients.html',
    'doctor/doctor_reports.html',
    'doctor/features_only.html',
    'doctor/home.html',
    'patient/appointments.html',
    'patient/appointments_doctors.html',
    'patient/patient_dashboard.html',
    'patient/prescriptions.html',
]

routes = [
    'admin_dashboard', 'manage_users', 'add_user', 'view_user', 'edit_user', 'delete_user',
    'view_reports', 'security_settings', 'doctor_home', 'doctor_dashboard', 'doctor_appointments',
    'doctor_patients', 'doctor_e_prescriptions', 'doctor_reports', 'patient_dashboard',
    'patient_appointments', 'patient_appointment_doctors', 'patient_prescriptions'
]

# Test templates
print(f"\n✓ TEMPLATES ({len(templates)})")
failures = []
for template in templates:
    try:
        get_template(template)
        print(f"  ✓ {template}")
    except Exception as e:
        print(f"  ✗ {template}: {e}")
        failures.append(template)

# Test routes
print(f"\n✓ ROUTES ({len(routes)})")
route_failures = []
for route in routes:
    try:
        path = reverse(route)
        print(f"  ✓ {route}: {path}")
    except Exception as e:
        print(f"  ✗ {route}: {e}")
        route_failures.append(route)

print("\n" + "="*60)
if not failures and not route_failures:
    print("✓ ALL TEMPLATES AND ROUTES VALID")
    print("  Templates: 19/19 ✓")
    print("  Routes: 18/18 ✓")
else:
    if failures:
        print(f"✗ Template Failures: {len(failures)}")
        for t in failures:
            print(f"    - {t}")
    if route_failures:
        print(f"✗ Route Failures: {len(route_failures)}")
        for r in route_failures:
            print(f"    - {r}")
print("="*60)
