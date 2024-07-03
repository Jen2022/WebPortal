# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet
from .views import TeamCategoryViewSet
from .views import SportViewSet
from .views import TeamViewSet
from .views import WorkspaceViewSet
from .views import SessionDataViewSet

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


router = DefaultRouter()
router.register(r'workspaces', WorkspaceViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'users', CustomUserViewSet)
router.register(r'team-categories', TeamCategoryViewSet, basename='teamcategory')
router.register(r'sports', SportViewSet, basename='sport')
router.register(r'session-data', SessionDataViewSet, basename='session-data')

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
