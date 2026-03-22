"""
Notification services.

This module provides functions to create and manage notifications.
It acts as a central service that can be called from any app in the system.
"""
from typing import Optional
from django.contrib.contenttypes.models import ContentType
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from apps.users.models import User
from .models import Notification, NotificationType


def create_notification(
    recipient: User,
    notification_type: str,
    message: str,
    actor: Optional[User] = None,
    related_object: Optional[object] = None
) -> Notification:
    """
    Create a notification for a user and send it in real-time via WebSocket.
    
    This is the main function to create notifications from anywhere in the system.
    
    Args:
        recipient: User who will receive the notification
        notification_type: Type of notification (from NotificationType)
        message: Message to display
        actor: User who triggered the notification (optional)
        related_object: Related model instance (optional)
    
    Returns:
        Created Notification instance
    
    Example:
        # From friends app
        create_notification(
            recipient=user_b,
            notification_type=NotificationType.FRIEND_REQUEST,
            message=f"{user_a.username} sent you a friend request",
            actor=user_a,
            related_object=friend_request
        )
    """
    content_type = None
    object_id = None
    
    if related_object:
        content_type = ContentType.objects.get_for_model(related_object)
        object_id = related_object.pk
    
    notification = Notification.objects.create(
        recipient=recipient,
        actor=actor,
        type=notification_type,
        message=message,
        content_type=content_type,
        object_id=object_id
    )
    
    # Send notification in real-time via WebSocket
    send_notification_to_user(recipient.id, notification)
    
    return notification


def send_notification_to_user(user_id: int, notification: Notification):
    """
    Send a notification to a user via WebSocket.
    
    Args:
        user_id: ID of the user to send notification to
        notification: Notification instance to send
    """
    from .serializers import NotificationListSerializer
    
    channel_layer = get_channel_layer()
    group_name = f'notifications_{user_id}'
    
    # Serialize notification
    serializer = NotificationListSerializer(notification)
    
    # Get unread count
    unread_count = get_unread_count(notification.recipient)
    
    # Send single message with both notification and unread count
    # This prevents duplicate toasts
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'notification_message',
            'notification': serializer.data,
            'unread_count': unread_count
        }
    )


def get_user_notifications(user: User, unread_only: bool = False):
    """
    Get notifications for a user.
    
    Args:
        user: User to get notifications for
        unread_only: If True, only return unread notifications
    
    Returns:
        QuerySet of Notification objects
    """
    notifications = Notification.objects.filter(recipient=user)
    
    if unread_only:
        notifications = notifications.filter(is_read=False)
    
    return notifications.select_related('actor', 'recipient')


def get_unread_count(user: User) -> int:
    """
    Get count of unread notifications for a user.
    
    Args:
        user: User to count notifications for
    
    Returns:
        Number of unread notifications
    """
    return Notification.objects.filter(
        recipient=user,
        is_read=False
    ).count()


def mark_all_as_read(user: User) -> int:
    """
    Mark all notifications as read for a user.
    
    Args:
        user: User whose notifications to mark as read
    
    Returns:
        Number of notifications marked as read
    """
    from django.utils import timezone
    
    count = Notification.objects.filter(
        recipient=user,
        is_read=False
    ).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return count


def delete_notification(notification_id: int, user: User) -> bool:
    """
    Delete a notification if it belongs to the user.
    
    Args:
        notification_id: ID of notification to delete
        user: User who owns the notification
    
    Returns:
        True if deleted, False if not found or not owned by user
    """
    try:
        notification = Notification.objects.get(
            id=notification_id,
            recipient=user
        )
        notification.delete()
        return True
    except Notification.DoesNotExist:
        return False
