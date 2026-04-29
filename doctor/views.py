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
                doctor_obj, created = Doctor.objects.get_or_create(
                    name=doctor_name)
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

DOCTOR_APPOINTMENTS = [
    {
        "date_label": "MON",
        "day": "04",
        "month": "APR",
        "year": "2026",
        "patient": "Arun Kumar",
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

    pending_count = 0
    active_appointments = []
    for appointment_index, appointment in enumerate(DOCTOR_APPOINTMENTS):
        if appointment.get("status") == "PENDING":
            pending_count += 1
        if appointment.get("status") in {"COMPLETED", "REJECTED"}:
            continue

        item = appointment.copy()
        item["appointment_index"] = appointment_index
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
    for appointment_index, appointment in enumerate(DOCTOR_APPOINTMENTS):
        if appointment.get("status") == "PENDING":
            item = appointment.copy()
            item["appointment_index"] = appointment_index
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

        for known_patient in DOCTOR_PATIENTS:
            if known_patient.get("name", "").strip().lower() == appointment_patient_name:
                patient = known_patient
                break

        if patient is None:
            patient = {
                "name": appointment.get("patient", "Patient"),
                "age": "N/A",
                "gender": "N/A",
                "condition": appointment.get("reason", "Pending consultation"),
                "last_visit": "N/A",
                "risk": "Pending",
            }

    return render(
        request,
        "dashboard/pages/doctor/doctor_patient_detail.html",
        {
            "doctor_name": doctor_name,
            "active": "appointments",
            "patient": patient,
        },
    )


def doctor_patients(request):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    prescription_map = {}
    for prescription in DOCTOR_E_PRESCRIPTIONS:
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
    for patient in DOCTOR_PATIENTS:
        item = patient.copy()
        patient_key = patient.get("name", "").strip().lower()
        item["prescription_summary"] = prescription_map.get(
            patient_key,
            "No e-prescription available",
        )
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
    if 0 <= patient_index < len(DOCTOR_PATIENTS):
        patient = DOCTOR_PATIENTS[patient_index]

    return render(
        request,
        "dashboard/pages/doctor/doctor_patient_detail.html",
        {
            "doctor_name": doctor_name,
            "active": "patients",
            "patient": patient,
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

    if 0 <= patient_index < len(DOCTOR_PATIENTS):
        patient = DOCTOR_PATIENTS[patient_index]
        patient_key = patient.get("name", "").strip().lower()

        for prescription in DOCTOR_E_PRESCRIPTIONS:
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
            "prescriptions": DOCTOR_E_PRESCRIPTIONS,
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
                "consultations": len(DOCTOR_APPOINTMENTS),
                "patients": len(DOCTOR_PATIENTS),
                "prescriptions": len(DOCTOR_E_PRESCRIPTIONS),
            },
        },
    )


def signout(request):
    request.session.pop("patient_name", None)
    request.session.pop("admin_name", None)
    request.session.pop("doctor_name", None)
    return redirect("home")
