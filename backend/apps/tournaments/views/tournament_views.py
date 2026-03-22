"""
Tournament management views.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import ValidationError, PermissionDenied

from apps.tournaments.models import Tournament
from apps.tournaments.serializers import (
    TournamentCreateSerializer,
    TournamentSerializer,
    TournamentUpdateSerializer,
    TournamentListSerializer
)
from apps.tournaments.permissions import IsOrganizer
from apps.tournaments.services import (
    create_tournament,
    update_tournament,
    delete_tournament,
    open_tournament,
    close_tournament,
    start_tournament,
    cancel_tournament,
    finish_tournament
)
from apps.tournaments.selectors import (
    get_tournament_by_id,
    get_tournament_by_slug
)


class TournamentPagination(PageNumberPagination):
    """Pagination class for tournament listings."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class TournamentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for tournament CRUD operations.
    
    Endpoints:
    - POST /api/tournaments/ - Create tournament (authenticated)
    - GET /api/tournaments/ - List tournaments with pagination
    - GET /api/tournaments/{id}/ - Retrieve tournament by ID
    - GET /api/tournaments/{slug}/ - Retrieve tournament by slug (public)
    - PATCH /api/tournaments/{id}/ - Update tournament (organizer only)
    - DELETE /api/tournaments/{id}/ - Delete tournament (organizer only)
    - POST /api/tournaments/{id}/open/ - Open registrations
    - POST /api/tournaments/{id}/close/ - Close registrations
    - POST /api/tournaments/{id}/start/ - Start tournament
    - POST /api/tournaments/{id}/cancel/ - Cancel tournament
    - POST /api/tournaments/{id}/finish/ - Finish tournament
    """
    queryset = Tournament.objects.select_related('organizer').all()
    serializer_class = TournamentSerializer
    pagination_class = TournamentPagination
    lookup_field = 'pk'
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy', 'open', 'close', 'start', 'cancel', 'finish']:
            return [IsAuthenticated(), IsOrganizer()]
        return []
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return TournamentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TournamentUpdateSerializer
        elif self.action == 'list':
            return TournamentListSerializer
        return TournamentSerializer
    
    def get_object(self):
        """Get tournament object by ID or slug."""
        lookup_value = self.kwargs.get(self.lookup_field)
        
        # Try to get by ID first
        if lookup_value.isdigit():
            tournament = get_tournament_by_id(int(lookup_value))
        else:
            # Try to get by slug
            tournament = get_tournament_by_slug(lookup_value)
        
        if not tournament:
            from rest_framework.exceptions import NotFound
            raise NotFound('Tournament not found.')
        
        # Check object permissions
        self.check_object_permissions(self.request, tournament)
        
        return tournament
    
    def create(self, request, *args, **kwargs):
        """Create a new tournament."""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            try:
                tournament = create_tournament(
                    organizer=request.user,
                    **serializer.validated_data
                )
                
                response_serializer = TournamentSerializer(tournament)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
            except ValidationError as e:
                if hasattr(e, 'message_dict'):
                    return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        """List tournaments with pagination."""
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.order_by('-start_date')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve tournament by ID or slug."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update tournament information."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            try:
                updated_tournament = update_tournament(
                    tournament=instance,
                    user=request.user,
                    **serializer.validated_data
                )
                
                response_serializer = TournamentSerializer(updated_tournament)
                return Response(response_serializer.data)
            
            except PermissionDenied as e:
                return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
            
            except ValidationError as e:
                if hasattr(e, 'message_dict'):
                    return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete tournament."""
        instance = self.get_object()
        
        try:
            delete_tournament(tournament=instance, user=request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOrganizer])
    def open(self, request, pk=None):
        """Open tournament for registrations."""
        tournament = self.get_object()
        
        try:
            updated_tournament = open_tournament(tournament, request.user)
            serializer = TournamentSerializer(updated_tournament)
            return Response(serializer.data)
        
        except (PermissionDenied, ValidationError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOrganizer])
    def close(self, request, pk=None):
        """Close tournament registrations."""
        tournament = self.get_object()
        
        try:
            updated_tournament = close_tournament(tournament, request.user)
            serializer = TournamentSerializer(updated_tournament)
            return Response(serializer.data)
        
        except (PermissionDenied, ValidationError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOrganizer])
    def start(self, request, pk=None):
        """Start tournament."""
        tournament = self.get_object()
        
        try:
            updated_tournament = start_tournament(tournament, request.user)
            serializer = TournamentSerializer(updated_tournament)
            return Response(serializer.data)
        
        except (PermissionDenied, ValidationError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOrganizer])
    def cancel(self, request, pk=None):
        """Cancel tournament."""
        tournament = self.get_object()
        
        try:
            updated_tournament = cancel_tournament(tournament, request.user)
            serializer = TournamentSerializer(updated_tournament)
            return Response(serializer.data)
        
        except (PermissionDenied, ValidationError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOrganizer])
    def finish(self, request, pk=None):
        """Finish tournament."""
        tournament = self.get_object()
        
        try:
            updated_tournament = finish_tournament(tournament, request.user)
            serializer = TournamentSerializer(updated_tournament)
            return Response(serializer.data)
        
        except (PermissionDenied, ValidationError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
