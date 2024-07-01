# users/serializers.py
from rest_framework import serializers
from .models import CustomUser
from .models import ParentPlayer
from .models import TeamCategory
from .models import Sport
from .models import Team
from .models import Workspace
from django.contrib.auth.hashers import make_password

class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ['id', 'name']

class CustomUserSerializer(serializers.ModelSerializer):
    workspace = serializers.PrimaryKeyRelatedField(queryset=Workspace.objects.all())
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'fname', 'lname', 'user_type','workspace']
        extra_kwargs = {
            'password': {'write_only': True}  # Ensure the password is write-only
        }

    def create(self, validated_data):
        # Hash the password before saving the user
        # workspace_data = validated_data.pop('workspace')
        # workspace, created = Workspace.objects.get_or_create(**workspace_data)
        # validated_data['workspace'] = workspace
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # workspace_data = validated_data.pop('workspace', None)
        # if workspace_data:
        #     workspace, created = Workspace.objects.get_or_create(**workspace_data)
        #     instance.workspace = workspace
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)

class ParentPlayerSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(user_type='parent'))
    player = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(user_type='player'))

    class Meta:
        model = ParentPlayer
        fields = ['id', 'parent', 'player']

class TeamCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamCategory
        fields = ['id', 'name','workspace']

    def validate_name(self, value):
        # Normalize the name for validation
        normalized_name = TeamCategory().normalize_name(value)
        if TeamCategory.objects.filter(name=normalized_name).exists():
            raise serializers.ValidationError("A category with a similar name already exists.")
        return value

class SportSerializer(serializers.ModelSerializer):
    workspace = serializers.PrimaryKeyRelatedField(queryset=Workspace.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Sport
        fields = ['id', 'name', 'workspace', 'global_sport']

    def validate(self, data):
        normalized_name = Sport().normalize_name(data['name'])
        workspace = data.get('workspace', None)
        global_sport = data.get('global_sport', False)

        if global_sport:
            if Sport.objects.filter(name=normalized_name, global_sport=True).exists():
                raise serializers.ValidationError("A sport with this name already exists.")
        else:
            if Sport.objects.filter(name=normalized_name, workspace=workspace, global_sport=False).exists():
                raise serializers.ValidationError({
                    'non_field_errors': ['A sport with a similar name already exists in this workspace.']
                })

        data['name'] = normalized_name
        return data
    
    # def create(self, validated_data):
    #     validated_data['name'] = Sport().normalize_name(validated_data['name'])
    #     return super().create(validated_data)
    
class TeamSerializer(serializers.ModelSerializer):
    coaches = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(user_type='coach'), many=True)
    players = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(user_type='player'), many=True)
    sport = serializers.SlugRelatedField(slug_field='name', queryset=Sport.objects.all())
    team_category = serializers.CharField(source='team_category.name')
    number_of_players = serializers.SerializerMethodField()
    coaches_details = CustomUserSerializer(source='coaches', many=True, read_only=True)
    players_details = CustomUserSerializer(source='players', many=True, read_only=True)
    workspace = serializers.PrimaryKeyRelatedField(queryset=Workspace.objects.all())

    class Meta:
        model = Team
        fields = [
            'id', 'team_name', 'number_of_players', 'coaches', 'coaches_details',
            'sport', 'team_category', 'players', 'players_details','workspace'
        ]
        read_only_fields = ['id', 'number_of_players', 'coaches_details', 'players_details']

    def get_number_of_players(self, obj):
        return obj.players.count()

    def create(self, validated_data):
        coaches = validated_data.pop('coaches')
        players = validated_data.pop('players', [])
        team_category_name = validated_data.pop('team_category')['name']
        team_category, created =TeamCategory.objects.get_or_create(
            name=TeamCategory().normalize_name(team_category_name),
            workspace=validated_data['workspace']
        )
        sport = validated_data.pop('sport')
        team = Team.objects.create(team_category=team_category, sport=sport, **validated_data)
        team.coaches.set(coaches)
        team.players.set(players)
        return team

    def update(self, instance, validated_data):
        coaches = validated_data.pop('coaches', None)
        players = validated_data.pop('players', None)
        team_category_name = validated_data.pop('team_category', {}).get('name', None)
        if team_category_name:
            team_category, created =TeamCategory.objects.get_or_create(
                name=TeamCategory().normalize_name(team_category_name),
                workspace=instance.workspace
            )
            instance.team_category = team_category

        instance.team_name = validated_data.get('team_name', instance.team_name)
        instance.sport = validated_data.get('sport', instance.sport)
        instance.save()
        if coaches is not None:
            instance.coaches.set(coaches)
        if players is not None:
            instance.players.set(players)
        return instance
