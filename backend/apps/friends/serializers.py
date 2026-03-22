"""
Friends serializers.
"""
from rest_framework import serializers
from apps.users.serializers.user_serializers import UserSerializer
from .models import FriendRequest, Friendship


class FriendRequestSerializer(serializers.ModelSerializer):
    """Serializer for FriendRequest model."""
    
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)
    
    class Meta:
        model = FriendRequest
        fields = [
            'id',
            'from_user',
            'to_user',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']


class FriendshipSerializer(serializers.ModelSerializer):
    """Serializer for Friendship model."""
    
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)
    
    class Meta:
        model = Friendship
        fields = [
            'id',
            'user1',
            'user2',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SendFriendRequestSerializer(serializers.Serializer):
    """Serializer for sending a friend request."""
    
    to_username = serializers.CharField(
        max_length=150,
        help_text='Username of the user to send friend request to'
    )
