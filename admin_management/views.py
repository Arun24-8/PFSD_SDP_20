from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from django.db import IntegrityError
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
    if email:
        doctor_obj, created = Doctor.objects.get_or_create(
            email=email,
            defaults={"name": doctor_name, "rating": Decimal("4.50")},
        )
    else:
        doctor_obj, created = Doctor.objects.get_or_create(
            name=doctor_name,
            defaults={"rating": Decimal("4.50")},
        )

    if created and not doctor_obj.rating:
        doctor_obj.rating = Decimal("4.50")
        doctor_obj.save(update_fields=["rating"])
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
            doctor_count = len(
                {item.get('name') for item in PATIENT_BOOKING_DOCTORS if item.get('name')})
    except db_utils.OperationalError:
        patient_count = len(DOCTOR_PATIENTS)
        doctor_count = len({item.get('name')
                           for item in PATIENT_BOOKING_DOCTORS if item.get('name')})

    total_consultations = len(DOCTOR_APPOINTMENTS)
    alerts = sum(1 for appointment in DOCTOR_APPOINTMENTS if appointment.get(
        'status') == 'PENDING')
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

        # Use email as the unique constraint; do not block on duplicate names

        # If a user already exists with this username/email, update and reuse it
        existing_user = User.objects.filter(
            Q(username=email) | Q(email=email)).first()
        if existing_user:
            existing_user.first_name = first_name
            existing_user.last_name = last_name
            existing_user.email = email
            existing_user.username = email
            existing_user.is_active = _status_to_is_active(status)
            if password:
                existing_user.set_password(password)

            _apply_role_to_user(existing_user, role)
            _create_doctor_profile(
                f"{first_name} {last_name}".strip(), email=email)
            existing_user.is_superuser = False
            existing_user.save()

            messages.success(request, 'Doctor account created successfully.')
            return redirect('manage_users')

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=False,
                is_active=_status_to_is_active(status),
            )
        except IntegrityError:
            messages.error(
                request, 'A user with this email/username already exists.')
            return render(request, 'dashboard/pages/dashboard/add_user.html')

        _apply_role_to_user(user, role)
        _create_doctor_profile(
            f"{first_name} {last_name}".strip(), email=email)
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
        # If user is a doctor, prevent deletion when they have appointments
        if user_obj.groups.filter(name='Doctor').exists():
            try:
                from doctor.views import DOCTOR_APPOINTMENTS
                from doctor.models import Doctor

                doctor = None
                # prefer matching by email if doctor record exists
                if user_obj.email:
                    doctor = Doctor.objects.filter(
                        email=user_obj.email).first()

                # fallback: match by name if no doctor record found
                if not doctor:
                    candidate_name = f"{user_obj.first_name} {user_obj.last_name}".strip(
                    )
                    # normalize function: remove 'Dr.' and lowercase

                    def _norm(n):
                        return (n or '').replace('Dr.', '').replace('Dr', '').strip().lower()

                    for appt in DOCTOR_APPOINTMENTS:
                        if _norm(appt.get('doctor')) == _norm(candidate_name):
                            messages.error(
                                request, 'Cannot delete doctor with existing appointments.')
                            return redirect('manage_users')

                # if a doctor object exists, check appointments by that name too
                if doctor:
                    def _norm2(n):
                        return (n or '').replace('Dr.', '').replace('Dr', '').strip().lower()

                    for appt in DOCTOR_APPOINTMENTS:
                        if _norm2(appt.get('doctor')) == _norm2(doctor.name):
                            messages.error(
                                request, 'Cannot delete doctor with existing appointments.')
                            return redirect('manage_users')
            except Exception:
                # if anything goes wrong checking appointments, be conservative and block deletion
                messages.error(
                    request, 'Cannot delete doctor: appointment check failed.')
                return redirect('manage_users')

        full_name = f"{user_obj.first_name} {user_obj.last_name}".strip(
        ) or user_obj.username
        user_obj.delete()
        messages.success(request, f'User "{full_name}" deleted successfully.')
    return redirect('manage_users')


def view_reports(request):
    """View system reports"""
    if not is_admin(request):
        return redirect('login')

    report_type = request.GET.get('report_type', 'weekly').lower()

    # determine date range based on report_type
    from datetime import timedelta
    from doctor.views import DOCTOR_APPOINTMENTS, MONTH_MAP
    from doctor.models import Doctor

    today = datetime.now().date()
    if report_type == 'daily':
        start_date = today
        end_date = today
    elif report_type == 'weekly':
        end_date = today
        start_date = today - timedelta(days=6)
    elif report_type == 'monthly':
        end_date = today
        start_date = today - timedelta(days=29)
    elif report_type == 'yearly':
        end_date = today
        start_date = today - timedelta(days=364)
    else:
        end_date = today
        start_date = today - timedelta(days=6)

    def _parse_appointment_date(appt):
        day = appt.get('day')
        month = appt.get('month')
        year = appt.get('year')
        if not (day and month and year):
            return None
        try:
            month_short = MONTH_MAP.get(month.upper(), month)
            return datetime.strptime(f"{day} {month_short} {year}", "%d %b %Y").date()
        except Exception:
            return None

    appt_dates = []
    for appt in DOCTOR_APPOINTMENTS:
        ad = _parse_appointment_date(appt)
        if ad and start_date <= ad <= end_date:
            appt_dates.append(ad)

    consultations_count = len(appt_dates)
    revenue = consultations_count * 50

    # average rating
    try:
        from django.db.models import Avg

        avg_rating = Doctor.objects.aggregate(avg=Avg('rating'))['avg']
        avg_rating = round(float(avg_rating or 0), 2)
    except Exception:
        avg_rating = 0.0

    # growth vs previous period
    period_days = (end_date - start_date).days + 1
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=period_days - 1)
    prev_count = 0
    for appt in DOCTOR_APPOINTMENTS:
        ad = _parse_appointment_date(appt)
        if ad and prev_start <= ad <= prev_end:
            prev_count += 1

    if prev_count == 0:
        growth = None if consultations_count == 0 else 100.0
    else:
        growth = round(
            ((consultations_count - prev_count) / prev_count) * 100.0, 1)

    # build daily trend list
    trend_map = {}
    cur = start_date
    while cur <= end_date:
        trend_map[cur.isoformat()] = 0
        cur += timedelta(days=1)
    for d in appt_dates:
        trend_map[d.isoformat()] = trend_map.get(d.isoformat(), 0) + 1

    # convert trend to ordered list with percentage for bar heights
    temp_list = [(k, trend_map[k]) for k in sorted(trend_map.keys())]
    max_count = max((cnt for _, cnt in temp_list), default=1)
    trend_list = []
    for k, cnt in temp_list:
        pct = int((cnt / max_count) * 100) if max_count > 0 else 0
        trend_list.append({'date': k, 'count': cnt, 'pct': pct})

    # CSV export
    if request.GET.get('export') == '1':
        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"mediconnect_report_{report_type}_{timestamp}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(['MediConnect Reports Export'])
        writer.writerow(
            ['Generated At', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow(['Report Type', report_type.replace('_', ' ').title()])
        writer.writerow(
            ['Time Range', f"{start_date.isoformat()} to {end_date.isoformat()}"])
        writer.writerow([])
        writer.writerow(['Metric', 'Value', 'Notes'])
        writer.writerow(['Consultations', str(
            consultations_count), f'{start_date} to {end_date}'])
        writer.writerow(
            ['Revenue', f'${revenue}', 'Est. $50 per consultation'])
        writer.writerow(['Average Rating', str(avg_rating), 'Out of 5'])
        writer.writerow(
            ['Growth', f'{growth if growth is not None else "N/A"}', 'Vs previous period'])
        writer.writerow([])
        writer.writerow(['Date', 'Consultation Count'])
        for date_iso, cnt in trend_list:
            writer.writerow([date_iso, str(cnt)])
        return response

    context = {
        'report_type': report_type,
        'start_date': start_date,
        'end_date': end_date,
        'consultations': consultations_count,
        'revenue': revenue,
        'avg_rating': avg_rating,
        'growth': growth,
        'trend': trend_list,
        'max_count': max_count,
    }
    return render(request, 'dashboard/pages/dashboard/view_reports.html', context)


def generate_report(request):
    """Generate a PDF report for the selected report_type and download it."""
    if not is_admin(request):
        return redirect('login')

    report_type = request.GET.get('report_type', 'weekly').lower()
    # reuse logic from view_reports to compute metrics
    from datetime import timedelta
    from doctor.views import DOCTOR_APPOINTMENTS, MONTH_MAP
    from doctor.models import Doctor

    today = datetime.now().date()
    if report_type == 'daily':
        start_date = today
        end_date = today
    elif report_type == 'weekly':
        end_date = today
        start_date = today - timedelta(days=6)
    elif report_type == 'monthly':
        end_date = today
        start_date = today - timedelta(days=29)
    elif report_type == 'yearly':
        end_date = today
        start_date = today - timedelta(days=364)
    else:
        end_date = today
        start_date = today - timedelta(days=6)

    def _parse_appointment_date(appt):
        day = appt.get('day')
        month = appt.get('month')
        year = appt.get('year')
        if not (day and month and year):
            return None
        try:
            month_short = MONTH_MAP.get(month.upper(), month)
            return datetime.strptime(f"{day} {month_short} {year}", "%d %b %Y").date()
        except Exception:
            return None

    appt_dates = []
    for appt in DOCTOR_APPOINTMENTS:
        ad = _parse_appointment_date(appt)
        if ad and start_date <= ad <= end_date:
            appt_dates.append(ad)

    consultations_count = len(appt_dates)
    revenue = consultations_count * 50
    try:
        from django.db.models import Avg

        avg_rating = Doctor.objects.aggregate(avg=Avg('rating'))['avg']
        avg_rating = round(float(avg_rating or 0), 2)
    except Exception:
        avg_rating = 0.0

    # create simple PDF using reportlab
    import io
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except Exception:
        # If reportlab missing, show friendly message
        messages.error(
            request, 'PDF generation library not installed. Please run pip install reportlab in the project venv.')
        return redirect('view_reports')

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 50
    y = height - margin

    p.setFont('Helvetica-Bold', 16)
    p.drawString(margin, y, 'MediConnect — System Report')
    y -= 30

    p.setFont('Helvetica', 10)
    p.drawString(
        margin, y, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    y -= 20
    p.drawString(
        margin, y, f'Period: {start_date.isoformat()} to {end_date.isoformat()}')
    y -= 30

    # metrics
    p.setFont('Helvetica-Bold', 12)
    p.drawString(margin, y, 'Metrics:')
    y -= 18
    p.setFont('Helvetica', 11)
    p.drawString(margin, y, f'- Consultations: {consultations_count}')
    y -= 16
    p.drawString(margin, y, f'- Revenue (est): ${revenue}')
    y -= 16
    p.drawString(margin, y, f'- Average Rating: {avg_rating}')
    y -= 30

    p.setFont('Helvetica-Bold', 12)
    p.drawString(margin, y, 'Daily trend:')
    y -= 18
    p.setFont('Helvetica', 10)
    # write up to 40 lines; add new page if necessary
    trend_dates = sorted({d.isoformat() for d in appt_dates})
    if not trend_dates:
        p.drawString(margin, y, 'No appointments in this period')
        y -= 16
    else:
        for td in trend_dates:
            cnt = sum(1 for d in appt_dates if d.isoformat() == td)
            p.drawString(margin, y, f'{td}: {cnt}')
            y -= 14
            if y < margin + 40:
                p.showPage()
                y = height - margin

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="mediconnect_report_{report_type}_{start_date}_{end_date}.pdf"'
    return response


def view_reports_detail(request):
    if not is_admin(request):
        return redirect('login')

    report_type = request.GET.get('report_type', 'weekly').lower()
    # reuse computation from view_reports
    from datetime import timedelta
    from doctor.views import DOCTOR_APPOINTMENTS, MONTH_MAP

    today = datetime.now().date()
    if report_type == 'daily':
        start_date = today
        end_date = today
    elif report_type == 'weekly':
        end_date = today
        start_date = today - timedelta(days=6)
    elif report_type == 'monthly':
        end_date = today
        start_date = today - timedelta(days=29)
    elif report_type == 'yearly':
        end_date = today
        start_date = today - timedelta(days=364)
    else:
        end_date = today
        start_date = today - timedelta(days=6)

    def _parse_appointment_date(appt):
        day = appt.get('day')
        month = appt.get('month')
        year = appt.get('year')
        if not (day and month and year):
            return None
        try:
            month_short = MONTH_MAP.get(month.upper(), month)
            return datetime.strptime(f"{day} {month_short} {year}", "%d %b %Y").date()
        except Exception:
            return None

    appointments = []
    for idx, appt in enumerate(DOCTOR_APPOINTMENTS):
        ad = _parse_appointment_date(appt)
        if ad and start_date <= ad <= end_date:
            item = appt.copy()
            item['date'] = ad.isoformat()
            item['index'] = idx
            appointments.append(item)

    context = {
        'report_type': report_type,
        'start_date': start_date,
        'end_date': end_date,
        'appointments': appointments,
    }
    return render(request, 'dashboard/pages/dashboard/report_detail.html', context)


def view_top_doctors(request):
    if not is_admin(request):
        return redirect('login')

    from doctor.views import DOCTOR_APPOINTMENTS
    counts = {}
    for appt in DOCTOR_APPOINTMENTS:
        doc = appt.get('doctor', 'Unknown')
        counts[doc] = counts.get(doc, 0) + 1

    doctors = sorted([{'name': k, 'consultations': v}
                     for k, v in counts.items()], key=lambda x: -x['consultations'])
    return render(request, 'dashboard/pages/dashboard/top_doctors.html', {'doctors': doctors})


def security_settings(request):
    """Manage security settings"""
    if not is_admin(request):
        return redirect('login')

    context = {}
    return render(request, 'dashboard/pages/dashboard/security_settings.html', context)
