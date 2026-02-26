from django.test import TestCase
from django.contrib.auth.models import User
from .models import AdminProfile

# Create your tests here.

class AdminProfileTestCase(TestCase):
    """Test cases for AdminProfile model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Admin'
        )
        self.admin_profile = AdminProfile.objects.create(
            user=self.user,
            employee_id='ADM001',
            department='Management',
            phone_number='1234567890'
        )

    def test_admin_profile_creation(self):
        """Test admin profile creation"""
        self.assertEqual(self.admin_profile.user.username, 'testadmin')
        self.assertEqual(self.admin_profile.employee_id, 'ADM001')

    def test_admin_string_representation(self):
        """Test admin string representation"""
        self.assertEqual(str(self.admin_profile), 'Test Admin')


class AdminViewsTestCase(TestCase):
    """Ensure the admin CRUD views work as expected"""

    def setUp(self):
        # create an admin user and set session flag
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='pass',
            is_staff=True,
            first_name='Admin',
            last_name='User',
        )
        self.client.force_login(self.admin_user)
        session = self.client.session
        session['admin_name'] = 'Admin User'
        session.save()

    def test_manage_users_view(self):
        response = self.client.get('/admin/manage-users/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Manage Users')

    def test_add_user_view_get_and_post(self):
        # GET should return form
        response = self.client.get('/admin/manage-users/add/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form')

        # POST create a user
        data = {
            'username': 'newuser',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new@example.com',
            'is_staff': False,
            'is_active': True,
        }
        response = self.client.post('/admin/manage-users/add/', data, follow=True)
        self.assertRedirects(response, '/admin/manage-users/')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_edit_user_view(self):
        user = User.objects.create_user(username='editme', password='pass')
        url = f'/admin/manage-users/{user.id}/edit/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit User')

        response = self.client.post(url, {'username': 'edited', 'first_name': 'Edited', 'last_name': '', 'email': '', 'is_staff': False, 'is_active': True}, follow=True)
        self.assertRedirects(response, '/admin/manage-users/')
        user.refresh_from_db()
        self.assertEqual(user.username, 'edited')

    def test_view_user_view(self):
        user = User.objects.create_user(username='viewme', password='pass')
        url = f'/admin/manage-users/{user.id}/view/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'viewme')

    def test_delete_user_view(self):
        user = User.objects.create_user(username='deleteme', password='pass')
        url = f'/admin/manage-users/{user.id}/delete/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # perform delete
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, '/admin/manage-users/')
        self.assertFalse(User.objects.filter(username='deleteme').exists())
