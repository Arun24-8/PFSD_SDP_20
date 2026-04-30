from django.db import models


class Doctor(models.Model):
    """Simple doctor profile storing name and rating."""

    name = models.CharField(max_length=100, unique=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    email = models.EmailField(max_length=255, unique=True)

    def __str__(self):
        return self.name


# Add doctor-related models here if needed
