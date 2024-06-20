# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet
from .views import TeamCategoryViewSet
from .views import SportViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'team-categories', TeamCategoryViewSet, basename='teamcategory')
router.register(r'sports', SportViewSet, basename='sport')

urlpatterns = [
    path('', include(router.urls)),
]
