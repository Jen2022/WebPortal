# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet
from .views import TeamCategoryViewSet
from .views import SportViewSet
from .views import TeamViewSet
from .views import WorkspaceViewSet
from .views import SessionDataViewSet

router = DefaultRouter()
router.register(r'workspaces', WorkspaceViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'users', CustomUserViewSet)
router.register(r'team-categories', TeamCategoryViewSet, basename='teamcategory')
router.register(r'sports', SportViewSet, basename='sport')
router.register(r'session-data', SessionDataViewSet, basename='session-data')

urlpatterns = [
    path('', include(router.urls)),
]
