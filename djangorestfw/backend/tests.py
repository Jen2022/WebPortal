# backend/tests/test_views.py
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from rest_framework import status
from .models import CustomUser
from .models import TeamCategory

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

class TeamCategoryViewSetTestCase(APITestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_user(
            username='admin', password='password', email='admin@example.com',
            fname='Admin', lname='User', user_type='admin'
        )
        self.client = APIClient()
        self.category_data = {'name': 'Under 12'}
        self.category = TeamCategory.objects.create(name='Under 12')

    def test_list_team_categories(self):        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('teamcategory-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'under12')  # name should be normalized

    def test_create_team_category(self):
        self.client.force_authenticate(user=self.admin_user)
        new_category_data = {'name': 'Under 14'}
        response = self.client.post(reverse('teamcategory-list'), new_category_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TeamCategory.objects.count(), 2)
        self.assertEqual(TeamCategory.objects.get(id=response.data['id']).name, 'under14')  # name should be normalized

    def test_create_duplicate_team_category(self):
        self.client.force_authenticate(user=self.admin_user)
        duplicate_category_data = {'name': 'under 12'}  # Same name, different formatting
        response = self.client.post(reverse('teamcategory-list'), duplicate_category_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'][0].code, 'invalid')
        self.assertEqual(str(response.data['name'][0]), 'A category with a similar name already exists.')


    def test_retrieve_team_category(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('teamcategory-detail', kwargs={'pk': self.category.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'under12')  # name should be normalized

    def test_update_team_category(self):        
        self.client.force_authenticate(user=self.admin_user)
        update_data = {'name': 'Under 16'}
        response = self.client.patch(reverse('teamcategory-detail', kwargs={'pk': self.category.pk}), update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'under16')  # name should be normalized

    def test_delete_team_category(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse('teamcategory-detail', kwargs={'pk': self.category.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TeamCategory.objects.count(), 0)

    def test_normalize_team_category_name(self):
        self.client.force_authenticate(user=self.admin_user)
        new_category_data = {'name': ' Under-12 '}
        response = self.client.post(reverse('teamcategory-list'), new_category_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'][0].code, 'invalid')
        self.assertEqual(str(response.data['name'][0]), 'A category with a similar name already exists.')