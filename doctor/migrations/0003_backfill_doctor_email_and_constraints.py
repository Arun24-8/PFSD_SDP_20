import re

from django.db import migrations, models


def backfill_doctor_email(apps, schema_editor):
    Doctor = apps.get_model("doctor", "Doctor")
    User = apps.get_model("auth", "User")

    used_emails = {
        (doctor.email or "").strip().lower()
        for doctor in Doctor.objects.exclude(email__isnull=True).exclude(email="")
    }

    user_email_by_full_name = {}
    for user in User.objects.exclude(email__isnull=True).exclude(email=""):
        full_name = f"{(user.first_name or '').strip()} {(user.last_name or '').strip()}".strip().lower()
        if full_name and full_name not in user_email_by_full_name:
            user_email_by_full_name[full_name] = user.email.strip().lower()

    for doctor in Doctor.objects.filter(email__isnull=True) | Doctor.objects.filter(email=""):
        doctor_name = (doctor.name or "").strip()
        lookup_name = doctor_name.lower()
        email = user_email_by_full_name.get(lookup_name)

        if not email:
            base = re.sub(r"[^a-z0-9]+", ".", lookup_name).strip(".") or f"doctor.{doctor.pk}"
            email = f"{base}@doctor.mediconnect.local"
            suffix = 1
            while email in used_emails:
                email = f"{base}.{suffix}@doctor.mediconnect.local"
                suffix += 1

        doctor.email = email
        doctor.save(update_fields=["email"])
        used_emails.add(email)


class Migration(migrations.Migration):

    dependencies = [
        ("doctor", "0002_doctor_email"),
    ]

    operations = [
        migrations.RunPython(backfill_doctor_email, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="doctor",
            name="email",
            field=models.EmailField(max_length=255, unique=True),
        ),
    ]
