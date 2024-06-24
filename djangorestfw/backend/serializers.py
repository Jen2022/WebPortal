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
    players = CustomUserSerializer(many=True)
    coaches = CustomUserSerializer(many=True)
    sport = SportSerializer()
    team_category = TeamCategorySerializer()
    number_of_players = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'team_name', 'number_of_players', 'players', 'coaches', 'sport', 'team_category']
        read_only_fields = ['id']

    def get_number_of_players(self, obj):
        return obj.players.count()