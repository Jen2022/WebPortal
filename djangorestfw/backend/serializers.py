# users/serializers.py
from rest_framework import serializers
from .models import CustomUser
from .models import TeamCategory
from .models import Sport
from .models import Team
from django.contrib.auth.hashers import make_password

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'fname', 'lname', 'user_type']
        extra_kwargs = {
            'password': {'write_only': True}  # Ensure the password is write-only
        }
    def create(self, validated_data):
        # Hash the password before saving the user
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Update the password if provided
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    

class TeamCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamCategory
        fields = ['id', 'name']

    def validate_name(self, value):
        # Normalize the name for validation
        normalized_name = TeamCategory().normalize_name(value)
        if TeamCategory.objects.filter(name=normalized_name).exists():
            raise serializers.ValidationError("A category with a similar name already exists.")
        return value

class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ['id', 'name']

    def validate_name(self, value):
        # Normalize the name for validation
        normalized_name = Sport().normalize_name(value)
        if Sport.objects.filter(name=normalized_name).exists():
            raise serializers.ValidationError("A sport with a similar name already exists.")
        return value
    
class TeamSerializer(serializers.ModelSerializer):
    coaches = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(user_type='coach'), many=True)
    players = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(user_type='player'), many=True)
    sport = serializers.SlugRelatedField(slug_field='name', queryset=Sport.objects.all())
    team_category = serializers.CharField(source='team_category.name')
    number_of_players = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'team_name', 'number_of_players', 'coaches', 'sport', 'team_category', 'players']
        read_only_fields = ['id', 'number_of_players']

    def get_number_of_players(self, obj):
        return obj.players.count()

    def create(self, validated_data):
        coaches = validated_data.pop('coaches')
        players = validated_data.pop('players', [])
        team_category_name = validated_data.pop('team_category')['name']
        team_category, created = TeamCategory.objects.get_or_create(
            name=TeamCategory().normalize_name(team_category_name)
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
            team_category, created = TeamCategory.objects.get_or_create(
                name=TeamCategory().normalize_name(team_category_name)
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