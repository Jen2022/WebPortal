# backend/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsAdminUser
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError

from .models import CustomUser
from .models import ParentPlayer
from .models import Team
from .models import TeamCategory
from .models import Sport
from .models import Workspace

from .serializers import CustomUserSerializer
from .serializers import SportSerializer
from .serializers import ParentPlayerSerializer
from .serializers import TeamSerializer
from .serializers import TeamCategorySerializer
from .serializers import WorkspaceSerializer

from .permissions import IsInWorkspace


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:  # Only allow admin to list and retrieve users
            permission_classes = [IsAuthenticated, IsAdminUser, IsInWorkspace]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminUser, IsInWorkspace]  # Only admin can create, update, and delete users
        else:
            permission_classes = [IsAuthenticated, IsInWorkspace]
        return [permission() for permission in permission_classes]  
    
class ParentPlayerViewSet(viewsets.ModelViewSet):
    queryset = ParentPlayer.objects.all()
    serializer_class = ParentPlayerSerializer
    permission_classes = [IsInWorkspace]

    def get_queryset(self):
        return ParentPlayer.objects.filter(workspace=self.request.user.workspace)
    
class TeamCategoryViewSet(viewsets.ModelViewSet):
    queryset = TeamCategory.objects.all()
    serializer_class = TeamCategorySerializer
    permission_classes = [IsAuthenticated, IsInWorkspace]
    def get_queryset(self):
        return TeamCategory.objects.filter(workspace=self.request.user.workspace)
    
class SportViewSet(viewsets.ModelViewSet):
    queryset = Sport.objects.all()
    serializer_class = SportSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsInWorkspace]

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
        

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_queryset(self):
        return Team.objects.filter(workspace=self.request.user.workspace)

class WorkspaceViewSet(viewsets.ModelViewSet):
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Workspace.objects.all()
        return Workspace.objects.filter(users=self.request.user)