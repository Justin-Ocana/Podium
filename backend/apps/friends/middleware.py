"""
Middleware for handling database connection issues.
"""
from django.db import connection
from django.db.utils import OperationalError
import logging

logger = logging.getLogger(__name__)


class DatabaseReconnectMiddleware:
    """
    Middleware to handle database connection issues.
    Attempts to reconnect if connection is lost.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            # Check if connection is alive
            connection.ensure_connection()
        except OperationalError as e:
            logger.warning(f"Database connection lost, attempting to reconnect: {e}")
            try:
                # Close the old connection
                connection.close()
                # Django will automatically create a new connection on next query
            except Exception as close_error:
                logger.error(f"Error closing connection: {close_error}")
        
        response = self.get_response(request)
        return response
