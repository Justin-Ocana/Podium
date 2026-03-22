"""
Public profile views.

Handles public user profile viewing and statistics.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.users.models import User
from apps.users.serializers import PublicProfileSerializer, UserStatsSerializer
from apps.users.selectors import get_user_by_username, get_user_stats


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for public user profiles (read-only).
    
    Endpoints:
    - GET /api/profiles/ - List public profiles
    - GET /api/profiles/{id}/ - Get profile by ID
    - GET /api/profiles/{username}/ - Get profile by username
    - GET /api/profiles/{id}/stats/ - Get user statistics
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = PublicProfileSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'
    
    def get_queryset(self):
        """
        Filter queryset to only show active users.
        """
        return super().get_queryset().order_by('-created_at')
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve user profile by ID or username.
        
        Supports both /api/profiles/123/ and /api/profiles/username/
        """
        lookup_value = kwargs.get('id')
        
        # Try to get by ID first
        if lookup_value.isdigit():
            try:
                instance = self.get_queryset().get(id=int(lookup_value))
            except User.DoesNotExist:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # Try to get by username
            instance = get_user_by_username(lookup_value)
            if not instance or not instance.is_active:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, id=None):
        """
        Get user statistics.
        
        GET /api/profiles/{id}/stats/
        
        Returns:
            - teams_count
            - tournaments_played_count
            - tournaments_organized_count
            - matches_won_count
            - matches_lost_count
            - matches_total_count
            - winrate
        """
        # Get user
        try:
            if id.isdigit():
                user = self.get_queryset().get(id=int(id))
            else:
                user = get_user_by_username(id)
                if not user or not user.is_active:
                    raise User.DoesNotExist
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get statistics
        stats = get_user_stats(user)
        
        # Serialize and return
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)
