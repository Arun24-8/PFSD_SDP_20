from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import AdminProfile

# Create your views here.


def is_admin(request):
    """Check if user is logged in as admin"""
    return request.session.get("admin_name") is not None


def admin_dashboard(request):
    """Display admin dashboard"""
    if not is_admin(request):
        return redirect('login')

    admin_name = request.session.get("admin_name")

    # sample aggregate data pulled from patient dashboard idea
    from doctor.models import Doctor
    from django.db import utils as db_utils

    SAMPLE_PATIENT_STATS = {
        'upcoming_appointments': 20,
        'active_prescriptions': 45,
        'total_visits': 1023,
    }

    SAMPLE_APPOINTMENT_PREVIEW = [
        {'date_label': 'TODAY', 'month': 'Feb', 'doctor': 'Dr. A. Roy', 'time': '09:00 AM'},
        {'date_label': 'TOMORROW', 'month': 'Feb', 'doctor': 'Dr. N. Singh', 'time': '11:30 AM'},
    ]

    # dynamic list of doctors (guard against missing table)
    try:
        doctor_list = list(Doctor.objects.values('name', 'rating'))
    except db_utils.OperationalError:
        doctor_list = []

    context = {
        'admin_profile': {
            'user': {
                'first_name': admin_name.split()[0] if admin_name else 'Admin',
                'last_name': ' '.join(admin_name.split()[1:]) if len(admin_name.split()) > 1 else ''
            }
        },
        'patient_stats': SAMPLE_PATIENT_STATS,
        'appointment_preview': SAMPLE_APPOINTMENT_PREVIEW,
        'doctor_list': doctor_list,
    }
    return render(request, 'dashboard/pages/dashboard/admin_dashboard.html', context)


def manage_users(request):
    """Manage users in the system"""
    if not is_admin(request):
        return redirect('login')

    users = User.objects.all()
    context = {
        'users': users,
    }
    return render(request, 'dashboard/pages/dashboard/manage_users.html', context)


def view_reports(request):
    """View system reports"""
    if not is_admin(request):
        return redirect('login')

    context = {}
    return render(request, 'dashboard/pages/dashboard/view_reports.html', context)


def security_settings(request):
    """Manage security settings"""
    if not is_admin(request):
        return redirect('login')

    context = {}
    return render(request, 'dashboard/pages/dashboard/security_settings.html', context)
