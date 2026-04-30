#!/usr/bin/env python
"""
Create patient accounts in the database.
Edit the patients list below to add more patients.
"""
from django.contrib.auth.models import User
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediconnect.settings')
django.setup()


# List of patients to create
patients = [
    {
        "username": "arun.kumar",
        "email": "arun.kumar@patient.com",
        "password": "Patient@123"
    },
    {
        "username": "meera.nair",
        "email": "meera.nair@patient.com",
        "password": "Patient@123"
    },
    {
        "username": "rahul.verma",
        "email": "rahul.verma@patient.com",
        "password": "Patient@123"
    },
    {
        "username": "sana.shaik",
        "email": "sana.shaik@patient.com",
        "password": "Patient@123"
    },
]

print("=" * 70)
print("CREATING PATIENT ACCOUNTS")
print("=" * 70)

created_count = 0
updated_count = 0

for patient in patients:
    try:
        username = patient["username"]
        email = patient["email"]
        password = patient["password"]

        # Create or update the patient user
        user, created = User.objects.get_or_create(username=username)
        user.email = email
        user.is_staff = False
        user.is_superuser = False
        user.set_password(password)
        user.save()

        if created:
            created_count += 1
            status = "✓ CREATED"
        else:
            updated_count += 1
            status = "✓ UPDATED"

        print(f"\n{status}")
        print(f"  Username: {username}")
        print(f"  Email: {email}")
        print(f"  Password: {password}")

    except Exception as e:
        print(f"\n✗ ERROR: {username}")
        print(f"  {e}")

print("\n" + "=" * 70)
print(f"Summary: {created_count} created, {updated_count} updated")
print("=" * 70)
print("\n✓ All patient accounts are now saved in the MySQL database!")
print("\nYou can login using:")
print("  Role: Patient")
print("  Username/Email: (any of the above)")
print("  Password: (the password you set)")
print("=" * 70)
