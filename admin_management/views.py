from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime, timedelta
import csv

from .models import AdminProfile
from .forms import AdminUserCreationForm, AdminUserChangeForm

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


def add_user(request):
    """Create a new user"""
    if not is_admin(request):
        return redirect('login')

    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('manage_users')
    else:
        form = AdminUserCreationForm()

    return render(request, 'dashboard/pages/user_form.html', {'form': form, 'title': 'Add User'})


def edit_user(request, user_id):
    """Edit an existing user"""
    if not is_admin(request):
        return redirect('login')

    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = AdminUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('manage_users')
    else:
        form = AdminUserChangeForm(instance=user)

    return render(request, 'dashboard/pages/user_form.html', {'form': form, 'title': 'Edit User'})


def view_user(request, user_id):
    """View details of a single user"""
    if not is_admin(request):
        return redirect('login')

    user = get_object_or_404(User, pk=user_id)
    return render(request, 'dashboard/pages/view_user.html', {'user_obj': user})


def delete_user(request, user_id):
    """Delete a user from the system"""
    if not is_admin(request):
        return redirect('login')

    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('manage_users')

    return render(request, 'dashboard/pages/confirm_delete.html', {'object': user, 'type': 'user'})


def view_reports(request):
    """View system reports"""
    if not is_admin(request):
        return redirect('login')
    
    # Get filter parameters
    frequency = request.GET.get('frequency', 'Daily')
    date_range = request.GET.get('date_range', 'Last 7 Days')
    
    # Calculate date range
    end_date = datetime.now()
    if date_range == 'Last 7 Days':
        start_date = end_date - timedelta(days=7)
    elif date_range == 'Last 30 Days':
        start_date = end_date - timedelta(days=30)
    elif date_range == 'Last 90 Days':
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=7)
    
    # Generate report data
    report_data = {
        'frequency': frequency,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'consultations': 487,  # Placeholder - would come from actual consultation model
        'revenue': 12450,  # Placeholder
        'avg_rating': 4.8,  # Placeholder
        'growth': 23,  # Placeholder
    }
    
    context = {
        'report_data': report_data,
        'frequency': frequency,
        'date_range': date_range,
    }
    return render(request, 'dashboard/pages/view_reports.html', context)


def generate_report(request):
    """Generate system report"""
    if not is_admin(request):
        return redirect('login')
    
    # Handle both GET and POST
    frequency = request.GET.get('frequency') or request.POST.get('frequency', 'Daily')
    date_range = request.GET.get('date_range') or request.POST.get('date_range', 'Last 7 Days')
    
    # Calculate date range
    end_date = datetime.now()
    if date_range == 'Last 7 Days':
        start_date = end_date - timedelta(days=7)
    elif date_range == 'Last 30 Days':
        start_date = end_date - timedelta(days=30)
    elif date_range == 'Last 90 Days':
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=7)
    
    # Generate report data
    report_data = {
        'frequency': frequency,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'consultations': 487,
        'revenue': 12450,
        'avg_rating': 4.8,
        'growth': 23,
    }
    
    context = {
        'report_data': report_data,
        'frequency': frequency,
        'date_range': date_range,
    }
    return render(request, 'dashboard/pages/view_reports.html', context)


def export_report(request):
    """Export system report as CSV"""
    if not is_admin(request):
        return redirect('login')
    
    # Get filter parameters
    frequency = request.GET.get('frequency', 'Daily')
    date_range = request.GET.get('date_range', 'Last 7 Days')
    
    # Calculate date range
    end_date = datetime.now()
    if date_range == 'Last 7 Days':
        start_date = end_date - timedelta(days=7)
    elif date_range == 'Last 30 Days':
        start_date = end_date - timedelta(days=30)
    elif date_range == 'Last 90 Days':
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=7)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow(['MediConnect System Report'])
    writer.writerow(['Generated on', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['Frequency', frequency])
    writer.writerow(['Date Range', date_range])
    writer.writerow(['Period', f'{start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}'])
    writer.writerow([])
    
    # Write summary statistics
    writer.writerow(['SUMMARY STATISTICS'])
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total Users', User.objects.count()])
    writer.writerow(['Active Users', User.objects.filter(is_active=True).count()])
    writer.writerow(['Staff Members', User.objects.filter(is_staff=True).count()])
    writer.writerow(['Consultations This Month', 487])
    writer.writerow(['Revenue This Month', '$12,450'])
    writer.writerow(['Average Rating', 4.8])
    writer.writerow(['Month over Month Growth', '+23%'])
    writer.writerow([])
    
    # Write user list
    writer.writerow(['USER LIST'])
    writer.writerow(['Username', 'Email', 'First Name', 'Last Name', 'Status', 'Staff', 'Date Joined'])
    users = User.objects.all()
    for user in users:
        writer.writerow([
            user.username,
            user.email,
            user.first_name,
            user.last_name,
            'Active' if user.is_active else 'Inactive',
            'Yes' if user.is_staff else 'No',
            user.date_joined.strftime('%Y-%m-%d'),
        ])
    
    return response


def security_settings(request):
    """Manage security settings"""
    if not is_admin(request):
        return redirect('login')
    
    context = {}
    return render(request, 'dashboard/pages/security_settings.html', context)

