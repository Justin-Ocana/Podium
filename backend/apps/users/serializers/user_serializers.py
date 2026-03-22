from rest_framework import serializers

from apps.users.models import User
from apps.users.validators import validate_username, validate_avatar_file, validate_bio


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User CRUD operations.
    
    Used for updating user profile information.
    """
    avatar_url = serializers.SerializerMethodField(read_only=True)
    banner_url = serializers.SerializerMethodField(read_only=True)
    presence_status = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'avatar',
            'avatar_url',
            'banner_url',
            'bio',
            'country',
            'region',
            'steam_username',
            'steam_url',
            'riot_id',
            'battlenet_id',
            'discord_id',
            'xbox_gamertag',
            'psn_id',
            'twitter_handle',
            'twitch_username',
            'youtube_channel',
            'is_invisible',
            'presence_status',
            'is_active',
        ]
        read_only_fields = ['id', 'is_active', 'presence_status']
        extra_kwargs = {
            'password': {'write_only': True},
            'avatar': {'write_only': True}
        }
    
    def get_avatar_url(self, obj):
        """Get full URL for avatar."""
        return obj.get_avatar_url()
    
    def get_banner_url(self, obj):
        """Get full URL for banner."""
        return obj.get_banner_url()
    
    def get_presence_status(self, obj):
        """Get user's presence status."""
        return obj.get_presence_status()
    
    def validate_username(self, value):
        """Validate username format and uniqueness."""
        validate_username(value)
        
        # Check uniqueness (case-insensitive), excluding current user
        user_id = self.instance.id if self.instance else None
        if User.objects.filter(username__iexact=value).exclude(id=user_id).exists():
            raise serializers.ValidationError('This username is already taken.')
        
        return value
    
    def validate_email(self, value):
        """Validate email uniqueness."""
        # Normalize to lowercase
        value = value.lower().strip()
        
        # Check uniqueness (case-insensitive), excluding current user
        user_id = self.instance.id if self.instance else None
        if User.objects.filter(email__iexact=value).exclude(id=user_id).exists():
            raise serializers.ValidationError('This email is already registered.')
        
        return value
    
    def validate_avatar(self, value):
        """Validate avatar file."""
        if value:
            validate_avatar_file(value)
        return value
    
    def validate_bio(self, value):
        """Validate bio length."""
        if value:
            validate_bio(value)
        return value


class UserDetailSerializer(UserSerializer):
    """
    Detailed serializer for User with additional fields.
    
    Includes timestamps and other metadata.
    """
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + [
            'created_at',
            'updated_at',
            'date_joined',
            'last_login',
        ]
        read_only_fields = UserSerializer.Meta.read_only_fields + [
            'created_at',
            'updated_at',
            'date_joined',
            'last_login',
        ]
