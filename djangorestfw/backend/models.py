from django.contrib.auth.models import AbstractUser
from django.db import models
import re
from django.core.exceptions import ValidationError
from django.db import models

class Workspace(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('coach', 'Coach'),
        ('player', 'Player'),
        ('parent', 'Parent'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    email = models.EmailField(unique=True)  
    password = models.CharField(max_length=128)  
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='users')

    REQUIRED_FIELDS = ['email', 'password', 'fname', 'lname', 'user_type','workspace']

    def __str__(self):
        return f"{self.fname} {self.lname} ({self.user_type})"
    
class ParentPlayer(models.Model):
    parent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='children', limit_choices_to={'user_type': 'parent'})
    player = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='parents', limit_choices_to={'user_type': 'player'})
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='parent_player_relationships')

    class Meta:
        unique_together = ('parent', 'player')

    def __str__(self):
        return f"{self.parent.fname} {self.parent.lname} - {self.player.fname} {self.player.lname}"
    
class TeamCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='team_categories')

    def __str__(self):
        return self.name

    def normalize_name(self, name):
        # Normalize by converting to lowercase, removing spaces and special characters
        return re.sub(r'[^a-z0-9]', '', name.lower())

    def save(self, *args, **kwargs):
        # Normalize the name before saving
        normalized_name = self.normalize_name(self.name)
        if TeamCategory.objects.exclude(id=self.id).filter(name__iexact=normalized_name).exists():
            raise ValidationError(f"A category with a similar name '{self.name}' already exists.")
        self.name = normalized_name
        super(TeamCategory, self).save(*args, **kwargs)

class Sport(models.Model):
    name = models.CharField(max_length=100, unique=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='sports')

    def __str__(self):
        return self.name

    def normalize_name(self, name):
        # Normalize by converting to lowercase and removing non-alphanumeric characters
        return re.sub(r'[^a-z0-9]', '', name.lower())

    def save(self, *args, **kwargs):
        normalized_name = self.normalize_name(self.name)
        if Sport.objects.exclude(id=self.id).filter(name=normalized_name).exists():
            raise ValidationError(f"A sport with a similar name '{self.name}' already exists.")
        self.name = normalized_name
        super(Sport, self).save(*args, **kwargs)

class Team(models.Model):
    team_name = models.CharField(max_length=100)
    players = models.ManyToManyField(CustomUser, related_name='teams_as_player', limit_choices_to={'user_type': 'player'})
    coaches = models.ManyToManyField(CustomUser, related_name='teams_as_coach', limit_choices_to={'user_type': 'coach'})
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    team_category = models.ForeignKey(TeamCategory, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='teams')

    def __str__(self):
        return self.team_name