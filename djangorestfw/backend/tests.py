from django.test import TestCase

# Create your tests here.
# backend/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser
from django.contrib.auth.hashers import make_password

class CustomUserViewSetTests(APITestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create(
            username='admin',
            email='admin@example.com',
            password=make_password('adminpassword'),
            fname='Admin',
            lname='User',
            user_type='admin'
        )
        self.client.force_authenticate(user=self.admin_user)
        self.user = CustomUser.objects.create(
            username='user1',
            email='user1@example.com',
            password=make_password('userpassword'),
            fname='User',
            lname='One',
            user_type='player'
        )

    def test_update_user(self):
        url = reverse('customuser-detail', args=[self.user.id])
        data = {
            'username': 'updateduser1',
            'email': 'updateduser1@example.com',
            'fname': 'Updated',
            'lname': 'User',
            'user_type': 'coach'
        }
        response = self.client.put(url, data, format='json')
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.username, data['username'])
        self.assertEqual(self.user.email, data['email'])
        self.assertEqual(self.user.fname, data['fname'])
        self.assertEqual(self.user.lname, data['lname'])
        self.assertEqual(self.user.user_type, data['user_type'])

    def test_partial_update_user(self):
        url = reverse('customuser-detail', args=[self.user.id])
        data = {
            'fname': 'Partially Updated'
        }
        response = self.client.patch(url, data, format='json')
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.fname, data['fname'])

    def test_update_user_password(self):
        url = reverse('customuser-detail', args=[self.user.id])
        data = {
            'password': 'newpassword123'
        }
        response = self.client.put(url, data, format='json')
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(data['password']))
