# backend/tests/test_views.py
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from rest_framework import status
from .models import CustomUser
class CustomUserViewSetTestCase(APITestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_user(
            username='admin', password='password', email='admin@example.com',
            fname='Admin', lname='User', user_type='admin'
        )
        self.coach_user = CustomUser.objects.create_user(
            username='coach', password='password', email='coach@example.com',
            fname='Coach', lname='User', user_type='coach'
        )
        self.player_user = CustomUser.objects.create_user(
            username='player', password='password', email='player@example.com',
            fname='Player', lname='User', user_type='player'
        )
        self.client = APIClient()

    def test_list_users_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('customuser-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_as_coach(self):
        self.client.force_authenticate(user=self.coach_user)
        response = self.client.get(reverse('customuser-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_as_player(self):
        self.client.force_authenticate(user=self.player_user)
        response = self.client.get(reverse('customuser-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('customuser-detail', kwargs={'pk': self.player_user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_user_as_player(self):
        self.client.force_authenticate(user=self.player_user)
        response = self.client.get(reverse('customuser-detail', kwargs={'pk': self.player_user.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'username': 'newuser', 'password': 'password', 'email': 'newuser@example.com',
            'fname': 'New', 'lname': 'User', 'user_type': 'player'
        }
        response = self.client.post(reverse('customuser-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_as_coach(self):
        self.client.force_authenticate(user=self.coach_user)
        data = {
            'username': 'newuser', 'password': 'password', 'email': 'newuser@example.com',
            'fname': 'New', 'lname': 'User', 'user_type': 'player'
        }
        response = self.client.post(reverse('customuser-list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_as_player(self):
        self.client.force_authenticate(user=self.player_user)
        data = {
            'username': 'newuser', 'password': 'password', 'email': 'newuser@example.com',
            'fname': 'New', 'lname': 'User', 'user_type': 'player'
        }
        response = self.client.post(reverse('customuser-list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {'fname': 'Updated'}
        response = self.client.patch(reverse('customuser-detail', kwargs={'pk': self.player_user.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user_as_coach(self):
        self.client.force_authenticate(user=self.coach_user)
        data = {'fname': 'Updated'}
        response = self.client.patch(reverse('customuser-detail', kwargs={'pk': self.player_user.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_as_player(self):
        self.client.force_authenticate(user=self.player_user)
        data = {'fname': 'Updated'}
        response = self.client.patch(reverse('customuser-detail', kwargs={'pk': self.player_user.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse('customuser-detail', kwargs={'pk': self.player_user.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_user_as_coach(self):
        self.client.force_authenticate(user=self.coach_user)
        response = self.client.delete(reverse('customuser-detail', kwargs={'pk': self.player_user.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_as_player(self):
        self.client.force_authenticate(user=self.player_user)
        response = self.client.delete(reverse('customuser-detail', kwargs={'pk': self.player_user.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
