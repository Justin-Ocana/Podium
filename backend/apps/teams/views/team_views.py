"""
Team management views.

Handles team CRUD operations and statistics.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import ValidationError, PermissionDenied

from apps.teams.models import Team
from apps.teams.serializers import (
    TeamCreateSerializer,
    TeamSerializer,
    TeamUpdateSerializer,
    TeamListSerializer
)
from apps.teams.permissions import IsCaptain
from apps.teams.services import create_team, update_team, delete_team
from apps.teams.selectors import (
    get_team_by_id,
    get_team_by_slug,
    get_team_stats
)


class TeamPagination(PageNumberPagination):
    """
    Pagination class for team listings.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class TeamViewSet(viewsets.ModelViewSet):
    """
    ViewSet for team CRUD operations.
    
    Endpoints:
    - POST /api/teams/ - Create team (authenticated)
    - GET /api/teams/ - List teams with pagination (20 per page)
    - GET /api/teams/{id}/ - Retrieve team by ID
    - GET /api/teams/{slug}/ - Retrieve team by slug (public)
    - PATCH /api/teams/{id}/ - Update team (captain only)
    - DELETE /api/teams/{id}/ - Delete team (captain only)
    - GET /api/teams/{id}/stats/ - Get team statistics
    """
    queryset = Team.objects.select_related('captain').all()
    serializer_class = TeamSerializer
    pagination_class = TeamPagination
    lookup_field = 'pk'
    
    def get_permissions(self):
        """
        Set permissions based on action.
        
        - create: requires authentication
        - update, partial_update, destroy: requires IsCaptain
        - retrieve (by slug): public access
        - list, stats: public access
        """
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsCaptain()]
        return []
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return TeamCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TeamUpdateSerializer
        elif self.action == 'list':
            return TeamListSerializer
        return TeamSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_teams(self, request):
        """
        Get all teams where the authenticated user is a member (including as captain).
        
        Returns team memberships with team details and user's role.
        """
        from apps.teams.models import TeamMembership
        from apps.teams.serializers import TeamMembershipSerializer
        
        # Get all memberships for the user
        memberships = TeamMembership.objects.filter(
            user=request.user,
            status='active'
        ).select_related('team', 'team__captain', 'team__game').order_by('-joined_at')
        
        serializer = TeamMembershipSerializer(memberships, many=True)
        return Response({'results': serializer.data})
    
    @action(detail=False, methods=['get'], url_path='user/(?P<username>[^/.]+)')
    def user_teams(self, request, username=None):
        """
        Get all teams where a specific user is a member (including as captain).
        
        GET /api/teams/user/{username}/
        
        Returns team memberships with team details and user's role.
        Public access.
        """
        from apps.users.models import User
        from apps.teams.models import TeamMembership
        from apps.teams.serializers import TeamMembershipSerializer
        
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all memberships for the user
        memberships = TeamMembership.objects.filter(
            user=user,
            status='active'
        ).select_related('team', 'team__captain', 'team__game').order_by('-joined_at')
        
        serializer = TeamMembershipSerializer(memberships, many=True)
        return Response({'results': serializer.data})
    
    def get_object(self):
        """
        Get team object by ID or slug.
        
        Supports both /api/teams/{id}/ and /api/teams/{slug}/ patterns.
        """
        lookup_value = self.kwargs.get(self.lookup_field)
        
        # Try to get by ID first
        if lookup_value.isdigit():
            team = get_team_by_id(int(lookup_value))
        else:
            # Try to get by slug
            team = get_team_by_slug(lookup_value)
        
        if not team:
            from rest_framework.exceptions import NotFound
            raise NotFound('Team not found.')
        
        # Check object permissions
        self.check_object_permissions(self.request, team)
        
        return team
    
    def create(self, request, *args, **kwargs):
        """
        Create a new team.
        
        POST /api/teams/
        
        Requires authentication. Creator becomes captain automatically.
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                # Serializer handles team creation via service
                team = serializer.save()
                
                # Return created team data
                response_serializer = TeamSerializer(team)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
            except ValidationError as e:
                # Handle validation errors from service
                if hasattr(e, 'message_dict'):
                    return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        """
        List teams with pagination.
        
        GET /api/teams/
        
        Returns 20 teams per page. Public access.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Order by created_at descending
        queryset = queryset.order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve team by ID or slug.
        
        GET /api/teams/{id}/ or GET /api/teams/{slug}/
        
        Public access.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """
        Update team information.
        
        PATCH /api/teams/{id}/
        
        Only captain can update. Requires IsCaptain permission.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            try:
                # Use service to update team
                updated_team = update_team(
                    team=instance,
                    user=request.user,
                    **serializer.validated_data
                )
                
                # Return updated data
                response_serializer = TeamSerializer(updated_team)
                return Response(response_serializer.data)
            
            except PermissionDenied as e:
                return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
            
            except ValidationError as e:
                # Handle validation errors from service
                if hasattr(e, 'message_dict'):
                    return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete team.
        
        DELETE /api/teams/{id}/
        
        Only captain can delete. Requires IsCaptain permission.
        """
        instance = self.get_object()
        
        try:
            # Use service to delete team
            delete_team(team=instance, user=request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], permission_classes=[])
    def stats(self, request, pk=None):
        """
        Get team statistics.
        
        GET /api/teams/{id}/stats/
        
        Returns aggregated statistics including tournaments played, wins, losses, win rate.
        Public access.
        """
        team = self.get_object()
        
        # Use selector to get stats
        stats_data = get_team_stats(team)
        
        return Response(stats_data)
