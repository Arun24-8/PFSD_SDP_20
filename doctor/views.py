from .models import Doctor
import re
import random

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import Group, User
from datetime import datetime

MONTH_MAP = {
    'JAN': 'Jan', 'FEB': 'Feb', 'MAR': 'Mar', 'APR': 'Apr', 'MAY': 'May', 'JUN': 'Jun',
    'JUL': 'Jul', 'AUG': 'Aug', 'SEP': 'Sep', 'OCT': 'Oct', 'NOV': 'Nov', 'DEC': 'Dec'
}


PATIENT_BOOKING_DOCTORS = [
    {"specialist": "Cardiology", "name": "Dr. Rajesh Reddy",
        "city": "Hyderabad", "rating": "4.9", "reviews": 215},
    {"specialist": "Neurology", "name": "Dr. Priya Sharma",
        "city": "Bengaluru", "rating": "4.8", "reviews": 174},
    {"specialist": "Orthopedics", "name": "Dr. Suresh Kumar",
        "city": "Chennai", "rating": "4.7", "reviews": 163},
    {"specialist": "Pediatrics", "name": "Dr. Anjali Verma",
        "city": "Pune", "rating": "4.9", "reviews": 208},
    {"specialist": "Dermatology", "name": "Dr. Kavitha Rao",
        "city": "Mumbai", "rating": "4.8", "reviews": 189},
    {"specialist": "Gynecology", "name": "Dr. Swathi Reddy",
        "city": "Hyderabad", "rating": "4.7", "reviews": 151},
    {"specialist": "Ophthalmology", "name": "Dr. Vivek Gupta",
        "city": "Delhi", "rating": "4.8", "reviews": 198},
    {"specialist": "ENT", "name": "Dr. Harish Naidu",
        "city": "Visakhapatnam", "rating": "4.6", "reviews": 133},
    {"specialist": "Psychiatry", "name": "Dr. Neha Singh",
        "city": "Noida", "rating": "4.9", "reviews": 176},
    {"specialist": "Oncology", "name": "Dr. Arvind Patel",
        "city": "Ahmedabad", "rating": "4.8", "reviews": 142},
    {"specialist": "Gastroenterology", "name": "Dr. Manish Agarwal",
        "city": "Jaipur", "rating": "4.7", "reviews": 147},
    {"specialist": "Nephrology", "name": "Dr. Kiran Kumar",
        "city": "Hyderabad", "rating": "4.8", "reviews": 159},
    {"specialist": "Pulmonology", "name": "Dr. Mohammed Asif",
        "city": "Kochi", "rating": "4.7", "reviews": 138},
    {"specialist": "Endocrinology", "name": "Dr. Deepika Nair",
        "city": "Thiruvananthapuram", "rating": "4.9", "reviews": 171},
    {"specialist": "Urology", "name": "Dr. Ramesh Babu",
        "city": "Vijayawada", "rating": "4.7", "reviews": 145},
    {"specialist": "Radiology", "name": "Dr. Sunil Joshi",
        "city": "Indore", "rating": "4.6", "reviews": 124},
    {"specialist": "Anesthesiology", "name": "Dr. Pooja Mehta",
        "city": "Surat", "rating": "4.8", "reviews": 166},
    {"specialist": "Pathology", "name": "Dr. Lakshmi Devi",
        "city": "Mysuru", "rating": "4.7", "reviews": 139},
    {"specialist": "General Medicine", "name": "Dr. Ravi Teja",
        "city": "Warangal", "rating": "4.8", "reviews": 203},
    {"specialist": "General Surgery", "name": "Dr. Srinivas Rao",
        "city": "Nellore", "rating": "4.9", "reviews": 194},
]


def _name_from_email(email):
    local_part = (email or "").split("@", 1)[0].strip()
    cleaned = re.sub(r"[._-]+", " ", local_part)
    normalized = " ".join(cleaned.split())
    return normalized.title() if normalized else "Patient"


def _display_name_from_user(user):
    full_name = f"{(user.first_name or '').strip()} {(user.last_name or '').strip()}".strip()
    if full_name:
        return full_name
    return _name_from_email(user.email or user.username)


def _db_patient_cards():
    patient_users = (
        User.objects.filter(groups__name="Patient", is_active=True)
        .distinct()
        .order_by("first_name", "last_name", "username")
    )
    cards = []
    for user in patient_users:
        cards.append({
            "name": _display_name_from_user(user),
            "age": "N/A",
            "gender": "N/A",
            "condition": "General Consultation",
            "last_visit": "N/A",
            "risk": "Low",
        })
    return cards


def _db_patient_name_set():
    return {
        patient.get("name", "").strip().lower()
        for patient in _db_patient_cards()
        if patient.get("name")
    }


def _db_doctor_cards():
    cards = []
    for doctor in Doctor.objects.order_by("name"):
        doctor_name = doctor.name or "Doctor"
        if not doctor_name.lower().startswith("dr."):
            doctor_name = f"Dr. {doctor_name}"
        cards.append({
            "specialist": "General Medicine",
            "name": doctor_name,
            "city": "Available Online",
            "rating": f"{doctor.rating}",
            "reviews": 0,
        })
    return cards


def _db_filtered_appointments():
    allowed_patients = _db_patient_name_set()
    appointments = []
    for idx, appointment in enumerate(DOCTOR_APPOINTMENTS):
        patient_key = appointment.get("patient", "").strip().lower()
        if patient_key and patient_key in allowed_patients:
            item = appointment.copy()
            item["appointment_index"] = idx
            appointments.append(item)
    return appointments


def _db_filtered_prescriptions():
    allowed_patients = _db_patient_name_set()
    prescriptions = []
    for idx, prescription in enumerate(DOCTOR_E_PRESCRIPTIONS):
        patient_key = prescription.get("patient", "").strip().lower()
        if patient_key and patient_key in allowed_patients:
            item = prescription.copy()
            item["index"] = idx
            item["status_label"] = prescription.get("status", "ACTIVE").title()
            prescriptions.append(item)
    return prescriptions


def _get_patient_appointments(patient_name):
    patient_key = (patient_name or "").strip().lower()
    appointments = []
    for appointment in _db_filtered_appointments():
        if appointment.get("patient", "").strip().lower() != patient_key:
            continue
        item = appointment.copy()
        try:
            item["date_iso"] = datetime.strptime(
                f"{appointment.get('day', '01')} {appointment.get('month', 'JAN')} {appointment.get('year', '2026')}",
                "%d %b %Y",
            ).date().isoformat()
        except ValueError:
            item["date_iso"] = ""
        item["join_available"] = appointment.get("status") == "CONFIRMED"
        item["status_label"] = appointment.get("status", "PENDING").title()
        appointments.append(item)
    return appointments


def _get_patient_prescriptions(patient_name):
    patient_key = (patient_name or "").strip().lower()
    prescriptions = []
    for prescription in _db_filtered_prescriptions():
        if prescription.get("patient", "").strip().lower() != patient_key:
            continue
        item = prescription.copy()
        prescriptions.append(item)
    return prescriptions


def home(request):
    return render(
        request,
        "dashboard/pages/doctor/home.html",
        {},
    )


def features(request):
    doctor_name = request.session.get("doctor_name")
    return render(
        request,
        "dashboard/pages/doctor/features_only.html",
        {"doctor_name": doctor_name},
    )


def patient_dashboard(request):
    patient_name = request.session.get("patient_name")
    if not patient_name:
        return redirect("login")

    appointments = _get_patient_appointments(patient_name)
    prescriptions = _get_patient_prescriptions(patient_name)

    return render(
        request,
        "dashboard/pages/patient/patient_dashboard.html",
        {
            "patient_name": patient_name,
            "appointments": appointments,
            "appointments_count": len(appointments),
            "prescriptions_count": len(prescriptions),
            "prescriptions": prescriptions,
        },
    )


def patient_appointments(request):
    patient_name = request.session.get("patient_name")
    if not patient_name:
        return redirect("login")

    appointments = _get_patient_appointments(patient_name)

    return render(
        request,
        "dashboard/pages/patient/appointments.html",
        {
            "patient_name": patient_name,
            "appointments": appointments,
        },
    )


def patient_appointment_doctors(request):
    patient_name = request.session.get("patient_name")
    if not patient_name:
        return redirect("login")

    return render(
        request,
        "dashboard/pages/patient/appointments_doctors.html",
        {
            "patient_name": patient_name,
            "doctors": _db_doctor_cards(),
        },
    )


def patient_prescriptions(request):
    patient_name = request.session.get("patient_name")
    if not patient_name:
        return redirect("login")

    prescriptions = _get_patient_prescriptions(patient_name)

    return render(
        request,
        "dashboard/pages/patient/prescriptions.html",
        {
            "patient_name": patient_name,
            "prescriptions": prescriptions,
        },
    )


def patient_download_prescription(request, prescription_index):
    patient_name = request.session.get("patient_name")
    if not patient_name:
        return redirect("login")

    if not (0 <= prescription_index < len(DOCTOR_E_PRESCRIPTIONS)):
        return redirect("patient_prescriptions")

    prescription = DOCTOR_E_PRESCRIPTIONS[prescription_index]
    filename = f"prescription-{prescription_index + 1}.txt"
    lines = [
        f"Patient: {prescription.get('patient', '')}",
        f"Date: {prescription.get('date', '')}",
        f"Diagnosis: {prescription.get('diagnosis', '')}",
        f"Status: {prescription.get('status', '')}",
        "",
        "Medicines:",
    ]
    for med in prescription.get("medicines", []):
        name = med.get("name", "Medicine")
        note = med.get("note", "")
        lines.append(f"- {name}: {note}")

    content = "\n".join(lines)
    response = HttpResponse(content, content_type="text/plain")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def patient_prescription_detail(request, prescription_index):
    patient_name = request.session.get("patient_name")
    if not patient_name:
        return redirect("login")

    if not (0 <= prescription_index < len(DOCTOR_E_PRESCRIPTIONS)):
        return redirect("patient_prescriptions")

    prescription = DOCTOR_E_PRESCRIPTIONS[prescription_index].copy()
    prescription["index"] = prescription_index
    return render(
        request,
        "dashboard/pages/patient/patient_prescription_detail.html",
        {
            "patient_name": patient_name,
            "prescription": prescription,
        },
    )


def login(request):
    error = None
    success = None
    form_mode = request.GET.get("mode", "signin").strip().lower()
    if form_mode not in {"signin", "register", "forgot"}:
        form_mode = "signin"
    selected_role = request.GET.get("role", "patient").strip().lower()
    if selected_role not in {"patient", "doctor", "admin"}:
        selected_role = "patient"
    if form_mode == "register":
        selected_role = "patient"
    if form_mode == "forgot" and selected_role == "admin":
        selected_role = "patient"
    if request.method == "POST":
        action = request.POST.get("action", "signin")
        role = request.POST.get("role", "patient").strip().lower()
        selected_role = role if role in {"patient", "doctor", "admin"} else "patient"

        if action == "register":
            form_mode = "register"
            full_name = request.POST.get("full_name", "").strip()
            username = request.POST.get("username", "").strip()
            email = request.POST.get("email", "").strip().lower()
            password = request.POST.get("password", "")
            confirm_password = request.POST.get("confirm_password", "")
            contact_number = request.POST.get("contact_number", "").strip()

            if role != "patient":
                error = "New accounts can be created from the Patient option only."
            elif not full_name or not username or not email or not password or not confirm_password:
                error = "Please fill all required fields."
            elif password != confirm_password:
                error = "Passwords do not match."
            elif User.objects.filter(username__iexact=username).exists():
                error = "This username is already taken."
            elif User.objects.filter(email__iexact=email).exists():
                error = "A user with this email already exists."
            else:
                first_name, _, last_name = full_name.partition(" ")
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )
                patient_group, _ = Group.objects.get_or_create(name="Patient")
                user.groups.add(patient_group)
                if contact_number:
                    request.session["patient_contact_number"] = contact_number
                return render(
                    request,
                    "dashboard/pages/dashboard/login.html",
                    {
                        "success": "Patient account created successfully. Please sign in.",
                        "form_mode": "signin",
                        "selected_role": "patient",
                        "request": request,
                    },
                )

            if error:
                return render(
                    request,
                    "dashboard/pages/dashboard/login.html",
                    {
                        "error": error,
                        "form_mode": form_mode,
                        "selected_role": "patient",
                        "request": request,
                    },
                )

        if action == "forgot":
            form_mode = "forgot"
            identifier = request.POST.get("email", "").strip()
            password = request.POST.get("password", "")
            confirm_password = request.POST.get("confirm_password", "")

            user_record = User.objects.filter(username__iexact=identifier).first()
            if user_record is None:
                user_record = User.objects.filter(email__iexact=identifier).first()

            if role not in {"patient", "doctor"}:
                error = "Password reset is available for patients and doctors only."
            elif not identifier or not password or not confirm_password:
                error = "Please enter your account email and new password."
            elif password != confirm_password:
                error = "Passwords do not match."
            elif user_record is None:
                error = "No account was found for that email or username."
            elif role == "doctor" and not user_record.groups.filter(name="Doctor").exists():
                error = "Doctor account not found. Please contact admin."
            elif role == "patient" and (user_record.is_staff or user_record.groups.filter(name="Doctor").exists()):
                error = "Patient account not found for those details."
            else:
                user_record.set_password(password)
                user_record.save(update_fields=["password"])
                success = "Password updated successfully. Please sign in."
                form_mode = "signin"

            return render(
                request,
                "dashboard/pages/dashboard/login.html",
                {
                    "error": error,
                    "success": success,
                    "form_mode": form_mode,
                    "selected_role": selected_role,
                    "request": request,
                },
            )

        identifier = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        # find user by username or email
        user_record = User.objects.filter(username__iexact=identifier).first()
        if user_record is None:
            user_record = User.objects.filter(email__iexact=identifier).first()

        user = None
        if user_record is not None:
            user = authenticate(request, username=user_record.username, password=password)

        if user is None:
            error = "Invalid email or password."
            return render(request, "dashboard/pages/dashboard/login.html", {"error": error, "form_mode": "signin", "selected_role": selected_role, "request": request})

        # successful authentication — log the user in
        auth_login(request, user)

        if role == "patient":
            request.session["patient_name"] = _display_name_from_user(user)
            return redirect("patient_dashboard")
        elif role == "admin":
            if not user.is_staff:
                error = "Admin access required."
                return render(request, "dashboard/pages/dashboard/login.html", {"error": error, "form_mode": "signin", "selected_role": selected_role, "request": request})
            request.session["admin_name"] = _name_from_email(identifier)
            return redirect("admin_dashboard")
        elif role == "doctor":
            # ensure the authenticated user is actually in the Doctor group
            if not user.groups.filter(name="Doctor").exists():
                error = "Doctor account not found. Please contact admin."
                return render(request, "dashboard/pages/dashboard/login.html", {"error": error, "form_mode": "signin", "selected_role": selected_role, "request": request})

            # ensure a Doctor profile exists (must be provisioned by admin)
            from doctor.models import Doctor as DoctorModel
            doctor_profile = DoctorModel.objects.filter(email__iexact=user.email).first()
            if doctor_profile is None:
                doctor_name = f"{user.first_name} {user.last_name}".strip() or _name_from_email(user.email or identifier)
                doctor_profile = DoctorModel.objects.filter(name__iexact=doctor_name).first()

            if doctor_profile is None:
                error = "Doctor profile not provisioned. Please contact admin."
                return render(request, "dashboard/pages/dashboard/login.html", {"error": error, "form_mode": "signin", "selected_role": selected_role, "request": request})

            request.session["doctor_name"] = doctor_profile.name
            return redirect("doctor_dashboard")
        else:
            request.session.pop("patient_name", None)
            request.session.pop("admin_name", None)
            request.session.pop("doctor_name", None)
            return redirect("home")

    return render(request, "dashboard/pages/dashboard/login.html", {"form_mode": form_mode, "selected_role": selected_role})


# sample schedule items for a doctor; in a real app these would come from a model
DOCTOR_SCHEDULE = [
    {
        "date_label": "TODAY",
        "month": "Oct",
        "patient": "John Doe",
        "specialist": "General Medicine",
        "time": "11:00 AM",
        "mode": "In-Person",
    },
    {
        "date_label": "TOMORROW",
        "month": "Oct",
        "patient": "Jane Smith",
        "specialist": "Dermatology",
        "time": "02:30 PM",
        "mode": "Video Call",
    },
]

DOCTOR_APPOINTMENTS = [
    {
        "date_label": "MON",
        "day": "04",
        "month": "APR",
        "year": "2026",
        "patient": "Arun Kumar",
        "doctor": "Dr. Sarah Johnson",
        "reason": "Follow-up for hypertension",
        "time": "09:30 AM",
        "mode": "In-Person",
        "status": "COMPLETED",
    },
    {
        "date_label": "MON",
        "day": "04",
        "month": "APR",
        "year": "2026",
        "patient": "Meera Nair",
        "doctor": "Dr. James Carter",
        "reason": "Diabetes medication review",
        "time": "11:00 AM",
        "mode": "Video Call",
        "status": "COMPLETED",
    },
    {
        "date_label": "TUE",
        "day": "05",
        "month": "APR",
        "year": "2026",
        "patient": "Rahul Verma",
        "doctor": "Dr. Anjali Singh",
        "reason": "Post-surgery check",
        "time": "02:30 PM",
        "mode": "In-Person",
        "status": "COMPLETED",
    },
    {
        "date_label": "WED",
        "day": "06",
        "month": "APR",
        "year": "2026",
        "patient": "Anitha Reddy",
        "doctor": "Dr. Neha Puri",
        "reason": "General consultation",
        "time": "04:15 PM",
        "mode": "Video Call",
        "status": "PENDING",
    },
    {
        "date_label": "THU",
        "day": "07",
        "month": "APR",
        "year": "2026",
        "patient": "Sana Shaik",
        "doctor": "Dr. Priya Menon",
        "reason": "Migraine follow-up",
        "time": "10:45 AM",
        "mode": "Video Call",
        "status": "PENDING",
    },
    {
        "date_label": "FRI",
        "day": "08",
        "month": "APR",
        "year": "2026",
        "patient": "Meera Nair",
        "doctor": "Dr. Ravi Reddy",
        "reason": "Diabetes quarterly review",
        "time": "03:00 PM",
        "mode": "In-Person",
        "status": "PENDING",
    },
]

DOCTOR_PATIENTS = [
    {
        "name": "Arun Kumar",
        "age": 42,
        "gender": "Male",
        "condition": "Hypertension",
        "last_visit": "2026-02-25",
        "risk": "Stable",
    },
    {
        "name": "Meera Nair",
        "age": 35,
        "gender": "Female",
        "condition": "Type-2 Diabetes",
        "last_visit": "2026-02-21",
        "risk": "Monitor",
    },
    {
        "name": "Rahul Verma",
        "age": 58,
        "gender": "Male",
        "condition": "Cardiac Recovery",
        "last_visit": "2026-02-20",
        "risk": "Priority",
    },
    {
        "name": "Sana Shaik",
        "age": 29,
        "gender": "Female",
        "condition": "Migraine",
        "last_visit": "2026-02-18",
        "risk": "Stable",
    },
]

DOCTOR_E_PRESCRIPTIONS = [
    {
        "patient": "Arun Kumar",
        "date": "Feb 25, 2026",
        "diagnosis": "Primary Hypertension",
        "status": "ACTIVE",
        "medicines": [
            {"name": "Amlodipine 5mg", "note": "Once daily after breakfast"},
            {"name": "Telmisartan 40mg", "note": "Once daily at night"},
        ],
    },
    {
        "patient": "Meera Nair",
        "date": "Feb 21, 2026",
        "diagnosis": "Type-2 Diabetes Management",
        "status": "ACTIVE",
        "medicines": [
            {"name": "Metformin 500mg", "note": "Twice daily with meals"},
            {"name": "Glimepiride 1mg", "note": "Once daily before breakfast"},
        ],
    },
    {
        "patient": "Sana Shaik",
        "date": "Feb 18, 2026",
        "diagnosis": "Migraine Episode",
        "status": "REVIEW",
        "medicines": [
            {"name": "Sumatriptan 50mg", "note": "As needed for severe episodes"},
            {"name": "Naproxen 250mg", "note": "After food, if pain persists"},
        ],
    },
]

DOCTOR_REPORTS = [
    {
        "title": "Weekly Consultations",
        "period": "Week 9, 2026",
        "summary": "18 completed • 2 rescheduled",
        "metric": "90% completion",
    },
    {
        "title": "Prescription Compliance",
        "period": "Last 30 days",
        "summary": "74% patients followed medication plan",
        "metric": "High adherence",
    },
    {
        "title": "Patient Follow-ups",
        "period": "Last 14 days",
        "summary": "11 follow-ups completed",
        "metric": "2 pending",
    },
]


def doctor_dashboard(request):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    # fetch doctor rating if model/table exists; the table may not exist until
    # migrations are run, so catch OperationalError to avoid crashing.
    rating = None
    try:
        rating = Doctor.objects.get(name=doctor_name).rating
    except Doctor.DoesNotExist:
        # doctor record not in DB yet; leave rating as None
        rating = None
    except Exception as err:  # broad catch for DB errors like missing table
        from django.db import utils as db_utils

        if isinstance(err, db_utils.OperationalError):
            # likely migrations not applied; skip rating lookup
            rating = None
        else:
            raise

    # prepare appointments for dashboard: enable join when appointment time
    # matches current local time (to the minute)
    now = datetime.now()
    appointments_for_dashboard = []
    for appt in _db_filtered_appointments():
        item = appt.copy()
        # Build a parseable datetime string if date parts are present
        join_enabled = False
        try:
            day = item.get("day")
            month = item.get("month")
            year = item.get("year")
            time_str = item.get("time")
            if day and month and year and time_str:
                month_short = MONTH_MAP.get(month.upper(), month)
                dt_str = f"{day} {month_short} {year} {time_str}"
                appt_dt = datetime.strptime(dt_str, "%d %b %Y %I:%M %p")
                # join when date+time matches current to the minute
                if appt_dt.strftime("%d %b %Y %I:%M %p") == now.strftime("%d %b %Y %I:%M %p"):
                    join_enabled = True
        except Exception:
            join_enabled = False

        item["join_enabled"] = join_enabled
        item["join_color"] = "red" if join_enabled else "white"
        appointments_for_dashboard.append(item)

    return render(
        request,
        "dashboard/pages/doctor/doctor_dashboard.html",
        {
            "doctor_name": doctor_name,
            "active": "dashboard",
            "rating": rating,
            "schedule": DOCTOR_SCHEDULE,
            "appointments": appointments_for_dashboard,
        },
    )


def doctor_join_call(request, appointment_index):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    if not (0 <= appointment_index < len(DOCTOR_APPOINTMENTS)):
        return redirect("doctor_dashboard")

    appointment = DOCTOR_APPOINTMENTS[appointment_index]
    # Determine if join is allowed (same logic as dashboard)
    now = datetime.now()
    join_allowed = False
    try:
        day = appointment.get("day")
        month = appointment.get("month")
        year = appointment.get("year")
        time_str = appointment.get("time")
        if day and month and year and time_str:
            month_short = MONTH_MAP.get(month.upper(), month)
            dt_str = f"{day} {month_short} {year} {time_str}"
            appt_dt = datetime.strptime(dt_str, "%d %b %Y %I:%M %p")
            if appt_dt.strftime("%d %b %Y %I:%M %p") == now.strftime("%d %b %Y %I:%M %p"):
                join_allowed = True
    except Exception:
        join_allowed = False

    # In a real app we'd redirect to a video call provider / room.
    # Here render a simple page that simulates joining the call.
    return render(
        request,
        "dashboard/pages/doctor/join_call.html",
        {
            "doctor_name": doctor_name,
            "appointment": appointment,
            "join_allowed": join_allowed,
        },
    )


def doctor_appointments(request):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    pending_count = 0
    active_appointments = []
    for appointment in _db_filtered_appointments():
        if appointment.get("status") == "PENDING":
            pending_count += 1
        if appointment.get("status") in {"COMPLETED", "REJECTED"}:
            continue

        item = appointment.copy()
        active_appointments.append(item)

    return render(
        request,
        "dashboard/pages/doctor/doctor_appointments.html",
        {
            "doctor_name": doctor_name,
            "active": "appointments",
            "appointments": active_appointments,
            "pending_count": pending_count,
        },
    )


def doctor_user_pendings(request):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    reminders = []
    for appointment in _db_filtered_appointments():
        if appointment.get("status") == "PENDING":
            item = appointment.copy()
            reminders.append(item)

    return render(
        request,
        "dashboard/pages/doctor/doctor_reminders.html",
        {
            "doctor_name": doctor_name,
            "active": "appointments",
            "reminders": reminders,
        },
    )


def doctor_accept_appointment(request, appointment_index):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    if request.method == "POST" and 0 <= appointment_index < len(DOCTOR_APPOINTMENTS):
        DOCTOR_APPOINTMENTS[appointment_index]["status"] = "CONFIRMED"

    return redirect("doctor_user_pendings")


def doctor_reject_appointment(request, appointment_index):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    if request.method == "POST" and 0 <= appointment_index < len(DOCTOR_APPOINTMENTS):
        DOCTOR_APPOINTMENTS[appointment_index]["status"] = "REJECTED"

    return redirect("doctor_user_pendings")


def doctor_pending_patient_detail(request, appointment_index):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    patient = None
    if 0 <= appointment_index < len(DOCTOR_APPOINTMENTS):
        appointment = DOCTOR_APPOINTMENTS[appointment_index]
        appointment_patient_name = appointment.get(
            "patient", "").strip().lower()

        for known_patient in _db_patient_cards():
            if known_patient.get("name", "").strip().lower() == appointment_patient_name:
                patient = known_patient
                break

    return render(
        request,
        "dashboard/pages/doctor/doctor_patient_detail.html",
        {
            "doctor_name": doctor_name,
            "active": "appointments",
            "patient": patient,
            "patient_index": appointment_index,
        },
    )


def doctor_patients(request):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    prescription_map = {}
    for prescription in _db_filtered_prescriptions():
        patient_key = prescription.get("patient", "").strip().lower()
        medicine_names = [
            medicine.get("name", "")
            for medicine in prescription.get("medicines", [])
            if medicine.get("name")
        ]
        summary = ", ".join(
            medicine_names) if medicine_names else "No medicines listed"
        prescription_map[patient_key] = f"{prescription.get('diagnosis', 'Prescription')}: {summary}"

    patient_cards = []
    for idx, patient in enumerate(_db_patient_cards()):
        item = patient.copy()
        patient_key = patient.get("name", "").strip().lower()
        item["prescription_summary"] = prescription_map.get(
            patient_key,
            "No e-prescription available",
        )
        item["patient_index"] = idx
        patient_cards.append(item)

    return render(
        request,
        "dashboard/pages/doctor/doctor_patients.html",
        {
            "doctor_name": doctor_name,
            "active": "patients",
            "patients": patient_cards,
        },
    )


def doctor_patient_detail(request, patient_index):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    patient = None
    db_patients = _db_patient_cards()
    if 0 <= patient_index < len(db_patients):
        patient = db_patients[patient_index]

    return render(
        request,
        "dashboard/pages/doctor/doctor_patient_detail.html",
        {
            "doctor_name": doctor_name,
            "active": "patients",
            "patient": patient,
            "patient_index": patient_index,
        },
    )


def doctor_patient_prescription(request, patient_index):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    patient = None
    prescriptions = []
    prescriptions_display = []
    timing_status = {
        "before_breakfast": False,
        "after_breakfast": False,
        "lunch": False,
        "before_dinner": False,
        "after_dinner": False,
    }

    db_patients = _db_patient_cards()
    if 0 <= patient_index < len(db_patients):
        patient = db_patients[patient_index]
        patient_key = patient.get("name", "").strip().lower()

        for prescription in _db_filtered_prescriptions():
            if prescription.get("patient", "").strip().lower() == patient_key:
                prescriptions.append(prescription)

    def _timing_flags(note):
        normalized = (note or "").strip().lower()
        return {
            "before_breakfast": "before breakfast" in normalized or "empty stomach" in normalized,
            "after_breakfast": "after breakfast" in normalized,
            "lunch": "lunch" in normalized,
            "before_dinner": "before dinner" in normalized,
            "after_dinner": "after dinner" in normalized or "at night" in normalized,
        }

    for prescription in prescriptions:
        display_prescription = prescription.copy()
        display_medicines = []
        for medicine in prescription.get("medicines", []):
            flags = _timing_flags(medicine.get("note", ""))

            if flags["before_breakfast"]:
                timing_status["before_breakfast"] = True
            if flags["after_breakfast"]:
                timing_status["after_breakfast"] = True
            if flags["lunch"]:
                timing_status["lunch"] = True
            if flags["before_dinner"]:
                timing_status["before_dinner"] = True
            if flags["after_dinner"]:
                timing_status["after_dinner"] = True

            display_medicines.append({
                "name": medicine.get("name", "Medicine"),
                "timing_flags": flags,
            })

        display_prescription["medicines_display"] = display_medicines
        prescriptions_display.append(display_prescription)

    timing_slots = [
        {
            "label": "Before Breakfast",
            "checked": timing_status["before_breakfast"],
        },
        {
            "label": "After Breakfast",
            "checked": timing_status["after_breakfast"],
        },
        {
            "label": "Lunch",
            "checked": timing_status["lunch"],
        },
        {
            "label": "Before Dinner",
            "checked": timing_status["before_dinner"],
        },
        {
            "label": "After Dinner",
            "checked": timing_status["after_dinner"],
        },
    ]

    return render(
        request,
        "dashboard/pages/doctor/doctor_patient_prescription.html",
        {
            "doctor_name": doctor_name,
            "active": "patients",
            "patient": patient,
            "prescriptions": prescriptions_display,
            "timing_slots": timing_slots,
        },
    )


def doctor_e_prescriptions(request):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    return render(
        request,
        "dashboard/pages/doctor/doctor_e_prescriptions.html",
        {
            "doctor_name": doctor_name,
            "active": "e_prescriptions",
            "prescriptions": _db_filtered_prescriptions(),
        },
    )


def doctor_reports(request):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    return render(
        request,
        "dashboard/pages/doctor/doctor_reports.html",
        {
            "doctor_name": doctor_name,
            "active": "reports",
            "reports": DOCTOR_REPORTS,
            "report_totals": {
                "consultations": len(_db_filtered_appointments()),
                "patients": len(_db_patient_cards()),
                "prescriptions": len(_db_filtered_prescriptions()),
            },
        },
    )


def doctor_generate_report(request):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    completed_consultations = sum(
        1 for appointment in DOCTOR_APPOINTMENTS
        if appointment.get("status") == "COMPLETED"
    )
    pending_consultations = sum(
        1 for appointment in DOCTOR_APPOINTMENTS
        if appointment.get("status") == "PENDING"
    )
    report_data = {
        "generated_at": datetime.now().strftime("%b %d, %Y %I:%M %p"),
        "consultations": len(DOCTOR_APPOINTMENTS),
        "completed_consultations": completed_consultations,
        "pending_consultations": pending_consultations,
        "patients": len(DOCTOR_PATIENTS),
        "e_prescriptions": len(DOCTOR_E_PRESCRIPTIONS),
        "summary": "Report generated using the latest appointment, patient, and prescription data.",
    }

    return render(
        request,
        "dashboard/pages/doctor/doctor_report_generated.html",
        {
            "doctor_name": doctor_name,
            "active": "reports",
            "report_data": report_data,
        },
    )


def doctor_report_detail(request, report_index):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    report = None
    if 0 <= report_index < len(DOCTOR_REPORTS):
        report = DOCTOR_REPORTS[report_index]

    return render(
        request,
        "dashboard/pages/doctor/doctor_report_detail.html",
        {
            "doctor_name": doctor_name,
            "active": "reports",
            "report": report,
        },
    )


def signout(request):
    request.session.pop("patient_name", None)
    request.session.pop("admin_name", None)
    request.session.pop("doctor_name", None)
    return redirect("home")
