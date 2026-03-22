"""
Friends app models.

This app manages friendships and friend requests between users.
"""
from django.db import models
from apps.users.models import User


class FriendRequestStatus(models.TextChoices):
    """Status choices for friend requests."""
    PENDING = 'PENDING', 'Pending'
    ACCEPTED = 'ACCEPTED', 'Accepted'
    DECLINED = 'DECLINED', 'Declined'


class FriendRequest(models.Model):
    """
    Model for friend requests between users.
    
    When a user sends a friend request to another user, a FriendRequest is created.
    The recipient can accept or decline the request.
    """
    
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_friend_requests',
        help_text='User who sent the friend request'
    )
    
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_friend_requests',
        help_text='User who received the friend request'
    )
    
    status = models.CharField(
        max_length=20,
        choices=FriendRequestStatus.choices,
        default=FriendRequestStatus.PENDING,
        help_text='Status of the friend request'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When the friend request was created'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When the friend request was last updated'
    )
    
    class Meta:
        db_table = 'friend_requests'
        verbose_name = 'Friend Request'
        verbose_name_plural = 'Friend Requests'
        ordering = ['-created_at']
        unique_together = ['from_user', 'to_user']
        indexes = [
            models.Index(fields=['to_user', 'status']),
            models.Index(fields=['from_user', 'status']),
        ]
    
    def __str__(self):
        return f'{self.from_user.username} → {self.to_user.username} ({self.status})'


class Friendship(models.Model):
    """
    Model for friendships between users.
    
    When a friend request is accepted, a Friendship is created.
    Friendships are bidirectional (if A is friends with B, B is friends with A).
    """
    
    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friendships_as_user1',
        help_text='First user in the friendship'
    )
    
    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friendships_as_user2',
        help_text='Second user in the friendship'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When the friendship was created'
    )
    
    class Meta:
        db_table = 'friendships'
        verbose_name = 'Friendship'
        verbose_name_plural = 'Friendships'
        ordering = ['-created_at']
        unique_together = ['user1', 'user2']
        indexes = [
            models.Index(fields=['user1', 'created_at']),
            models.Index(fields=['user2', 'created_at']),
        ]
    
    def __str__(self):
        return f'{self.user1.username} ↔ {self.user2.username}'
