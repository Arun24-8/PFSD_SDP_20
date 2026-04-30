"""
URL configuration for mediconnect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from doctor import views as doctor_views

urlpatterns = [
    path('', doctor_views.home, name='home'),
    path('features/', doctor_views.features, name='features'),
    path('login/', doctor_views.login, name='login'),
    path('signout/', doctor_views.signout, name='signout'),

    path('patient/', include('patient.urls')),
    path('doctor/', include('doctor.urls')),
    path('admin/', include('admin_management.urls')),
    path('admin-panel/', admin.site.urls),
]
