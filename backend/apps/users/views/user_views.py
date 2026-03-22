"""
User management views.

Handles user profile viewing and editing.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination

from apps.users.models import User
from apps.users.serializers import UserSerializer, UserDetailSerializer
from apps.users.permissions import IsOwnerOrReadOnly
from apps.users.services import update_user_profile
from apps.users.selectors import search_users


class UserPagination(PageNumberPagination):
    """
    Pagination class for user listings.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user CRUD operations.
    
    Endpoints:
    - GET /api/users/ - List users
    - GET /api/users/{id}/ - Retrieve user
    - PATCH /api/users/{id}/ - Update user
    - GET /api/users/me/ - Get current user
    - PATCH /api/users/me/ - Update current user
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    pagination_class = UserPagination
    permission_classes = [IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve' or self.action == 'me':
            return UserDetailSerializer
        return UserSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on query parameters.
        
        Supports search by username.
        """
        queryset = super().get_queryset()
        
        # Search filter
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = search_users(search_query, active_only=True)
        
        return queryset.order_by('-created_at')
    
    def update(self, request, *args, **kwargs):
        """
        Update user profile.
        
        Only the owner can update their profile.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Check permission
        if instance != request.user:
            return Response({
                'error': 'You can only update your own profile'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            # Use service to update profile
            updated_user = update_user_profile(instance, **serializer.validated_data)
            
            # Return updated data
            response_serializer = UserDetailSerializer(updated_user)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Disable DELETE - users should be deactivated instead."""
        return Response({
            'error': 'User deletion is not allowed. Please contact support to deactivate your account.'
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated], url_path='me')
    def me(self, request):
        """
        Get or update current user profile.
        
        GET /api/users/me/ - Get current user
        PATCH /api/users/me/ - Update current user
        """
        if request.method == 'GET':
            serializer = UserDetailSerializer(request.user)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = UserSerializer(request.user, data=request.data, partial=True)
            
            if serializer.is_valid():
                # Use service to update profile
                updated_user = update_user_profile(request.user, **serializer.validated_data)
                
                # Return updated data
                response_serializer = UserDetailSerializer(updated_user)
                return Response(response_serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path=r'username/(?P<username>[^/.]+)')
    def by_username(self, request, username=None):
        """
        Get user profile by username (public endpoint).
        
        GET /api/users/username/{username}/ - Get user by username
        """
        try:
            user = User.objects.get(username=username, is_active=True)
            serializer = UserDetailSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
