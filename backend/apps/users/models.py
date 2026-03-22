from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from .managers import UserManager


class User(AbstractUser):
    """
    Custom User model for Podium platform.
    
    Extends Django's AbstractUser with additional fields for competitive gaming platform:
    - avatar: Profile picture
    - bio: User biography/description
    - created_at: Account creation timestamp
    - updated_at: Last update timestamp
    """
    
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text='User profile picture (max 5MB, JPEG/PNG/WebP)'
    )
    
    avatar_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text='Cloudinary URL for avatar image'
    )
    
    banner_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text='Cloudinary URL for profile banner image'
    )
    
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text='User biography or description'
    )
    
    # Location
    country = models.CharField(
        max_length=100,
        blank=True,
        help_text='User country'
    )
    
    region = models.CharField(
        max_length=100,
        blank=True,
        help_text='User region/state'
    )
    
    # Gaming Connections (stored as JSON)
    steam_username = models.CharField(
        max_length=100,
        blank=True,
        help_text='Steam username/display name'
    )
    
    steam_url = models.URLField(
        max_length=200,
        blank=True,
        help_text='Steam profile URL'
    )
    
    riot_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='Riot ID (e.g., Username#TAG)'
    )
    
    battlenet_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='Battle.net ID'
    )
    
    discord_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='Discord username (e.g., username#1234)'
    )
    
    xbox_gamertag = models.CharField(
        max_length=100,
        blank=True,
        help_text='Xbox Gamertag'
    )
    
    psn_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='PlayStation Network ID'
    )
    
    # Social Media (optional)
    twitter_handle = models.CharField(
        max_length=100,
        blank=True,
        help_text='Twitter/X handle (without @)'
    )
    
    twitch_username = models.CharField(
        max_length=100,
        blank=True,
        help_text='Twitch username'
    )
    
    youtube_channel = models.CharField(
        max_length=100,
        blank=True,
        help_text='YouTube channel URL or handle'
    )
    
    # Presence/Status
    is_invisible = models.BooleanField(
        default=False,
        help_text='User appears offline when invisible mode is enabled'
    )
    
    last_seen = models.DateTimeField(
        auto_now=True,
        help_text='Last activity timestamp'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Account creation timestamp'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last update timestamp'
    )
    
    # Define authentication field
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    # Use custom manager
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username
    
    def get_absolute_url(self):
        """
        Returns the public profile URL for this user.
        
        Returns:
            str: URL pattern /u/{username}/
        """
        return f'/u/{self.username}/'
    
    def get_avatar_url(self):
        """
        Returns the full URL to the user's avatar.
        
        Prioritizes Cloudinary URL over local file upload.
        If no avatar is uploaded, returns None so frontend can show default.
        
        Returns:
            str or None: Full URL to avatar image or None for default
        """
        # Prioritize Cloudinary URL
        if self.avatar_url:
            return self.avatar_url
        
        # Fallback to local file
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        
        # Return None to let frontend handle default avatar
        return None
    
    def get_banner_url(self):
        """
        Returns the full URL to the user's profile banner.
        
        Returns:
            str or None: Full URL to banner image or None if not set
        """
        return self.banner_url if self.banner_url else None
    
    def get_presence_status(self):
        """
        Returns the user's presence status.
        
        Returns:
            str: 'online' if active within 5 minutes and not invisible, otherwise 'offline'
        """
        from django.utils import timezone
        from datetime import timedelta
        
        # If invisible mode is enabled, always show offline
        if self.is_invisible:
            return 'offline'
        
        # Check if user was active in the last 5 minutes
        if self.last_seen:
            time_diff = timezone.now() - self.last_seen
            if time_diff < timedelta(minutes=5):
                return 'online'
        
        return 'offline'
