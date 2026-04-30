from django.conf import settings
from django.db import models


class Doctor(models.Model):
    """Simple doctor profile storing name and rating."""

    name = models.CharField(max_length=100, unique=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    email = models.EmailField(max_length=255, unique=True)
    specialist_type = models.CharField(max_length=100, default="General Medicine")
    timings = models.TextField(default="")

    def __str__(self):
        return self.name


class Appointment(models.Model):
    """Patient booking assigned to one doctor."""

    STATUS_PENDING = "PENDING"
    STATUS_CONFIRMED = "CONFIRMED"
    STATUS_REJECTED = "REJECTED"
    STATUS_COMPLETED = "COMPLETED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_COMPLETED, "Completed"),
    ]

    MODE_CHOICES = [
        ("Video Call", "Video Call"),
        ("In-Person", "In-Person"),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_appointments",
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    reason = models.CharField(max_length=255, default="General consultation")
    appointment_date = models.DateField()
    appointment_time = models.CharField(max_length=20)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default="Video Call")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["appointment_date", "appointment_time", "created_at"]

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.appointment_date}"


class Prescription(models.Model):
    """Medication plan issued by a doctor for a real patient."""

    STATUS_ACTIVE = "ACTIVE"
    STATUS_COMPLETED = "COMPLETED"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_COMPLETED, "Completed"),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="prescriptions",
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="prescriptions",
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prescriptions",
    )
    diagnosis = models.CharField(max_length=255)
    medicines = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )
    issued_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-issued_at", "-id"]

    def __str__(self):
        return f"{self.diagnosis} for {self.patient}"
