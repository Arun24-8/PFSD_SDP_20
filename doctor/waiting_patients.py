from django.shortcuts import render, redirect
from .views import DOCTOR_APPOINTMENTS


def waiting_patients(request):
    doctor_name = request.session.get("doctor_name")
    if not doctor_name:
        return redirect("login")

    waiting = []
    for idx, a in enumerate(DOCTOR_APPOINTMENTS):
        if a.get("status") == "PENDING":
            item = a.copy()
            item["idx"] = idx
            waiting.append(item)

    return render(request, "dashboard/pages/doctor/waiting_patients.html", {"doctor_name": doctor_name, "waiting": waiting, "active": "waiting"})
