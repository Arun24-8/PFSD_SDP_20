from django.contrib import admin

from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating')
    search_fields = ('name',)

# Register your doctor app models here. For now, there are no models to register.
