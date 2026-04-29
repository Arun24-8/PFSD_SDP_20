#!/usr/bin/env python
from django.contrib.auth.models import User
from django.urls import reverse, NoReverseMatch
from django.template.loader import render_to_string
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediconnect.settings')
django.setup()


print("="*70)
print("  COMPREHENSIVE VALIDATION: TEMPLATES + ROUTES")
print("="*70)

# Test template rendering with minimal context
templates_to_render = {
    'dashboard/admin_dashboard.html': {'admin_name': 'Test Admin'},
    'dashboard/manage_users.html': {'users': [], 'selected_role': 'all', 'selected_status': 'all'},
    'dashboard/add_user.html': {},
    'dashboard/edit_user.html': {'user_obj': None},
    'dashboard/view_user.html': {'user_obj': None},
    'dashboard/login.html': {},
    'dashboard/security_settings.html': {},
    'dashboard/view_reports.html': {'reports': []},
    'doctor/doctor_dashboard.html': {'doctor_name': 'Test', 'rating': 4.5, 'schedule': []},
    'doctor/doctor_appointments.html': {'appointments': []},
    'doctor/doctor_patients.html': {'patients': []},
    'doctor/doctor_e_prescriptions.html': {'e_prescriptions': []},
    'doctor/doctor_reports.html': {'reports': []},
    'patient/patient_dashboard.html': {'patient_name': 'Test'},
    'patient/appointments.html': {'appointments': []},
    'patient/appointments_doctors.html': {'doctors': []},
    'patient/prescriptions.html': {'prescriptions': []},
}

routes_to_test = [
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

print("\n[1] TEMPLATE RENDERING")
print("-"*70)
template_pass = 0
template_fail = 0
for template, context in templates_to_render.items():
    try:
        render_to_string(template, context)
        print(f"  ✓ {template}")
        template_pass += 1
    except Exception as e:
        print(f"  ✗ {template}")
        print(f"     Error: {str(e)[:80]}")
        template_fail += 1

print(f"\nTemplate Results: {template_pass} passed, {template_fail} failed")

print("\n[2] ROUTE RESOLUTION")
print("-"*70)
route_pass = 0
route_fail = 0
for route_name, kwargs in routes_to_test:
    try:
        path = reverse(route_name, kwargs=kwargs if kwargs else None)
        print(f"  ✓ {route_name:.<40} {path}")
        route_pass += 1
    except NoReverseMatch as e:
        print(f"  ✗ {route_name:.<40} ERROR")
        route_fail += 1

print(f"\nRoute Results: {route_pass} passed, {route_fail} failed")

print("\n" + "="*70)
if template_fail == 0 and route_fail == 0:
    print(f"  ✅ ALL SYSTEMS OPERATIONAL")
    print(f"     Templates: {template_pass}/{len(templates_to_render)} ✓")
    print(f"     Routes:    {route_pass}/{len(routes_to_test)} ✓")
else:
    print(f"  ⚠️  ISSUES DETECTED")
    if template_fail > 0:
        print(f"     Templates: {template_fail} failures")
    if route_fail > 0:
        print(f"     Routes: {route_fail} failures")
print("="*70)
