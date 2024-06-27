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
    
class IsInWorkspace(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.workspace is not None

    def has_object_permission(self, request, view, obj):
        return obj.workspace == request.user.workspace