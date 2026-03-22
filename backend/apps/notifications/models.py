"""
Notifications app models.

This app provides a scalable notification system for the Podium platform.
It supports various event types and can be extended to support real-time notifications,
emails, and push notifications in the future.
"""
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from apps.users.models import User


class NotificationType(models.TextChoices):
    """
    Notification types for different events in the system.
    
    This enum makes it easy to add new notification types without changing the model.
    """
    # Friend/Social notifications
    FRIEND_REQUEST = 'FRIEND_REQUEST', 'Friend Request'
    FRIEND_ACCEPTED = 'FRIEND_ACCEPTED', 'Friend Accepted'
    
    # Team notifications
    TEAM_INVITE = 'TEAM_INVITE', 'Team Invitation'
    TEAM_MEMBER_JOINED = 'TEAM_MEMBER_JOINED', 'Team Member Joined'
    TEAM_MEMBER_LEFT = 'TEAM_MEMBER_LEFT', 'Team Member Left'
    
    # Tournament notifications
    TOURNAMENT_STARTED = 'TOURNAMENT_STARTED', 'Tournament Started'
    TOURNAMENT_FINISHED = 'TOURNAMENT_FINISHED', 'Tournament Finished'
    TOURNAMENT_INVITE = 'TOURNAMENT_INVITE', 'Tournament Invitation'
    
    # Match notifications
    MATCH_SCHEDULED = 'MATCH_SCHEDULED', 'Match Scheduled'
    MATCH_RESULT_SUBMITTED = 'MATCH_RESULT_SUBMITTED', 'Match Result Submitted'
    
    # System notifications
    SYSTEM_ANNOUNCEMENT = 'SYSTEM_ANNOUNCEMENT', 'System Announcement'


class Notification(models.Model):
    """
    Notification model for storing user notifications.
    
    Uses Generic Foreign Keys to support notifications for any model in the system.
    This makes the system flexible and scalable.
    
    Example:
        User A sends friend request to User B
        → Notification created with:
            - recipient: User B
            - actor: User A
            - type: FRIEND_REQUEST
            - message: "Juan sent you a friend request"
            - related_object: FriendRequest instance
    """
    
    # Who receives the notification
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text='User who receives this notification'
    )
    
    # Who triggered the notification (optional, can be None for system notifications)
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='triggered_notifications',
        null=True,
        blank=True,
        help_text='User who triggered this notification'
    )
    
    # Type of notification
    type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        help_text='Type of notification event'
    )
    
    # Message to display
    message = models.TextField(
        help_text='Notification message to display to the user'
    )
    
    # Generic relation to any model (FriendRequest, Team, Tournament, etc.)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='Type of the related object'
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='ID of the related object'
    )
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # Status
    is_read = models.BooleanField(
        default=False,
        help_text='Whether the notification has been read'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When the notification was created'
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the notification was read'
    )
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]
    
    def __str__(self):
        return f'{self.type} for {self.recipient.username}'
    
    def mark_as_read(self):
        """Mark this notification as read."""
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_unread(self):
        """Mark this notification as unread."""
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save(update_fields=['is_read', 'read_at'])
