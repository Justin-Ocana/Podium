"""
WebSocket authentication middleware.

Allows authentication via token query parameter for WebSocket connections.
"""
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.db import connection
from django.db.utils import OperationalError
from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs
import logging

logger = logging.getLogger(__name__)


@database_sync_to_async
def get_user_from_token(token_key):
    """Get user from authentication token with connection retry."""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Ensure connection is alive
            connection.ensure_connection()
            token = Token.objects.select_related('user').get(key=token_key)
            return token.user
        except OperationalError as e:
            retry_count += 1
            logger.warning(f"Database connection error (attempt {retry_count}/{max_retries}): {e}")
            connection.close()
            if retry_count >= max_retries:
                logger.error(f"Failed to authenticate user after {max_retries} attempts")
                return AnonymousUser()
        except Token.DoesNotExist:
            return AnonymousUser()
        except Exception as e:
            logger.error(f"Unexpected error in get_user_from_token: {e}")
            return AnonymousUser()
    
    return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    """
    Middleware to authenticate WebSocket connections using token.
    
    Expects token in query string: ws://localhost:8000/ws/notifications/?token=<token>
    """
    
    async def __call__(self, scope, receive, send):
        # Get token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token_key = query_params.get('token', [None])[0]
        
        # Authenticate user
        if token_key:
            scope['user'] = await get_user_from_token(token_key)
        else:
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)
