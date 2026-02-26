import re
import random

from django.shortcuts import render, redirect
from .models import Doctor


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



def home(request):
    patient_name = request.session.get("patient_name")
    admin_name = request.session.get("admin_name")
    doctor_name = request.session.get("doctor_name")
    return render(
        request,
        "dashboard/pages/doctor/home.html",
        {
            "patient_name": patient_name,
            "admin_name": admin_name,
            "doctor_name": doctor_name,
        },
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

    return render(
        request,
        "dashboard/pages/patient/patient_dashboard.html",
        {
            "patient_name": patient_name,
        },
    )


def patient_appointments(request):
    patient_name = request.session.get("patient_name")
    if not patient_name:
        return redirect("login")

    return render(
        request,
        "dashboard/pages/patient/appointments.html",
        {
            "patient_name": patient_name,
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
            "doctors": PATIENT_BOOKING_DOCTORS,
        },
    )


def patient_prescriptions(request):
    patient_name = request.session.get("patient_name")
    if not patient_name:
        return redirect("login")

    return render(
        request,
        "dashboard/pages/patient/prescriptions.html",
        {
            "patient_name": patient_name,
        },
    )


def login(request):
    if request.method == "POST":
        role = request.POST.get("role", "patient")
        email = request.POST.get("email", "")

        if role == "patient":
            request.session["patient_name"] = _name_from_email(email)
            return redirect("patient_dashboard")
        elif role == "admin":
            request.session["admin_name"] = _name_from_email(email)
            return redirect("admin_dashboard")
        elif role == "doctor":
            doctor_name = _name_from_email(email)
            request.session["doctor_name"] = doctor_name
            # ensure a Doctor record exists with a rating; pick random if new
            try:
                doctor_obj, created = Doctor.objects.get_or_create(name=doctor_name)
                if created:
                    doctor_obj.rating = round(random.uniform(4.0, 5.0), 2)
                    doctor_obj.save()
            except Exception as err:
                # avoid crashing when table does not yet exist
                from django.db import utils as db_utils

                if isinstance(err, db_utils.OperationalError):
                    pass
                else:
                    raise
            return redirect("doctor_dashboard")
        else:
            request.session.pop("patient_name", None)
            request.session.pop("admin_name", None)
            request.session.pop("doctor_name", None)

        return redirect("home")

    return render(request, "dashboard/pages/dashboard/login.html")


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

    return render(
        request,
        "dashboard/pages/doctor/doctor_dashboard.html",
        {
            "doctor_name": doctor_name,
            "active": "dashboard",
            "rating": rating,
            "schedule": DOCTOR_SCHEDULE,
        },
    )


def doctor_appointments(request):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    return render(
        request,
        "dashboard/pages/doctor/doctor_appointments.html",
        {"doctor_name": doctor_name, "active": "appointments"},
    )


def doctor_patients(request):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    return render(
        request,
        "dashboard/pages/doctor/doctor_patients.html",
        {"doctor_name": doctor_name, "active": "patients"},
    )


def doctor_consultations(request):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    return render(
        request,
        "dashboard/pages/doctor/doctor_consultations.html",
        {"doctor_name": doctor_name, "active": "consultations"},
    )


def doctor_e_prescriptions(request):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    return render(
        request,
        "dashboard/pages/doctor/doctor_e_prescriptions.html",
        {"doctor_name": doctor_name, "active": "e_prescriptions"},
    )


def doctor_notifications(request):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    return render(
        request,
        "dashboard/pages/doctor/doctor_notifications.html",
        {"doctor_name": doctor_name, "active": "notifications"},
    )


def doctor_reports(request):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    return render(
        request,
        "dashboard/pages/doctor/doctor_reports.html",
        {"doctor_name": doctor_name, "active": "reports"},
    )


def doctor_profile(request):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    return render(
        request,
        "dashboard/pages/doctor/doctor_profile.html",
        {"doctor_name": doctor_name, "active": "profile"},
    )


def signout(request):
    request.session.pop("patient_name", None)
    request.session.pop("admin_name", None)
    request.session.pop("doctor_name", None)
    return redirect("home")
