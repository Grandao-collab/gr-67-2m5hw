from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterAPITest(APITestCase):
    def test_user_registration_success(self):
        url = reverse('register')
        payload = {
            'username': 'newuser',
            'password': 'StrongPass123',
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertNotIn('password', response.data)
