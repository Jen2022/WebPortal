# users/serializers.py
from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'fname', 'lname', 'user_type']

    def update(self, instance, validated_data):
        # Update the password if provided
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
