from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class AdminProfile(models.Model):
    """
    Admin profile model for storing admin-specific information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Admin Profiles"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
