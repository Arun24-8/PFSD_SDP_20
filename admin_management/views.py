from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import AdminProfile

# Create your views here.

def is_admin(request):
    """Check if user is logged in as admin"""
    return request.session.get("admin_name") is not None


def admin_dashboard(request):
    """Display admin dashboard"""
    if not is_admin(request):
        return redirect('login')
    
    admin_name = request.session.get("admin_name")
    context = {
        'admin_profile': {
            'user': {
                'first_name': admin_name.split()[0] if admin_name else 'Admin',
                'last_name': ' '.join(admin_name.split()[1:]) if len(admin_name.split()) > 1 else ''
            }
        },
    }
    return render(request, 'dashboard/pages/admin_dashboard.html', context)


def manage_users(request):
    """Manage users in the system"""
    if not is_admin(request):
        return redirect('login')
    
    users = User.objects.all()
    context = {
        'users': users,
    }
    return render(request, 'dashboard/pages/manage_users.html', context)


def view_reports(request):
    """View system reports"""
    if not is_admin(request):
        return redirect('login')
    
    context = {}
    return render(request, 'dashboard/pages/view_reports.html', context)


def security_settings(request):
    """Manage security settings"""
    if not is_admin(request):
        return redirect('login')
    
    context = {}
    return render(request, 'dashboard/pages/security_settings.html', context)

