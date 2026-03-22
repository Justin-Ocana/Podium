"""
Friends views.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.users.models import User
from .models import FriendRequest, Friendship
from .serializers import (
    FriendRequestSerializer,
    FriendshipSerializer,
    SendFriendRequestSerializer
)
from . import services


class FriendViewSet(viewsets.ViewSet):
    """
    ViewSet for managing friends and friend requests.
    
    Endpoints:
    - GET /api/friends/ - List all friends
    - GET /api/friends/requests/ - List pending friend requests
    - GET /api/friends/sent_requests/ - List sent friend requests
    - POST /api/friends/send_request/ - Send a friend request
    - POST /api/friends/accept_request/ - Accept a friend request
    - POST /api/friends/decline_request/ - Decline a friend request
    - DELETE /api/friends/cancel_request/{id}/ - Cancel a sent friend request
    - DELETE /api/friends/remove/{username}/ - Remove a friend
    """
    
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """List all friends of the authenticated user."""
        friends = services.get_friends(request.user)
        
        # Serialize friends with presence status
        from apps.users.serializers.user_serializers import UserSerializer
        serializer = UserSerializer(friends, many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def requests(self, request):
        """List all pending friend requests received by the authenticated user."""
        requests = services.get_pending_requests(request.user)
        serializer = FriendRequestSerializer(requests, many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sent_requests(self, request):
        """List all pending friend requests sent by the authenticated user."""
        requests = services.get_sent_requests(request.user)
        serializer = FriendRequestSerializer(requests, many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def send_request(self, request):
        """Send a friend request to another user."""
        serializer = SendFriendRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        to_username = serializer.validated_data['to_username']
        to_user = get_object_or_404(User, username=to_username)
        
        try:
            friend_request = services.send_friend_request(
                from_user=request.user,
                to_user=to_user
            )
            
            response_serializer = FriendRequestSerializer(friend_request)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        except ValueError as e:
            # Log the specific error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Friend request failed from {request.user.username} to {to_username}: {str(e)}")
            
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Log unexpected errors
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error in send_request: {e}", exc_info=True)
            
            return Response(
                {'error': 'An unexpected error occurred. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def accept_request(self, request):
        """Accept a friend request."""
        request_id = request.data.get('request_id')
        
        if not request_id:
            return Response(
                {'error': 'request_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            friendship = services.accept_friend_request(
                request_id=request_id,
                user=request.user
            )
            
            serializer = FriendshipSerializer(friendship)
            return Response(serializer.data)
        
        except FriendRequest.DoesNotExist:
            return Response(
                {'error': 'Friend request not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def decline_request(self, request):
        """Decline a friend request."""
        request_id = request.data.get('request_id')
        
        if not request_id:
            return Response(
                {'error': 'request_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            services.decline_friend_request(
                request_id=request_id,
                user=request.user
            )
            
            return Response(
                {'message': 'Friend request declined'},
                status=status.HTTP_200_OK
            )
        
        except FriendRequest.DoesNotExist:
            return Response(
                {'error': 'Friend request not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['delete'])
    def cancel_request(self, request, pk=None):
        """Cancel a sent friend request."""
        try:
            services.cancel_friend_request(
                request_id=pk,
                user=request.user
            )
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except FriendRequest.DoesNotExist:
            return Response(
                {'error': 'Friend request not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['delete'])
    def remove(self, request, pk=None):
        """Remove a friend."""
        friend = get_object_or_404(User, username=pk)
        
        try:
            services.remove_friend(
                user=request.user,
                friend=friend
            )
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
