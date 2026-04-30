from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
import csv
from datetime import datetime
from decimal import Decimal
from .models import AdminProfile

# Create your views here.


def is_admin(request):
    """Check if user is logged in as admin"""
    return request.session.get("admin_name") is not None


def _split_name(full_name):
    cleaned = (full_name or "").replace("Dr.", "").replace("Dr", "").strip()
    parts = cleaned.split()
    if not parts:
        return "User", ""
    first_name = parts[0]
    last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
    return first_name, last_name


def _email_from_name(full_name, domain):
    tokens = "".join(ch.lower() if ch.isalnum()
                     else " " for ch in (full_name or "")).split()
    slug = ".".join(tokens) if tokens else "user"
    return f"{slug}@{domain}"


def _sync_users_from_dashboards():
    doctor_group, _ = Group.objects.get_or_create(name="Doctor")
    patient_group, _ = Group.objects.get_or_create(name="Patient")

    from doctor.models import Doctor
    from django.db import utils as db_utils

    try:
        doctor_names = set(Doctor.objects.values_list("name", flat=True))
    except db_utils.OperationalError:
        doctor_names = set()

    from doctor.views import PATIENT_BOOKING_DOCTORS
    for doctor_item in PATIENT_BOOKING_DOCTORS:
        doctor_name = doctor_item.get("name")
        if doctor_name:
            doctor_names.add(doctor_name)

    for doctor_name in doctor_names:
        first_name, last_name = _split_name(doctor_name)
        email = _email_from_name(doctor_name, "doctor.mediconnect.local")
        existing_doctor_user = User.objects.filter(
            first_name=first_name,
            last_name=last_name,
            groups__name="Doctor",
        ).first()
        if existing_doctor_user:
            continue

        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "is_active": True,
                "is_staff": False,
            },
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])
        user.groups.add(doctor_group)

    from doctor.views import DOCTOR_PATIENTS

    for patient in DOCTOR_PATIENTS:
        patient_name = patient.get("name", "Patient")
        first_name, last_name = _split_name(patient_name)
        email = _email_from_name(patient_name, "patient.mediconnect.local")
        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "is_active": True,
                "is_staff": False,
            },
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])
        user.groups.add(patient_group)


def _apply_role_to_user(user, role):
    normalized_role = (role or "").strip().lower()
    doctor_group, _ = Group.objects.get_or_create(name="Doctor")
    patient_group, _ = Group.objects.get_or_create(name="Patient")

    user.groups.remove(doctor_group, patient_group)

    if normalized_role == "admin":
        user.is_staff = True
    else:
        user.is_staff = False
        if normalized_role == "doctor":
            user.groups.add(doctor_group)
        else:
            user.groups.add(patient_group)


def _create_doctor_profile(full_name, email=None):
    from doctor.models import Doctor

    doctor_name = full_name.strip() or "Doctor"
    doctor_obj, created = Doctor.objects.get_or_create(
        name=doctor_name,
        defaults={"rating": Decimal("4.50"), "email": email},
    )
    if created and not doctor_obj.rating:
        doctor_obj.rating = Decimal("4.50")
        doctor_obj.save(update_fields=["rating"])
    if email and doctor_obj.email != email:
        doctor_obj.email = email
        doctor_obj.save(update_fields=["email"])
    return doctor_obj


def _status_to_is_active(status):
    return (status or "active").strip().lower() == "active"


def _infer_user_role(user):
    if user.is_staff:
        return "admin"
    if user.groups.filter(name="Doctor").exists():
        return "doctor"
    return "patient"


def admin_dashboard(request):
    """Display admin dashboard"""
    if not is_admin(request):
        return redirect('login')

    admin_name = request.session.get("admin_name")

    from django.db import utils as db_utils
    from doctor.models import Doctor
    from doctor.views import DOCTOR_APPOINTMENTS, DOCTOR_E_PRESCRIPTIONS, DOCTOR_PATIENTS, PATIENT_BOOKING_DOCTORS

    patient_count = 0
    doctor_count = 0
    try:
        patient_count = User.objects.filter(groups__name='Patient').count()
        doctor_count = Doctor.objects.count()
        if patient_count == 0:
            patient_count = len(DOCTOR_PATIENTS)
        if doctor_count == 0:
            doctor_count = len({item.get('name') for item in PATIENT_BOOKING_DOCTORS if item.get('name')})
    except db_utils.OperationalError:
        patient_count = len(DOCTOR_PATIENTS)
        doctor_count = len({item.get('name') for item in PATIENT_BOOKING_DOCTORS if item.get('name')})

    total_consultations = len(DOCTOR_APPOINTMENTS)
    alerts = sum(1 for appointment in DOCTOR_APPOINTMENTS if appointment.get('status') == 'PENDING')
    upcoming_appointments = sum(
        1 for appointment in DOCTOR_APPOINTMENTS
        if appointment.get('status') in {'PENDING', 'CONFIRMED'}
    )
    active_prescriptions = len(DOCTOR_E_PRESCRIPTIONS)
    total_visits = sum(
        1 for appointment in DOCTOR_APPOINTMENTS
        if appointment.get('status') == 'COMPLETED'
    )

    patient_stats = {
        'upcoming_appointments': upcoming_appointments,
        'active_prescriptions': active_prescriptions,
        'total_visits': total_visits,
    }

    stats = {
        'patients': patient_count,
        'doctors': doctor_count,
        'total_consultations': total_consultations,
        'alerts': alerts,
    }

    SAMPLE_APPOINTMENT_PREVIEW = [
        {'date_label': 'TODAY', 'month': 'Feb',
            'doctor': 'Dr. A. Roy', 'time': '09:00 AM'},
        {'date_label': 'TOMORROW', 'month': 'Feb',
            'doctor': 'Dr. N. Singh', 'time': '11:30 AM'},
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
        'stats': stats,
        'patient_stats': patient_stats,
        'appointment_preview': SAMPLE_APPOINTMENT_PREVIEW,
        'doctor_list': doctor_list,
    }
    return render(request, 'dashboard/pages/dashboard/admin_dashboard.html', context)


def manage_users(request):
    """Manage users in the system"""
    if not is_admin(request):
        return redirect('login')

    _sync_users_from_dashboards()
    search_term = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', 'all').strip().lower()
    status_filter = request.GET.get('status', 'all').strip().lower()

    users = User.objects.all().order_by('-date_joined')
    if search_term:
        users = users.filter(
            Q(username__icontains=search_term)
            | Q(email__icontains=search_term)
            | Q(first_name__icontains=search_term)
            | Q(last_name__icontains=search_term)
        )

    if role_filter != 'all':
        if role_filter == 'admin':
            users = users.filter(is_staff=True)
        elif role_filter == 'doctor':
            users = users.filter(groups__name='Doctor').distinct()
        elif role_filter == 'patient':
            users = users.exclude(is_staff=True).exclude(
                groups__name='Doctor').distinct()

    if status_filter != 'all':
        users = users.filter(is_active=(status_filter == 'active'))

    context = {
        'users': users,
        'search_term': search_term,
        'selected_role': role_filter,
        'selected_status': status_filter,
    }
    return render(request, 'dashboard/pages/dashboard/manage_users.html', context)


def add_user(request):
    """Add a new doctor from a separate admin page"""
    if not is_admin(request):
        return redirect('login')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        status = request.POST.get('status', 'active').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = 'doctor'

        if not first_name or not email or not password:
            messages.error(request, 'Please fill all required fields.')
            return render(request, 'dashboard/pages/dashboard/add_user.html')

        if password != confirm_password:
            messages.error(
                request, 'Password and confirm password must match.')
            return render(request, 'dashboard/pages/dashboard/add_user.html')

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, 'A user with this email already exists.')
            return render(request, 'dashboard/pages/dashboard/add_user.html')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=False,
            is_active=_status_to_is_active(status),
        )

        _apply_role_to_user(user, role)
        _create_doctor_profile(f"{first_name} {last_name}".strip(), email)
        user.is_superuser = False
        user.save(update_fields=['is_staff', 'is_active', 'is_superuser'])

        messages.success(request, 'Doctor account created successfully.')
        return redirect('manage_users')

    return render(request, 'dashboard/pages/dashboard/add_user.html')


def view_user(request, user_id):
    """View details for a single user"""
    if not is_admin(request):
        return redirect('login')

    user_obj = get_object_or_404(User, pk=user_id)
    context = {
        'user_obj': user_obj,
        'role': _infer_user_role(user_obj),
    }
    return render(request, 'dashboard/pages/dashboard/view_user.html', context)


def edit_user(request, user_id):
    """Edit an existing user"""
    if not is_admin(request):
        return redirect('login')

    user_obj = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        role = request.POST.get('role', '').strip().lower()
        status = request.POST.get('status', 'active').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not first_name or not email or not role:
            messages.error(request, 'Please fill all required fields.')
            return redirect('edit_user', user_id=user_obj.id)

        existing_email_user = User.objects.filter(username=email).exclude(
            pk=user_obj.pk).first()
        existing_secondary_email = User.objects.filter(email=email).exclude(
            pk=user_obj.pk).first()
        if existing_email_user or existing_secondary_email:
            messages.error(request, 'A user with this email already exists.')
            return redirect('edit_user', user_id=user_obj.id)

        if password or confirm_password:
            if password != confirm_password:
                messages.error(
                    request, 'Password and confirm password must match.')
                return redirect('edit_user', user_id=user_obj.id)
            user_obj.set_password(password)

        user_obj.first_name = first_name
        user_obj.last_name = last_name
        user_obj.email = email
        user_obj.username = email
        user_obj.is_active = _status_to_is_active(status)
        _apply_role_to_user(user_obj, role)
        user_obj.is_superuser = False
        user_obj.save()

        messages.success(request, 'User updated successfully.')
        return redirect('manage_users')

    context = {
        'user_obj': user_obj,
        'role': _infer_user_role(user_obj),
        'status': 'active' if user_obj.is_active else 'inactive',
    }
    return render(request, 'dashboard/pages/dashboard/edit_user.html', context)


def delete_user(request, user_id):
    """Delete a user"""
    if not is_admin(request):
        return redirect('login')

    user_obj = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        full_name = f"{user_obj.first_name} {user_obj.last_name}".strip(
        ) or user_obj.username
        user_obj.delete()
        messages.success(request, f'User "{full_name}" deleted successfully.')
    return redirect('manage_users')


def view_reports(request):
    """View system reports"""
    if not is_admin(request):
        return redirect('login')

    report_type = request.GET.get('report_type', 'daily').lower()
    time_range = request.GET.get('time_range', 'last_7_days').lower()

    if request.GET.get('export') == '1':
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"mediconnect_report_{report_type}_{time_range}_{timestamp}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(['MediConnect Reports Export'])
        writer.writerow(
            ['Generated At', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow(['Report Type', report_type.replace('_', ' ').title()])
        writer.writerow(['Time Range', time_range.replace('_', ' ').title()])
        writer.writerow([])
        writer.writerow(['Metric', 'Value', 'Notes'])
        writer.writerow(['Consultations', '487', 'This month'])
        writer.writerow(['Revenue', '$12,450', 'This month'])
        writer.writerow(['Average Rating', '4.8', 'Out of 5'])
        writer.writerow(['Growth', '+23%', 'Month over month'])
        writer.writerow([])
        writer.writerow(['Month', 'Consultation Trend'])
        writer.writerow(['Jan', '60%'])
        writer.writerow(['Feb', '75%'])
        writer.writerow(['Mar', '85%'])
        writer.writerow(['Apr', '70%'])
        writer.writerow(['May', '90%'])
        writer.writerow(['Jun', '95%'])
        return response

    context = {
        'report_type': report_type,
        'time_range': time_range,
    }
    return render(request, 'dashboard/pages/dashboard/view_reports.html', context)


def security_settings(request):
    """Manage security settings"""
    if not is_admin(request):
        return redirect('login')

    context = {}
    return render(request, 'dashboard/pages/dashboard/security_settings.html', context)
