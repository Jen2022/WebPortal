# backend/views.py
from rest_framework import viewsets
from .models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsAdminUser, IsCoachUser, IsPlayerUser

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:  # Only allow admin to list and retrieve users
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminUser]  # Only admin can create, update, and delete users
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]  