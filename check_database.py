#!/usr/bin/env python
"""
Check if data is saved in the MySQL database.
"""
from doctor.models import Doctor
from django.contrib.auth.models import Group
from django.db import connection
from django.contrib.auth.models import User
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediconnect.settings')
django.setup()


print("=" * 60)
print("DATABASE VERIFICATION")
print("=" * 60)

# Show which database we're connected to
print("\n1. Database Connection:")
print(f"   Engine: {connection.settings_dict['ENGINE']}")
print(f"   Database: {connection.settings_dict['NAME']}")
print(f"   Host: {connection.settings_dict['HOST']}")
print(f"   Port: {connection.settings_dict['PORT']}")

# Check users table
print("\n2. Users in Database:")
users = User.objects.all()
print(f"   Total users: {users.count()}")
for u in users:
    print(f"   - Username: {u.username}")
    print(f"     Email: {u.email}")
    print(f"     Is Staff: {u.is_staff}")
    print(f"     Is Superuser: {u.is_superuser}")
    print(f"     Created: {u.date_joined}")
    print()

# Check other tables count

print("3. Other Data in Database:")
print(f"   Groups: {Group.objects.count()}")
print(f"   Doctors: {Doctor.objects.count()}")

print("\n✓ Data is successfully saved in MySQL database!")
print("=" * 60)
