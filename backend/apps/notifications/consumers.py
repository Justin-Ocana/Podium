"""
WebSocket consumers for real-time notifications.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    
    Each user connects to their own notification channel.
    When a notification is created, it's sent to the user's channel in real-time.
    
    Usage:
        ws://localhost:8000/ws/notifications/?token=<auth_token>
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        # Get user from scope (set by AuthMiddleware)
        self.user = self.scope['user']
        
        # Reject anonymous users
        if isinstance(self.user, AnonymousUser) or not self.user.is_authenticated:
            await self.close()
            return
        
        # Create a unique channel group for this user
        self.group_name = f'notifications_{self.user.id}'
        
        # Join the user's notification group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial unread count asynchronously (don't block connection)
        try:
            unread_count = await self.get_unread_count()
            await self.send(text_data=json.dumps({
                'type': 'unread_count',
                'count': unread_count
            }))
        except Exception as e:
            # If DB fails, just send 0 and continue
            import logging
            logging.getLogger(__name__).warning(f"Failed to get initial unread count: {e}")
            await self.send(text_data=json.dumps({
                'type': 'unread_count',
                'count': 0
            }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'group_name'):
            # Leave the notification group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """
        Handle messages from WebSocket.
        
        Supported commands:
        - mark_as_read: Mark a notification as read
        - mark_all_as_read: Mark all notifications as read
        """
        try:
            data = json.loads(text_data)
            command = data.get('command')
            
            if command == 'mark_as_read':
                notification_id = data.get('notification_id')
                if notification_id:
                    await self.mark_notification_as_read(notification_id)
            
            elif command == 'mark_all_as_read':
                count = await self.mark_all_as_read()
                await self.send(text_data=json.dumps({
                    'type': 'marked_all_as_read',
                    'count': count
                }))
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def notification_message(self, event):
        """
        Handle notification message from channel layer.
        
        This is called when a notification is sent to the user's group.
        """
        # Send notification to WebSocket with unread count
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification'],
            'unread_count': event.get('unread_count', 0)
        }))
    
    async def unread_count_update(self, event):
        """Handle unread count update."""
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': event['count']
        }))
    
    @database_sync_to_async
    def get_unread_count(self):
        """Get unread notification count for the user with connection retry."""
        from django.db import connection
        from django.db.utils import OperationalError
        from .services import get_unread_count
        import logging
        import time
        
        logger = logging.getLogger(__name__)
        max_retries = 2  # Reduced retries for faster response
        
        for attempt in range(max_retries):
            try:
                # Close stale connections before trying
                if connection.connection and connection.is_usable():
                    pass  # Connection is good
                else:
                    connection.close()
                
                return get_unread_count(self.user)
            except OperationalError as e:
                logger.warning(f"DB error in get_unread_count (attempt {attempt + 1}/{max_retries}): {str(e)[:100]}")
                connection.close()
                if attempt < max_retries - 1:
                    time.sleep(0.1)  # Brief pause before retry
                else:
                    return 0
            except Exception as e:
                logger.error(f"Unexpected error in get_unread_count: {str(e)[:100]}")
                connection.close()
                return 0
        
        return 0
    
    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        """Mark a notification as read with connection retry."""
        from django.db import connection
        from django.db.utils import OperationalError
        from .models import Notification
        import logging
        import time
        
        logger = logging.getLogger(__name__)
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                if not connection.is_usable():
                    connection.close()
                
                notification = Notification.objects.get(
                    id=notification_id,
                    recipient=self.user
                )
                notification.mark_as_read()
                return True
            except Notification.DoesNotExist:
                return False
            except OperationalError as e:
                logger.warning(f"DB error in mark_notification_as_read (attempt {attempt + 1}/{max_retries}): {str(e)[:100]}")
                connection.close()
                if attempt < max_retries - 1:
                    time.sleep(0.1)
                else:
                    return False
            except Exception as e:
                logger.error(f"Unexpected error in mark_notification_as_read: {str(e)[:100]}")
                connection.close()
                return False
        
        return False
    
    @database_sync_to_async
    def mark_all_as_read(self):
        """Mark all notifications as read with connection retry."""
        from django.db import connection
        from django.db.utils import OperationalError
        from .services import mark_all_as_read
        import logging
        import time
        
        logger = logging.getLogger(__name__)
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                if not connection.is_usable():
                    connection.close()
                
                return mark_all_as_read(self.user)
            except OperationalError as e:
                logger.warning(f"DB error in mark_all_as_read (attempt {attempt + 1}/{max_retries}): {str(e)[:100]}")
                connection.close()
                if attempt < max_retries - 1:
                    time.sleep(0.1)
                else:
                    return 0
            except Exception as e:
                logger.error(f"Unexpected error in mark_all_as_read: {str(e)[:100]}")
                connection.close()
                return 0
        
        return 0
