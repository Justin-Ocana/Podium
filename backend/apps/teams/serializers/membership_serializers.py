"""
Membership serializers for Podium platform.

This module contains serializers for team membership operations:
- MembershipSerializer: For reading membership data with nested user info
- InvitePlayerSerializer: For inviting players to teams
- TransferCaptainSerializer: For transferring team captaincy
- RemoveMemberSerializer: For removing members from teams
"""

from rest_framework import serializers
from apps.teams.models import TeamMembership


class UserNestedSerializer(serializers.Serializer):
    """
    Nested serializer for user data in memberships.
    
    Includes username and avatar_url for display purposes.
    """
    username = serializers.CharField(read_only=True)
    avatar_url = serializers.SerializerMethodField(read_only=True)
    
    def get_avatar_url(self, obj):
        """Get full URL for user's avatar."""
        return obj.get_avatar_url()


class MembershipSerializer(serializers.ModelSerializer):
    """
    Serializer for reading team membership data.
    
    Fields: id, user (nested username and avatar_url), role, status, joined_at
    """
    user = UserNestedSerializer(read_only=True)
    
    class Meta:
        model = TeamMembership
        fields = ['id', 'user', 'role', 'status', 'joined_at']
        read_only_fields = ['id', 'user', 'role', 'status', 'joined_at']


class InvitePlayerSerializer(serializers.Serializer):
    """
    Serializer for inviting a player to a team.
    
    Fields: user_id
    """
    user_id = serializers.IntegerField(required=True)
    
    def validate_user_id(self, value):
        """Validate that user_id is a positive integer."""
        if value <= 0:
            raise serializers.ValidationError('User ID must be a positive integer.')
        return value


class TransferCaptainSerializer(serializers.Serializer):
    """
    Serializer for transferring team captaincy.
    
    Fields: user_id
    """
    user_id = serializers.IntegerField(required=True)
    
    def validate_user_id(self, value):
        """Validate that user_id is a positive integer."""
        if value <= 0:
            raise serializers.ValidationError('User ID must be a positive integer.')
        return value


class RemoveMemberSerializer(serializers.Serializer):
    """
    Serializer for removing a member from a team.
    
    Fields: user_id
    """
    user_id = serializers.IntegerField(required=True)
    
    def validate_user_id(self, value):
        """Validate that user_id is a positive integer."""
        if value <= 0:
            raise serializers.ValidationError('User ID must be a positive integer.')
        return value



class TeamNestedSerializer(serializers.Serializer):
    """
    Nested serializer for team data in memberships.
    
    Includes team details for display in My Teams page.
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    tag = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)
    logo_url = serializers.SerializerMethodField(read_only=True)
    banner_url = serializers.SerializerMethodField(read_only=True)
    primary_color = serializers.CharField(read_only=True)
    secondary_color = serializers.CharField(read_only=True)
    captain = UserNestedSerializer(read_only=True)
    members_count = serializers.SerializerMethodField(read_only=True)
    tournaments_count = serializers.SerializerMethodField(read_only=True)
    game = serializers.SerializerMethodField(read_only=True)
    
    def get_logo_url(self, obj):
        """Get full URL for team's logo."""
        return obj.get_logo_url()
    
    def get_banner_url(self, obj):
        """Get full URL for team's banner."""
        return obj.get_banner_url()
    
    def get_members_count(self, obj):
        """Get count of active members."""
        return obj.memberships.filter(status='active').count()
    
    def get_tournaments_count(self, obj):
        """Get count of tournaments the team participated in."""
        # TODO: Implement when tournaments are ready
        return 0
    
    def get_game(self, obj):
        """Get game data if team has a game."""
        if obj.game:
            return {
                'id': obj.game.id,
                'name': obj.game.name,
                'cover_url': obj.game.cover_url
            }
        return None


class TeamMembershipSerializer(serializers.ModelSerializer):
    """
    Serializer for team memberships with nested team data.
    
    Used for My Teams page to show user's teams with full team details.
    Fields: id, team (nested), role, status, joined_at
    """
    team = TeamNestedSerializer(read_only=True)
    
    class Meta:
        model = TeamMembership
        fields = ['id', 'team', 'role', 'status', 'joined_at']
        read_only_fields = ['id', 'team', 'role', 'status', 'joined_at']
