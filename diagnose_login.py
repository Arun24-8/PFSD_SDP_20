#!/usr/bin/env python
"""
Diagnose login issues by checking database users.
"""
from django.contrib.auth.models import User
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediconnect.settings')
django.setup()


print("=" * 70)
print("LOGIN DIAGNOSTIC REPORT")
print("=" * 70)

# Get all users
users = User.objects.all()
print(f"\nTotal users in database: {users.count()}\n")

for u in users:
    print(f"Username: {u.username}")
    print(f"Email: {u.email}")
    print(f"Created: {u.date_joined}")
    print(f"Is Staff: {u.is_staff}")
    print("-" * 70)

print("\nTo login, use one of these combinations:")
print("- Username field: [username] (from Username column above)")
print("- OR Email field: [email] (from Email column above)")
print("=" * 70)
