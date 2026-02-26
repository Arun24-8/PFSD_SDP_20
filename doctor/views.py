import re

from django.shortcuts import render, redirect


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
    return render(
        request,
        "dashboard/pages/doctor/home.html",
        {
            "patient_name": patient_name,
            "admin_name": admin_name,
        },
    )


def features(request):
    return render(request, "dashboard/pages/doctor/features_only.html")


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
            request.session["doctor_name"] = _name_from_email(email)
            # Redirect to doctor dashboard when created
            return redirect("home")
        else:
            request.session.pop("patient_name", None)
            request.session.pop("admin_name", None)
            request.session.pop("doctor_name", None)

        return redirect("home")

    return render(request, "dashboard/pages/dashboard/login.html")


def signout(request):
    request.session.pop("patient_name", None)
    request.session.pop("admin_name", None)
    request.session.pop("doctor_name", None)
    return redirect("home")
