from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('coach', 'Coach'),
        ('player', 'Player'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    email = models.EmailField(unique=True)  # Ensure email is unique
    password = models.CharField(max_length=128)  # Adjust length as per your hash algorithm
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)

    REQUIRED_FIELDS = ['email','password', 'fname', 'lname', 'user_type']

    def __str__(self):
        return f"{self.fname} {self.lname} ({self.user_type})"