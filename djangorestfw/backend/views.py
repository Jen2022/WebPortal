# backend/views.py
from rest_framework import viewsets
from .models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsAdminUser, IsCoachUser, IsPlayerUser
from rest_framework import viewsets
from .models import TeamCategory
from .serializers import TeamCategorySerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Sport
from .serializers import SportSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError

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
    
class TeamCategoryViewSet(viewsets.ModelViewSet):
    queryset = TeamCategory.objects.all()
    serializer_class = TeamCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
     


class SportViewSet(viewsets.ModelViewSet):
    queryset = Sport.objects.all()
    serializer_class = SportSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def add_other(self, request):
        name = request.data.get('name')
        if not name:
            return Response({'error': 'Name is required'}, status=400)
        
        try:
            sport, created = Sport.objects.get_or_create(name=name)
            if created:
                return Response(SportSerializer(sport).data, status=201)
            else:
                return Response({'error': 'Sport already exists'}, status=400)
        except ValidationError as e:
            return Response({'error': e.message_dict}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)