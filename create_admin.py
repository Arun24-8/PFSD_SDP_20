#!/usr/bin/env python
"""
Create an admin superuser non-interactively.
Edit these values:
"""
from django.contrib.auth.models import User
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediconnect.settings')
django.setup()


# Set these values:
admin_username = "admin"
admin_email = "admin@gmail.com"
admin_password = "Admin@123"

# Create or update the superuser
try:
    user, created = User.objects.get_or_create(username=admin_username)
    user.email = admin_email
    user.is_staff = True
    user.is_superuser = True
    user.set_password(admin_password)
    user.save()

    if created:
        print(f"✓ Superuser created: {admin_username}")
    else:
        print(f"✓ Superuser updated: {admin_username}")

    print(f"  Username: {admin_username}")
    print(f"  Email: {admin_email}")
    print(f"  Password: {admin_password}")

except Exception as e:
    print(f"✗ Error: {e}")
    import sys
    sys.exit(1)
