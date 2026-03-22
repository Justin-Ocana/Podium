from rest_framework import serializers

from apps.users.models import User


class PublicProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for public user profiles.
    
    Excludes sensitive information like email and password.
    Only shows publicly visible information.
    """
    avatar_url = serializers.SerializerMethodField(read_only=True)
    profile_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'avatar_url',
            'profile_url',
            'bio',
            'created_at',
        ]
        read_only_fields = fields
    
    def get_avatar_url(self, obj):
        """Get full URL for avatar."""
        return obj.get_avatar_url()
    
    def get_profile_url(self, obj):
        """Get public profile URL."""
        return obj.get_absolute_url()


class UserStatsSerializer(serializers.Serializer):
    """
    Serializer for user statistics.
    
    Aggregates data from related models (teams, tournaments, matches).
    """
    teams_count = serializers.IntegerField(read_only=True)
    tournaments_played_count = serializers.IntegerField(read_only=True)
    tournaments_organized_count = serializers.IntegerField(read_only=True)
    matches_won_count = serializers.IntegerField(read_only=True)
    matches_lost_count = serializers.IntegerField(read_only=True)
    matches_total_count = serializers.IntegerField(read_only=True)
    winrate = serializers.FloatField(read_only=True)
    
    def to_representation(self, instance):
        """
        Calculate statistics from user instance.
        
        Args:
            instance: User instance
            
        Returns:
            dict: Statistics data
        """
        # Get counts using reverse relationships
        # Note: These will be implemented when teams, tournaments, and matches apps are ready
        teams_count = 0
        tournaments_played_count = 0
        tournaments_organized_count = 0
        matches_won_count = 0
        matches_lost_count = 0
        
        # Try to get actual counts if relationships exist
        try:
            teams_count = instance.teams.count() if hasattr(instance, 'teams') else 0
        except:
            pass
        
        try:
            tournaments_organized_count = instance.organized_tournaments.count() if hasattr(instance, 'organized_tournaments') else 0
        except:
            pass
        
        # Calculate totals
        matches_total_count = matches_won_count + matches_lost_count
        
        # Calculate winrate
        if matches_total_count > 0:
            winrate = (matches_won_count / matches_total_count) * 100
        else:
            winrate = 0.0
        
        return {
            'teams_count': teams_count,
            'tournaments_played_count': tournaments_played_count,
            'tournaments_organized_count': tournaments_organized_count,
            'matches_won_count': matches_won_count,
            'matches_lost_count': matches_lost_count,
            'matches_total_count': matches_total_count,
            'winrate': round(winrate, 2),
        }
