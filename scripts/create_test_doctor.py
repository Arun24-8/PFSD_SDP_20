from django.contrib.auth.models import User, Group
from doctor.models import Doctor

# create group
g, _ = Group.objects.get_or_create(name='Doctor')

u, created = User.objects.get_or_create(username='john.doe@doctor.local', defaults={'email':'john.doe@doctor.local','first_name':'John','last_name':'Doe','is_active':True})
if created:
    u.set_password('Secret123')
    u.save()
u.groups.add(g)
Doctor.objects.get_or_create(name='John Doe', defaults={'rating':'4.5'})
print('setup_done')
