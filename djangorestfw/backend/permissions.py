# backend/permissions.py
from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.user_type == 'admin'

class IsCoachUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.user_type == 'coach'

class IsPlayerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.user_type == 'player'
