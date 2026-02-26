from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class AdminUserCreationForm(UserCreationForm):
    """Form for administrators to create new users"""

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
        )


class AdminUserChangeForm(UserChangeForm):
    """Form for administrators to update existing users"""

    password = None  # hide the password field since we don't edit it here

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
        )
