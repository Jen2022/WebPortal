# backend/views.py
from rest_framework import viewsets, status
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
from .models import SessionImpactsOverview, SessionImpact, Notes

from .serializers import CustomUserSerializer
from .serializers import SportSerializer
from .serializers import ParentPlayerSerializer
from .serializers import TeamSerializer
from .serializers import TeamCategorySerializer
from .serializers import WorkspaceSerializer
from .serializers import SessionDataSerializer, UpdateNoteSerializer, SessionImpactsOverviewSerializer
from rest_framework.parsers import MultiPartParser, FormParser

from django.shortcuts import get_object_or_404
from datetime import datetime
import json
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
    
    def get_queryset(self):
        return CustomUser.objects.filter(workspace=self.request.user.workspace)
    
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
    serializer_class = SportSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsInWorkspace]

    def get_queryset(self):
        global_sports = Sport.objects.filter(global_sport=True)
        workspace_sports = Sport.objects.filter(workspace=self.request.user.workspace, global_sport=False)
        return global_sports.union(workspace_sports)
    
    def get_object(self):
        queryset = self.get_queryset()
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_field]}
        try:
            # Search in the unioned queryset
            obj = next(item for item in queryset if getattr(item, self.lookup_field) == filter_kwargs[self.lookup_field])
        except StopIteration:
            # If not found, raise a 404 error
            from django.shortcuts import get_object_or_404
            obj = get_object_or_404(queryset.model, **filter_kwargs)
        
        # Perform the standard permission check.
        self.check_object_permissions(self.request, obj)
        return obj
    def create(self, request, *args, **kwargs):
        # Copy request data to a mutable dict
        data = request.data.copy()
        data['global_sport'] = False
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()
    
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

class SessionDataViewSet(viewsets.ViewSet):
    parser_classes = [MultiPartParser, FormParser]
    
    @action(detail=True, methods=['get'], url_path='sessions-overview')
    def get_player_sessions(self, request, pk=None):
        player = get_object_or_404(CustomUser, pk=pk)
        sessions = SessionImpactOverview.objects.filter(user=player)
        serializer = SessionImpactOverviewSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='session-overview')
    def get_session_overview(self, request, pk=None):
        """
        Retrieve a specific session overview.
        """
        session = get_object_or_404(SessionImpactsOverview, pk=pk)
        serializer = SessionImpactsOverviewSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        serializer = SessionDataSerializer(data=request.data, many=True)
        if serializer.is_valid():
            self.parse_and_save_session_data(serializer.validated_data)
            return Response({"message": "Session data saved successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='upload-file')
    def upload_file(self, request):
        if 'file' not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        file_obj = request.FILES['file']
        try:
            data = json.load(file_obj)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON file"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = SessionDataSerializer(data=data, many=True)
        if serializer.is_valid():
            self.parse_and_save_session_data(serializer.validated_data)
            return Response({"message": "Session data saved successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def parse_and_save_session_data(self, session_data):
        for session in session_data:
            player = CustomUser.objects.get(id=session['player_id'])
            date = datetime.now().date()

            max_lin_impact = session['max_impact_lin']
            max_rot_impact = session['max_impact_rot']
            
            total_lin_impact = sum([reading['linear_impact'] for reading in session['all_readings']])
            total_rot_impact = sum([reading['rotational_impact'] for reading in session['all_readings']])
            count_readings = len(session['all_readings'])

            avg_lin_impact = total_lin_impact / count_readings if count_readings > 0 else 0
            avg_rot_impact = total_rot_impact / count_readings if count_readings > 0 else 0

            session_overview = SessionImpactsOverview.objects.create(
                user=player,
                date=date,
                max_lin_impact=max_lin_impact,
                max_rot_impact=max_rot_impact,
                avg_lin_impact=avg_lin_impact,
                avg_rot_impact=avg_rot_impact,
                cumulative_lin_impact=total_lin_impact,
                cumulative_rot_impact=total_rot_impact,
            )

            for reading in session['all_readings']:
                SessionImpact.objects.create(
                    session=session_overview,
                    time=datetime.fromtimestamp(reading['time']),
                    linear_impact=reading['linear_impact'],
                    rotational_impact=reading['rotational_impact']
                )

    @action(detail=True, methods=['post'], url_path='add-note')
    def add_note_to_session(self, request, pk=None):
        session = get_object_or_404(SessionImpactsOverview, pk=pk)
        serializer = UpdateNoteSerializer(data=request.data)
        if serializer.is_valid():
            note_text = serializer.validated_data['note']
            note_instance, created = Notes.objects.get_or_create(note=note_text)
            session.note = note_instance
            session.save()
            return Response({"message": "Note added to session successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)