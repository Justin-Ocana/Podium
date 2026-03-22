from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import re
from apps.users.models import User


class Team(models.Model):
    """
    Team model for Podium platform.
    
    Represents a competitive esports team with full customization support.
    Universal design supports any competitive game (Valorant, CS2, LoL, Rocket League, etc.)
    """
    
    # Core fields (required)
    name = models.CharField(
        max_length=50,
        help_text='Team name (3-50 characters, unique case-insensitive)',
        validators=[MinLengthValidator(3)]
    )
    
    tag = models.CharField(
        max_length=5,
        unique=True,
        help_text='Team tag/abbreviation (2-5 characters, e.g., PHX, NVX)',
        validators=[MinLengthValidator(2), MaxLengthValidator(5)]
    )
    
    slug = models.SlugField(
        max_length=60,
        unique=True,
        help_text='URL-friendly identifier generated from team name'
    )
    
    logo_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text='Cloudinary URL for team logo'
    )
    
    description = models.TextField(
        max_length=1000,
        blank=True,
        help_text='Team description or bio'
    )
    
    captain = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teams_as_captain',
        help_text='Team captain with administrative permissions'
    )
    
    # Game
    game = models.ForeignKey(
        'Game',
        on_delete=models.PROTECT,
        related_name='primary_teams',
        blank=True,
        null=True,
        help_text='Primary game this team competes in'
    )
    
    # Branding & Customization (recommended)
    banner_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text='Cloudinary URL for team banner image'
    )
    
    primary_color = models.CharField(
        max_length=7,
        blank=True,
        default='#ff4655',
        help_text='Primary brand color (hex format, e.g., #ff4655)'
    )
    
    secondary_color = models.CharField(
        max_length=7,
        blank=True,
        default='#111111',
        help_text='Secondary brand color (hex format, e.g., #111111)'
    )
    
    # Location
    country = models.CharField(
        max_length=100,
        blank=True,
        help_text='Team country (e.g., Ecuador, Spain, USA)'
    )
    
    region = models.CharField(
        max_length=100,
        blank=True,
        help_text='Team region (e.g., LATAM, NA, EU, APAC)'
    )
    
    # Optional fields
    is_verified = models.BooleanField(
        default=False,
        help_text='Verified/official team badge'
    )
    
    sponsor = models.CharField(
        max_length=100,
        blank=True,
        help_text='Team sponsor (e.g., Red Bull, Monster Energy)'
    )
    
    founded_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Year the team was founded'
    )
    
    website = models.URLField(
        max_length=200,
        blank=True,
        help_text='Team website URL'
    )
    
    looking_for_players = models.BooleanField(
        default=False,
        help_text='Whether the team is actively looking for new players'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Team creation timestamp'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last update timestamp'
    )
    
    class Meta:
        db_table = 'teams'
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tag']),
            models.Index(fields=['slug']),
            models.Index(fields=['country']),
            models.Index(fields=['region']),
        ]
    
    def __str__(self):
        return f'{self.name} ({self.tag})'
    
    def get_absolute_url(self):
        """Returns the public profile URL for this team."""
        return f'/teams/{self.slug}/'
    
    def get_logo_url(self):
        """Returns the full URL to the team's logo."""
        if self.logo_url:
            return self.logo_url
        return '/static/images/default-team-logo.png'
    
    def get_banner_url(self):
        """Returns the full URL to the team's banner."""
        if self.banner_url:
            return self.banner_url
        return None
    
    def _generate_unique_slug(self, base_slug):
        """Generate a unique slug by appending numeric suffix if needed."""
        slug = base_slug[:60]
        
        if not Team.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            return slug
        
        counter = 1
        while True:
            suffix = f'-{counter}'
            max_base_length = 60 - len(suffix)
            unique_slug = f'{base_slug[:max_base_length]}{suffix}'
            
            if not Team.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                return unique_slug
            
            counter += 1
            
            if counter > 9999:
                raise ValueError('Unable to generate unique slug after 9999 attempts')
    
    def _generate_slug_from_name(self):
        """Generate slug from team name."""
        slug = self.name.lower().strip()
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        return slug
    
    def save(self, *args, **kwargs):
        """Override save to automatically generate slug and normalize tag."""
        # Normalize tag to uppercase
        if self.tag:
            self.tag = self.tag.upper().strip()
        
        # Generate slug if needed
        if not self.pk or (self.pk and self._state.adding is False):
            if self.pk:
                try:
                    old_instance = Team.objects.get(pk=self.pk)
                    name_changed = old_instance.name != self.name
                except Team.DoesNotExist:
                    name_changed = False
            else:
                name_changed = True
            
            if name_changed or not self.slug:
                base_slug = self._generate_slug_from_name()
                self.slug = self._generate_unique_slug(base_slug)
        
        super().save(*args, **kwargs)


class TeamMembership(models.Model):
    """
    Intermediate model representing membership between User and Team.
    
    Supports multiple roles for flexible team structures:
    - captain: Team leader with full permissions
    - player: Active roster player
    - manager: Team manager (can manage roster but not edit team)
    - coach: Team coach (advisory role)
    """
    
    ROLE_CHOICES = [
        ('captain', 'Captain'),
        ('player', 'Player'),
        ('manager', 'Manager'),
        ('coach', 'Coach'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('left', 'Left'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='team_memberships',
        help_text='User who is a member of the team'
    )
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='memberships',
        help_text='Team that the user is a member of'
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        help_text='Role of the user in the team'
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        help_text='Status of the membership'
    )
    
    joined_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when the membership was created'
    )
    
    class Meta:
        db_table = 'team_memberships'
        verbose_name = 'Team Membership'
        verbose_name_plural = 'Team Memberships'
        ordering = ['joined_at']
        unique_together = [('user', 'team')]
        indexes = [
            models.Index(fields=['team', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['team', 'role', 'status']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.team.name} ({self.role})'
    
    def clean(self):
        """Validate that there is exactly one captain with status='active' per team."""
        super().clean()
        
        if self.role == 'captain' and self.status == 'active':
            existing_captains = TeamMembership.objects.filter(
                team=self.team,
                role='captain',
                status='active'
            ).exclude(pk=self.pk if self.pk else None)
            
            if existing_captains.exists():
                raise ValidationError(
                    'A team can only have one active captain. '
                    'Transfer captaincy before assigning a new captain.'
                )
        
        if self.pk:
            try:
                old_instance = TeamMembership.objects.get(pk=self.pk)
                was_active_captain = (
                    old_instance.role == 'captain' and 
                    old_instance.status == 'active'
                )
                will_be_active_captain = (
                    self.role == 'captain' and 
                    self.status == 'active'
                )
                
                if was_active_captain and not will_be_active_captain:
                    other_captains = TeamMembership.objects.filter(
                        team=self.team,
                        role='captain',
                        status='active'
                    ).exclude(pk=self.pk)
                    
                    if not other_captains.exists():
                        raise ValidationError(
                            'Cannot remove the only active captain. '
                            'Transfer captaincy to another member first.'
                        )
            except TeamMembership.DoesNotExist:
                pass
    
    def save(self, *args, **kwargs):
        """Override save to call clean() for validation."""
        if 'update_fields' not in kwargs:
            self.full_clean()
        super().save(*args, **kwargs)


class TeamJoinRequest(models.Model):
    """
    Model for join requests from users wanting to join a team.
    
    Users can request to join a team, and the captain/manager can accept or reject.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='join_requests',
        help_text='Team the user wants to join'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='team_join_requests',
        help_text='User requesting to join'
    )
    
    message = models.TextField(
        max_length=500,
        blank=True,
        help_text='Optional message from the user'
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Status of the join request'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When the request was created'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When the request was last updated'
    )
    
    class Meta:
        db_table = 'team_join_requests'
        verbose_name = 'Team Join Request'
        verbose_name_plural = 'Team Join Requests'
        ordering = ['-created_at']
        unique_together = [('team', 'user')]
        indexes = [
            models.Index(fields=['team', 'status']),
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f'{self.user.username} → {self.team.name} ({self.status})'


class TeamInvite(models.Model):
    """
    Model for team invitations sent by captain/manager to users.
    
    Captain or manager can invite users to join the team.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='invites',
        help_text='Team sending the invitation'
    )
    
    invited_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='team_invites_received',
        help_text='User being invited'
    )
    
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='team_invites_sent',
        help_text='Captain/manager who sent the invitation'
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Status of the invitation'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When the invitation was created'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When the invitation was last updated'
    )
    
    class Meta:
        db_table = 'team_invites'
        verbose_name = 'Team Invite'
        verbose_name_plural = 'Team Invites'
        ordering = ['-created_at']
        unique_together = [('team', 'invited_user')]
        indexes = [
            models.Index(fields=['team', 'status']),
            models.Index(fields=['invited_user', 'status']),
        ]
    
    def __str__(self):
        return f'{self.team.name} → {self.invited_user.username} ({self.status})'


class Game(models.Model):
    """
    Model for games cached from RAWG API.
    
    Stores essential game data locally to minimize API calls.
    Games are fetched on-demand when users search/select them.
    """
    
    rawg_id = models.IntegerField(
        unique=True,
        help_text='Game ID from RAWG API'
    )
    
    name = models.CharField(
        max_length=200,
        help_text='Game name (e.g., Valorant, CS2)'
    )
    
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text='URL-friendly identifier from RAWG'
    )
    
    cover_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text='Game cover/background image from RAWG'
    )
    
    genres = models.JSONField(
        default=list,
        blank=True,
        help_text='Game genres (e.g., ["FPS", "Shooter"])'
    )
    
    platforms = models.JSONField(
        default=list,
        blank=True,
        help_text='Available platforms (e.g., ["PC", "PlayStation", "Xbox"])'
    )
    
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='RAWG rating (0-5)'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When the game was cached locally'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last time game data was updated'
    )
    
    class Meta:
        db_table = 'games'
        verbose_name = 'Game'
        verbose_name_plural = 'Games'
        ordering = ['name']
        indexes = [
            models.Index(fields=['rawg_id']),
            models.Index(fields=['slug']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name


class TeamGame(models.Model):
    """
    Model for games that a team competes in.
    
    Links teams to games from the Game cache.
    """
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='games',
        help_text='Team that plays this game'
    )
    
    game = models.ForeignKey(
        Game,
        on_delete=models.PROTECT,
        related_name='teams',
        help_text='Game from RAWG cache'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When the game was added to team'
    )
    
    class Meta:
        db_table = 'team_games'
        verbose_name = 'Team Game'
        verbose_name_plural = 'Team Games'
        ordering = ['created_at']
        unique_together = [('team', 'game')]
        indexes = [
            models.Index(fields=['team', 'game']),
        ]
    
    def __str__(self):
        return f'{self.team.name} - {self.game.name}'


class TeamStats(models.Model):
    """
    Model for team statistics.
    
    Automatically updated when matches are completed.
    """
    
    team = models.OneToOneField(
        Team,
        on_delete=models.CASCADE,
        related_name='stats',
        primary_key=True,
        help_text='Team these stats belong to'
    )
    
    matches_played = models.PositiveIntegerField(
        default=0,
        help_text='Total matches played'
    )
    
    matches_won = models.PositiveIntegerField(
        default=0,
        help_text='Total matches won'
    )
    
    matches_lost = models.PositiveIntegerField(
        default=0,
        help_text='Total matches lost'
    )
    
    tournaments_played = models.PositiveIntegerField(
        default=0,
        help_text='Total tournaments participated in'
    )
    
    tournaments_won = models.PositiveIntegerField(
        default=0,
        help_text='Total tournaments won'
    )
    
    winrate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text='Win rate percentage (0-100)'
    )
    
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text='When stats were last updated'
    )
    
    class Meta:
        db_table = 'team_stats'
        verbose_name = 'Team Stats'
        verbose_name_plural = 'Team Stats'
    
    def __str__(self):
        return f'{self.team.name} Stats'
    
    def recalculate_winrate(self):
        """Recalculate win rate based on matches played."""
        if self.matches_played > 0:
            self.winrate = round((self.matches_won / self.matches_played) * 100, 2)
        else:
            self.winrate = 0.00
        self.save(update_fields=['winrate', 'last_updated'])


class TeamSocial(models.Model):
    """
    Model for team social media links.
    
    Stores links to team's social media profiles and community platforms.
    """
    
    PLATFORM_CHOICES = [
        ('discord', 'Discord'),
        ('twitter', 'Twitter/X'),
        ('twitch', 'Twitch'),
        ('youtube', 'YouTube'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('tiktok', 'TikTok'),
        ('website', 'Website'),
    ]
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='social_links',
        help_text='Team these social links belong to'
    )
    
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        help_text='Social media platform'
    )
    
    url = models.URLField(
        max_length=500,
        help_text='URL to the social media profile'
    )
    
    class Meta:
        db_table = 'team_socials'
        verbose_name = 'Team Social Link'
        verbose_name_plural = 'Team Social Links'
        unique_together = [('team', 'platform')]
        indexes = [
            models.Index(fields=['team', 'platform']),
        ]
    
    def __str__(self):
        return f'{self.team.name} - {self.get_platform_display()}'


class TeamSettings(models.Model):
    """
    Model for team settings and configuration.
    
    Controls team visibility, join policy, and other preferences.
    """
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    
    JOIN_POLICY_CHOICES = [
        ('open', 'Open'),
        ('request', 'Request to Join'),
        ('invite_only', 'Invite Only'),
    ]
    
    team = models.OneToOneField(
        Team,
        on_delete=models.CASCADE,
        related_name='settings',
        primary_key=True,
        help_text='Team these settings belong to'
    )
    
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='public',
        help_text='Team visibility (public or private)'
    )
    
    join_policy = models.CharField(
        max_length=15,
        choices=JOIN_POLICY_CHOICES,
        default='request',
        help_text='How users can join the team'
    )
    
    allow_requests = models.BooleanField(
        default=True,
        help_text='Allow users to request to join'
    )
    
    max_members = models.PositiveIntegerField(
        default=10,
        help_text='Maximum number of team members'
    )
    
    class Meta:
        db_table = 'team_settings'
        verbose_name = 'Team Settings'
        verbose_name_plural = 'Team Settings'
    
    def __str__(self):
        return f'{self.team.name} Settings'
