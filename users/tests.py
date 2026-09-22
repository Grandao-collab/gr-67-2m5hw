from django.test import TestCase

from users.models import CustomUser


class CustomUserPhoneValidationTests(TestCase):
    def test_create_user_rejects_invalid_phone_number(self):
        with self.assertRaisesMessage(ValueError, 'Phone number must start with 996'):
            CustomUser.objects.create_user(
                email='user@example.com',
                password='secret123',
                phone_number='1234567890',
            )

    def test_create_superuser_requires_phone_number(self):
        with self.assertRaisesMessage(ValueError, 'Superuser must have a valid phone number'):
            CustomUser.objects.create_superuser(
                email='admin@example.com',
                password='secret123',
            )

    def test_create_superuser_with_valid_phone_number(self):
        user = CustomUser.objects.create_superuser(
            email='admin@example.com',
            password='secret123',
            phone_number='+996555123456',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.phone_number, '+996555123456')
