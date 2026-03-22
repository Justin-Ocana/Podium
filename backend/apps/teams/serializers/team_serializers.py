"""
Team serializers for Podium platform.

This module contains serializers for Team CRUD operations:
- TeamCreateSerializer: For creating new teams
- TeamSerializer: For reading team data with full details
- TeamUpdateSerializer: For updating team information
- TeamListSerializer: For listing teams with reduced fields
"""

from rest_framework import serializers
from apps.teams.models import Team, Game
from apps.teams.validators import validate_team_name, validate_team_description
from apps.teams.serializers.game_serializers import GameSerializer


class CaptainNestedSerializer(serializers.Serializer):
    """
    Nested serializer for captain user data.
    
    Includes username and avatar_url for display purposes.
    """
    username = serializers.CharField(read_only=True)
    avatar_url = serializers.SerializerMethodField(read_only=True)
    
    def get_avatar_url(self, obj):
        """Get full URL for captain's avatar."""
        return obj.get_avatar_url()


class TeamCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new teams.
    
    Fields: name, tag, game_id, description, 
            primary_color, secondary_color, country, region, looking_for_players
    
    Note: logo and banner are uploaded separately via upload endpoints
    """
    game_id = serializers.IntegerField(write_only=True, help_text='RAWG game ID')
    
    class Meta:
        model = Team
        fields = [
            'name', 
            'tag',
            'game_id',
            'description', 
            'primary_color',
            'secondary_color',
            'country',
            'region',
            'looking_for_players'
        ]
    
    def validate_name(self, value):
        """Validate team name format and uniqueness."""
        validate_team_name(value)
        
        # Check uniqueness (case-insensitive)
        if Team.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError('A team with this name already exists.')
        
        return value
    
    def validate_tag(self, value):
        """Validate team tag format and uniqueness."""
        if not value:
            raise serializers.ValidationError('Tag is required.')
        
        # Auto-uppercase
        value = value.upper()
        
        # Length validation
        if len(value) < 2 or len(value) > 5:
            raise serializers.ValidationError('Tag must be between 2 and 5 characters.')
        
        # Check uniqueness (case-insensitive)
        if Team.objects.filter(tag__iexact=value).exists():
            raise serializers.ValidationError('A team with this tag already exists.')
        
        return value
    
    def validate_game_id(self, value):
        """Validate that the game exists in cache."""
        try:
            Game.objects.get(rawg_id=value)
        except Game.DoesNotExist:
            raise serializers.ValidationError('Game not found. Please search for the game first.')
        return value
    
    def validate_description(self, value):
        """Validate team description length."""
        if value:
            validate_team_description(value)
        return value
    
    def create(self, validated_data):
        """Create team with game relationship."""
        game_id = validated_data.pop('game_id')
        game = Game.objects.get(rawg_id=game_id)
        validated_data['game'] = game
        
        # Call the service to create team
        from apps.teams.services import create_team
        team = create_team(
            creator=self.context['request'].user,
            **validated_data
        )
        return team


class TeamSerializer(serializers.ModelSerializer):
    """
    Serializer for reading team data with full details.
    
    Fields: id, name, slug, tag, logo_url, banner_url, description, game, 
            primary_color, secondary_color, country, region, looking_for_players,
            captain (nested), member_count, created_at, updated_at
    """
    logo_url = serializers.SerializerMethodField(read_only=True)
    banner_url = serializers.SerializerMethodField(read_only=True)
    captain = CaptainNestedSerializer(read_only=True)
    member_count = serializers.SerializerMethodField(read_only=True)
    game = GameSerializer(read_only=True)
    
    class Meta:
        model = Team
        fields = [
            'id',
            'name',
            'slug',
            'tag',
            'logo_url',
            'banner_url',
            'description',
            'game',
            'primary_color',
            'secondary_color',
            'country',
            'region',
            'looking_for_players',
            'captain',
            'member_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_logo_url(self, obj):
        """Get full URL for team logo."""
        return obj.get_logo_url()
    
    def get_banner_url(self, obj):
        """Get full URL for team banner."""
        return obj.get_banner_url() if hasattr(obj, 'get_banner_url') else None
    
    def get_member_count(self, obj):
        """Get count of active team members."""
        return obj.memberships.filter(status='active').count()


class TeamUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating team information.
    
    Fields: name, tag, description, primary_color, 
            secondary_color, country, region, looking_for_players
    
    Note: logo and banner are uploaded separately via upload endpoints
    """
    
    class Meta:
        model = Team
        fields = [
            'name', 
            'tag',
            'description', 
            'primary_color',
            'secondary_color',
            'country',
            'region',
            'looking_for_players'
        ]
    
    def validate_name(self, value):
        """Validate team name format and uniqueness."""
        validate_team_name(value)
        
        # Check uniqueness (case-insensitive), excluding current team
        team_id = self.instance.id if self.instance else None
        if Team.objects.filter(name__iexact=value).exclude(id=team_id).exists():
            raise serializers.ValidationError('A team with this name already exists.')
        
        return value
    
    def validate_tag(self, value):
        """Validate team tag format and uniqueness."""
        if not value:
            raise serializers.ValidationError('Tag is required.')
        
        # Auto-uppercase
        value = value.upper()
        
        # Length validation
        if len(value) < 2 or len(value) > 5:
            raise serializers.ValidationError('Tag must be between 2 and 5 characters.')
        
        # Check uniqueness (case-insensitive), excluding current team
        team_id = self.instance.id if self.instance else None
        if Team.objects.filter(tag__iexact=value).exclude(id=team_id).exists():
            raise serializers.ValidationError('A team with this tag already exists.')
        
        return value
    
    def validate_description(self, value):
        """Validate team description length."""
        if value:
            validate_team_description(value)
        return value


class TeamListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing teams with reduced fields.
    
    Fields: id, name, slug, tag, logo_url, banner_url, primary_color, secondary_color, 
            game, member_count, looking_for_players, captain
    """
    logo_url = serializers.SerializerMethodField(read_only=True)
    banner_url = serializers.SerializerMethodField(read_only=True)
    member_count = serializers.SerializerMethodField(read_only=True)
    game = GameSerializer(read_only=True)
    captain = CaptainNestedSerializer(read_only=True)
    
    class Meta:
        model = Team
        fields = [
            'id',
            'name',
            'slug',
            'tag',
            'logo_url',
            'banner_url',
            'primary_color',
            'secondary_color',
            'game',
            'captain',
            'member_count',
            'looking_for_players',
        ]
        read_only_fields = ['id', 'slug']
    
    def get_logo_url(self, obj):
        """Get full URL for team logo."""
        return obj.get_logo_url()
    
    def get_banner_url(self, obj):
        """Get full URL for team banner."""
        return obj.get_banner_url() if hasattr(obj, 'get_banner_url') else None
    
    def get_member_count(self, obj):
        """Get count of active team members."""
        return obj.memberships.filter(status='active').count()
