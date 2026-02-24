import re

from django.shortcuts import render, redirect


def _name_from_email(email):
    local_part = (email or "").split("@", 1)[0].strip()
    cleaned = re.sub(r"[._-]+", " ", local_part)
    normalized = " ".join(cleaned.split())
    return normalized.title() if normalized else "Patient"


def home(request):
    patient_name = request.session.get("patient_name")
    return render(
        request,
        "dashboard/pages/home.html",
        {
            "patient_name": patient_name,
        },
    )


def features(request):
    return redirect("/#features")


def patient_dashboard(request):
    patient_name = request.session.get("patient_name")
    if not patient_name:
        return redirect("login")

    return render(
        request,
        "dashboard/pages/patient_dashboard.html",
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
        else:
            request.session.pop("patient_name", None)

        return redirect("home")

    return render(request, "dashboard/pages/login.html")


def signout(request):
    request.session.pop("patient_name", None)
    return redirect("home")
