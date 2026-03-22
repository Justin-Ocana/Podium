# Views for users app

from .auth_views import (
    RegisterView,
    LoginView,
    LogoutView,
    PasswordChangeView,
)
from .user_views import UserViewSet
from .profile_views import ProfileViewSet

__all__ = [
    # Auth views
    'RegisterView',
    'LoginView',
    'LogoutView',
    'PasswordChangeView',
    # User views
    'UserViewSet',
    # Profile views
    'ProfileViewSet',
]

