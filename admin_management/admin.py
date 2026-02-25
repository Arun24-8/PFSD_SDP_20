from django.contrib import admin
from .models import AdminProfile

# Register your models here.

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'department', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'employee_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Admin Details', {
            'fields': ('employee_id', 'department', 'phone_number', 'address')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
