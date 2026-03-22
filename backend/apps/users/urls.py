"""
URL configuration for users app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    PasswordChangeView,
    UserViewSet,
    ProfileViewSet,
)
from .views.upload_views import (
    upload_avatar,
    upload_banner,
    delete_avatar,
    delete_banner,
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', ProfileViewSet, basename='profile')

# URL patterns
urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('me/change-password/', PasswordChangeView.as_view(), name='password-change'),
    
    # Upload endpoints
    path('me/upload-avatar/', upload_avatar, name='upload-avatar'),
    path('me/upload-banner/', upload_banner, name='upload-banner'),
    path('me/delete-avatar/', delete_avatar, name='delete-avatar'),
    path('me/delete-banner/', delete_banner, name='delete-banner'),
    
    # Include router URLs
    path('', include(router.urls)),
]
