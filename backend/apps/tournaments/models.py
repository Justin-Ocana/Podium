from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.text import slugify
import re
from apps.users.models import User


class Tournament(models.Model):
    """
    Tournament model for Podium platform.
    
    Represents a competitive tournament with configuration, rules, and lifecycle management.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('in_progress', 'In Progress'),
        ('finished', 'Finished'),
        ('cancelled', 'Cancelled'),
    ]
    
    FORMAT_CHOICES = [
        ('single_elimination', 'Single Elimination'),
        ('double_elimination', 'Double Elimination'),
        ('round_robin', 'Round Robin'),
        ('swiss', 'Swiss'),
    ]
    
    PARTICIPANT_TYPE_CHOICES = [
        ('teams', 'Teams'),
        ('players', 'Players'),
    ]
    
    # Basic information
    name = models.CharField(
        max_length=100,
        help_text='Tournament name (3-100 characters)',
        validators=[MinLengthValidator(3)]
    )
    
    slug = models.SlugField(
        max_length=120,
        unique=True,
        help_text='URL-friendly identifier generated from tournament name'
    )
    
    description = models.TextField(
        max_length=2000,
        blank=True,
        help_text='Tournament description'
    )
    
    game = models.CharField(
        max_length=100,
        help_text='Game name (e.g., League of Legends, Valorant)'
    )
    
    banner = models.ImageField(
        upload_to='tournament_banners/',
        blank=True,
        null=True,
        help_text='Tournament banner image (max 10MB, JPEG/PNG/WebP)'
    )
    
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_tournaments',
        help_text='User who created and manages the tournament'
    )
    
    # Configuration
    format = models.CharField(
        max_length=20,
        choices=FORMAT_CHOICES,
        default='single_elimination',
        help_text='Tournament bracket format'
    )
    
    participant_type = models.CharField(
        max_length=10,
        choices=PARTICIPANT_TYPE_CHOICES,
        default='teams',
        help_text='Type of participants (teams or individual players)'
    )
    
    max_participants = models.PositiveIntegerField(
        help_text='Maximum number of participants allowed'
    )
    
    # Dates
    registration_start = models.DateTimeField(
        help_text='When registration opens'
    )
    
    registration_end = models.DateTimeField(
        help_text='When registration closes'
    )
    
    start_date = models.DateTimeField(
        help_text='When tournament starts'
    )
    
    # Status
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='draft',
        help_text='Current tournament status'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Tournament creation timestamp'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last update timestamp'
    )
    
    class Meta:
        db_table = 'tournaments'
        verbose_name = 'Tournament'
        verbose_name_plural = 'Tournaments'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """
        Returns the public profile URL for this tournament.
        
        Returns:
            str: URL pattern /tournaments/{slug}/
        """
        return f'/tournaments/{self.slug}/'
    
    def get_banner_url(self):
        """
        Returns the full URL to the tournament's banner.
        
        If no banner is uploaded, returns a default banner URL.
        
        Returns:
            str: Full URL to banner image or default banner
        """
        if self.banner and hasattr(self.banner, 'url'):
            return self.banner.url
        return '/static/images/default-tournament-banner.png'
    
    def _generate_unique_slug(self, base_slug):
        """
        Generate a unique slug by appending numeric suffix if needed.
        
        Args:
            base_slug (str): The base slug to make unique
            
        Returns:
            str: A unique slug (max 120 characters)
        """
        slug = base_slug[:120]
        
        if not Tournament.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            return slug
        
        counter = 1
        while True:
            suffix = f'-{counter}'
            max_base_length = 120 - len(suffix)
            unique_slug = f'{base_slug[:max_base_length]}{suffix}'
            
            if not Tournament.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                return unique_slug
            
            counter += 1
            
            if counter > 9999:
                raise ValueError('Unable to generate unique slug after 9999 attempts')
    
    def _generate_slug_from_name(self):
        """
        Generate slug from tournament name.
        
        Returns:
            str: Generated slug
        """
        slug = self.name.lower().strip()
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        
        return slug
    
    def save(self, *args, **kwargs):
        """
        Override save to automatically generate slug from name.
        """
        if not self.pk or (self.pk and self._state.adding is False):
            if self.pk:
                try:
                    old_instance = Tournament.objects.get(pk=self.pk)
                    name_changed = old_instance.name != self.name
                except Tournament.DoesNotExist:
                    name_changed = False
            else:
                name_changed = True
            
            if name_changed or not self.slug:
                base_slug = self._generate_slug_from_name()
                self.slug = self._generate_unique_slug(base_slug)
        
        super().save(*args, **kwargs)


class TournamentSettings(models.Model):
    """
    Technical settings for tournament bracket configuration.
    
    Stores bracket-specific settings that will be used by the brackets app.
    """
    
    tournament = models.OneToOneField(
        Tournament,
        on_delete=models.CASCADE,
        related_name='settings',
        help_text='Tournament these settings belong to'
    )
    
    # Bracket configuration
    bracket_size = models.PositiveIntegerField(
        help_text='Size of the bracket (e.g., 8, 16, 32, 64)'
    )
    
    number_of_rounds = models.PositiveIntegerField(
        default=1,
        help_text='Number of rounds in the tournament'
    )
    
    third_place_match = models.BooleanField(
        default=False,
        help_text='Whether to include a third place match'
    )
    
    has_group_stage = models.BooleanField(
        default=False,
        help_text='Whether tournament has a group stage before playoffs'
    )
    
    # Match configuration
    match_format = models.CharField(
        max_length=10,
        choices=[
            ('bo1', 'Best of 1'),
            ('bo3', 'Best of 3'),
            ('bo5', 'Best of 5'),
        ],
        default='bo1',
        help_text='Match format (Best of X)'
    )
    
    class Meta:
        db_table = 'tournament_settings'
        verbose_name = 'Tournament Settings'
        verbose_name_plural = 'Tournament Settings'
    
    def __str__(self):
        return f'Settings for {self.tournament.name}'


class TournamentRules(models.Model):
    """
    Custom rules and regulations for a tournament.
    
    Stores tournament-specific rules that participants must follow.
    """
    
    tournament = models.OneToOneField(
        Tournament,
        on_delete=models.CASCADE,
        related_name='rules',
        help_text='Tournament these rules belong to'
    )
    
    rules_text = models.TextField(
        help_text='Tournament rules and regulations in markdown format'
    )
    
    # Optional specific rules
    map_pool = models.CharField(
        max_length=500,
        blank=True,
        help_text='Allowed maps (comma-separated)'
    )
    
    time_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Time limit per match in minutes'
    )
    
    custom_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional custom settings as JSON'
    )
    
    class Meta:
        db_table = 'tournament_rules'
        verbose_name = 'Tournament Rules'
        verbose_name_plural = 'Tournament Rules'
    
    def __str__(self):
        return f'Rules for {self.tournament.name}'
