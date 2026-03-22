"""
Notification serializers.
"""
from rest_framework import serializers
from apps.users.serializers.user_serializers import UserSerializer
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model.
    
    Includes actor information and formats timestamps.
    """
    actor = UserSerializer(read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'recipient',
            'actor',
            'type',
            'message',
            'is_read',
            'created_at',
            'read_at',
            'time_ago',
            'content_type',
            'object_id',
        ]
        read_only_fields = [
            'id',
            'recipient',
            'actor',
            'type',
            'message',
            'created_at',
            'read_at',
            'content_type',
            'object_id',
        ]
    
    def get_time_ago(self, obj):
        """
        Get human-readable time since notification was created.
        """
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return 'just now'
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f'{minutes}m ago'
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f'{hours}h ago'
        elif diff < timedelta(days=7):
            days = diff.days
            return f'{days}d ago'
        elif diff < timedelta(days=30):
            weeks = diff.days // 7
            return f'{weeks}w ago'
        else:
            months = diff.days // 30
            return f'{months}mo ago'


class NotificationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for notification lists.
    
    Only includes essential actor info to reduce payload size.
    """
    actor_username = serializers.CharField(source='actor.username', read_only=True)
    actor_avatar = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'actor_username',
            'actor_avatar',
            'type',
            'message',
            'is_read',
            'created_at',
            'time_ago',
            'object_id',
        ]
    
    def get_actor_avatar(self, obj):
        """Get actor's avatar URL."""
        if obj.actor:
            return obj.actor.get_avatar_url()
        return None
    
    def get_time_ago(self, obj):
        """Get human-readable time."""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return 'just now'
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f'{minutes}m ago'
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f'{hours}h ago'
        else:
            days = diff.days
            return f'{days}d ago'
