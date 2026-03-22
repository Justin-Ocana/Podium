"""
Tournament serializers for Podium platform.
"""

from rest_framework import serializers
from apps.tournaments.models import Tournament, TournamentSettings, TournamentRules
from apps.tournaments.validators import (
    validate_tournament_name,
    validate_tournament_banner,
    validate_tournament_description,
    validate_tournament_dates,
    validate_max_participants
)


class OrganizerNestedSerializer(serializers.Serializer):
    """Nested serializer for organizer user data."""
    username = serializers.CharField(read_only=True)
    avatar_url = serializers.SerializerMethodField(read_only=True)
    
    def get_avatar_url(self, obj):
        return obj.get_avatar_url()


class TournamentSettingsSerializer(serializers.ModelSerializer):
    """Serializer for tournament settings."""
    
    class Meta:
        model = TournamentSettings
        fields = [
            'bracket_size',
            'number_of_rounds',
            'third_place_match',
            'has_group_stage',
            'match_format',
        ]


class TournamentRulesSerializer(serializers.ModelSerializer):
    """Serializer for tournament rules."""
    
    class Meta:
        model = TournamentRules
        fields = [
            'rules_text',
            'map_pool',
            'time_limit',
            'custom_settings',
        ]


class TournamentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tournaments."""
    settings = TournamentSettingsSerializer(required=False)
    rules = TournamentRulesSerializer(required=False)
    
    class Meta:
        model = Tournament
        fields = [
            'name',
            'description',
            'game',
            'banner',
            'format',
            'participant_type',
            'max_participants',
            'registration_start',
            'registration_end',
            'start_date',
            'settings',
            'rules',
        ]
    
    def validate_name(self, value):
        validate_tournament_name(value)
        return value
    
    def validate_banner(self, value):
        if value:
            validate_tournament_banner(value)
        return value
    
    def validate_description(self, value):
        if value:
            validate_tournament_description(value)
        return value
    
    def validate_max_participants(self, value):
        validate_max_participants(value)
        return value
    
    def validate(self, data):
        """Validate date logic."""
        validate_tournament_dates(
            data['registration_start'],
            data['registration_end'],
            data['start_date']
        )
        return data


class TournamentSerializer(serializers.ModelSerializer):
    """Serializer for reading tournament data with full details."""
    banner_url = serializers.SerializerMethodField(read_only=True)
    organizer = OrganizerNestedSerializer(read_only=True)
    settings = TournamentSettingsSerializer(read_only=True)
    rules = TournamentRulesSerializer(read_only=True)
    participant_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Tournament
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'game',
            'banner_url',
            'organizer',
            'format',
            'participant_type',
            'max_participants',
            'participant_count',
            'registration_start',
            'registration_end',
            'start_date',
            'status',
            'settings',
            'rules',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'status', 'created_at', 'updated_at']
    
    def get_banner_url(self, obj):
        return obj.get_banner_url()
    
    def get_participant_count(self, obj):
        """Get count of registered participants."""
        # Will be implemented when registrations app is ready
        return 0


class TournamentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tournament information."""
    settings = TournamentSettingsSerializer(required=False)
    rules = TournamentRulesSerializer(required=False)
    
    class Meta:
        model = Tournament
        fields = [
            'name',
            'description',
            'game',
            'banner',
            'format',
            'max_participants',
            'registration_start',
            'registration_end',
            'start_date',
            'settings',
            'rules',
        ]
    
    def validate_name(self, value):
        validate_tournament_name(value)
        return value
    
    def validate_banner(self, value):
        if value:
            validate_tournament_banner(value)
        return value
    
    def validate_description(self, value):
        if value:
            validate_tournament_description(value)
        return value
    
    def validate_max_participants(self, value):
        validate_max_participants(value)
        return value


class TournamentListSerializer(serializers.ModelSerializer):
    """Serializer for listing tournaments with reduced fields."""
    banner_url = serializers.SerializerMethodField(read_only=True)
    organizer_username = serializers.CharField(source='organizer.username', read_only=True)
    participant_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Tournament
        fields = [
            'id',
            'name',
            'slug',
            'game',
            'banner_url',
            'organizer_username',
            'format',
            'participant_type',
            'max_participants',
            'participant_count',
            'start_date',
            'status',
        ]
        read_only_fields = ['id', 'slug', 'status']
    
    def get_banner_url(self, obj):
        return obj.get_banner_url()
    
    def get_participant_count(self, obj):
        return 0
