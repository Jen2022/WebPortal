from django.urls import reverse

from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from .models import CustomUser
from .models import TeamCategory
from .models import Sport
from .models import Team,Workspace

class CustomUserViewSetTestCase(APITestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name='Default Test2 Workspace')
        
        self.admin_user = CustomUser.objects.create_user(
            username='admin', password='password', email='admin@example.com',
            fname='Admin', lname='User', user_type='admin', workspace=self.workspace
        )
        self.coach_user = CustomUser.objects.create_user(
            username='coach', password='password', email='coach@example.com',
            fname='Coach', lname='User', user_type='coach', workspace=self.workspace
        )
        self.player_user = CustomUser.objects.create_user(
            username='player', password='password', email='player@example.com',
            fname='Player', lname='User', user_type='player', workspace=self.workspace
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
            'username': 'newuser',
            'password': 'password',
            'email': 'newuser@example.com',
            'fname': 'New',
            'lname': 'User',
            'user_type': 'player',
            'workspace': self.workspace.id
        }
        response = self.client.post(reverse('customuser-list'), data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)  # Print the response data to debug the validation error
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
        self.workspace = Workspace.objects.create(name='Default Test Workspace')
        
        self.admin_user = CustomUser.objects.create_user(
            username='admin', password='password', email='admin@example.com',
            fname='Admin', lname='User', user_type='admin', workspace=self.workspace
        )
        self.client = APIClient()
        self.category_data = {'name': 'Under 12', 'workspace': self.workspace.id}
        self.category = TeamCategory.objects.create(name='Under 12', workspace=self.workspace)

    def test_list_team_categories(self):        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('teamcategory-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'under12')  # name should be normalized

    def test_create_team_category(self):
        self.client.force_authenticate(user=self.admin_user)
        new_category_data = {'name': 'Under 14', 'workspace': self.workspace.id}
        response = self.client.post(reverse('teamcategory-list'), new_category_data)
        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)
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

class SportViewSetTestCase(APITestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name='Default Test Workspace')
        self.admin_user = CustomUser.objects.create_user(
            username='admin', password='password', email='admin@example.com',
            fname='Admin', lname='User', user_type='admin', workspace = self.workspace
        )
        self.client = APIClient()
        self.sport_data = {'name': 'Golf','global_sport':False}
        self.sport = Sport.objects.create(name='Golf',workspace= self.workspace)

    def test_list_sports(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('sport-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 8)
        self.assertEqual(response.data[-1]['name'], 'golf')  # name should be normalized

    def test_create_sport(self):
        self.client.force_authenticate(user=self.admin_user)
        new_sport_data = {'name': 'Baseball','workspace':self.workspace.id}
        response = self.client.post(reverse('sport-list'), new_sport_data)
        if(response.status_code!=status.HTTP_201_CREATED):
            print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Sport.objects.count(), 9)
        self.assertEqual(Sport.objects.get(id=response.data['id']).name, 'baseball')  # name should be normalized
    
    def test_create_duplicate_sport(self):
        self.client.force_authenticate(user=self.admin_user)
        duplicate_sport_data = {'name': 'golf', 'workspace': self.workspace.id}
        response = self.client.post(reverse('sport-list'), duplicate_sport_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(response.data['non_field_errors'][0], 'The fields name, workspace must make a unique set.')

    def test_create_duplicate_sport_with_different_case(self):
        self.client.force_authenticate(user=self.admin_user)
        duplicate_sport_data = {'name': 'GOLF', 'workspace': self.workspace.id}
        response = self.client.post(reverse('sport-list'), duplicate_sport_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(response.data['non_field_errors'][0], 'A sport with a similar name already exists in this workspace.')

    
    def test_update_sport(self):
        self.client.force_authenticate(user=self.admin_user)
        update_data = {'name': 'Baseball', 'workspace': self.workspace.id}
        response = self.client.patch(reverse('sport-detail', kwargs={'pk': self.sport.pk}), update_data, format='json')
        if response.status_code != status.HTTP_200_OK:
            print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'baseball')

    def test_delete_sport(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse('sport-detail', kwargs={'pk': self.sport.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Sport.objects.count(), 7)
  
class TeamViewSetTestCase(APITestCase):
    
    def setUp(self):
        self.workspace = Workspace.objects.create(name='Default Test Workspace')
        self.admin_user = CustomUser.objects.create_user(
            username='admin', password='password', email='admin@example.com',
            fname='Admin', lname='User', user_type='admin', workspace=self.workspace
        )
        # Create sample users
        self.coach1 = CustomUser.objects.create_user(username='coach1', password='password', email='coach1@example.com', fname='Coach', lname='One', user_type='coach', workspace=self.workspace)
        self.coach2 = CustomUser.objects.create_user(username='coach2', password='password', email='coach2@example.com', fname='Coach', lname='Two', user_type='coach', workspace=self.workspace)
        self.player1 = CustomUser.objects.create_user(username='player1', password='password', email='player1@example.com', fname='Player', lname='One', user_type='player', workspace=self.workspace)
        self.player2 = CustomUser.objects.create_user(username='player2', password='password', email='player2@example.com', fname='Player', lname='Two', user_type='player', workspace=self.workspace)

        # Create sample sport
        self.sport = Sport.objects.create(name='badminton', workspace=self.workspace)

        # Create sample team category
        self.team_category = TeamCategory.objects.create(name='Under 14', workspace=self.workspace)

        # Create client
        self.client = self.client_class()

    def test_create_team(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('team-list')
        data = {
            "team_name": "Team A",
            "coaches": [self.coach1.id, self.coach2.id],  # IDs of existing coaches
            "sport": "badminton",
            "team_category": "Under 14",
            "players": [self.player1.id, self.player2.id],  # IDs of existing players
            'workspace': self.workspace.id
        }
        response = self.client.post(url, data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)  # Print the response data for debugging
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(Team.objects.get().team_name, 'Team A')

    def test_retrieve_team(self):
        self.client.force_authenticate(user=self.admin_user)
        team = Team.objects.create(team_name='Team B', sport=self.sport, team_category=self.team_category, workspace=self.workspace )
        team.coaches.set([self.coach1, self.coach2])
        team.players.set([self.player1, self.player2])
        url = reverse('team-detail', args=[team.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['team_name'], 'Team B')
        self.assertEqual(response.data['number_of_players'], 2)
        self.assertListEqual(response.data['coaches'], [self.coach1.id, self.coach2.id])
        self.assertListEqual(response.data['players'], [self.player1.id, self.player2.id])

    def test_update_team(self):
        self.client.force_authenticate(user=self.admin_user)
        team = Team.objects.create(team_name='Team C', sport=self.sport, team_category=self.team_category,workspace= self.workspace)
        team.coaches.set([self.coach1])
        team.players.set([self.player1])

        url = reverse('team-detail', args=[team.id])
        data = {
            "team_name": "Team C Updated",
            "coaches": [self.coach2.id],  # Updating coaches
            "sport": "badminton",
            "team_category": "Under 14",
            "players": [self.player2.id],  # Updating players
            'workspace': self.workspace.id
        }
        response = self.client.put(url, data, format='json')
        if response.status_code != status.HTTP_200_OK:
            print(response.data)  # Print the response data for debugging
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        team.refresh_from_db()
        self.assertEqual(team.team_name, 'Team C Updated')
        self.assertListEqual(list(team.coaches.values_list('username', flat=True)), ['coach2'])
        self.assertListEqual(list(team.players.values_list('username', flat=True)), ['player2'])

    def test_delete_team(self):
        self.client.force_authenticate(user=self.admin_user)
        team = Team.objects.create(team_name='Team D', sport=self.sport, team_category=self.team_category, workspace=self.workspace)
        url = reverse('team-detail', args=[team.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Team.objects.count(), 0)



