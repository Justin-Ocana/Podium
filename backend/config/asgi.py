"""
ASGI config for Podium project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

from apps.notifications.routing import websocket_urlpatterns
from apps.notifications.middleware import TokenAuthMiddleware


class CustomOriginValidator(OriginValidator):
    """Custom origin validator that allows configured CORS origins."""
    
    def valid_origin(self, parsed_origin):
        from django.conf import settings
        # Allow any origin in CORS_ALLOWED_ORIGINS
        origin = f"{parsed_origin[0]}://{parsed_origin[1]}"
        if parsed_origin[2] is not None:  # port
            origin = f"{origin}:{parsed_origin[2]}"
        
        # Check against CORS_ALLOWED_ORIGINS
        allowed = origin in settings.CORS_ALLOWED_ORIGINS
        if not allowed:
            # Also check without port for localhost
            origin_no_port = f"{parsed_origin[0]}://{parsed_origin[1]}"
            allowed = origin_no_port in settings.CORS_ALLOWED_ORIGINS
        
        return allowed


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": CustomOriginValidator(
        TokenAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
