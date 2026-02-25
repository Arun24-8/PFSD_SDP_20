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
