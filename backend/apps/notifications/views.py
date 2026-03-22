"""
Notification views.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import PageNumberPagination

from .models import Notification
from .serializers import NotificationSerializer, NotificationListSerializer
from .services import get_user_notifications, get_unread_count, mark_all_as_read


class NotificationPagination(PageNumberPagination):
    """Pagination for notifications."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationViewSet(ReadOnlyModelViewSet):
    """
    ViewSet for viewing and managing notifications.
    
    list: Get all notifications for the authenticated user
    retrieve: Get a specific notification
    mark_as_read: Mark a notification as read
    mark_all_as_read: Mark all notifications as read
    unread_count: Get count of unread notifications
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationListSerializer
    pagination_class = NotificationPagination
    
    def get_queryset(self):
        """Get notifications for the authenticated user."""
        user = self.request.user
        queryset = get_user_notifications(user)
        
        # Filter by read status if requested
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
            queryset = queryset.filter(is_read=is_read_bool)
        
        return queryset
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action."""
        if self.action == 'retrieve':
            return NotificationSerializer
        return NotificationListSerializer
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Mark a specific notification as read.
        
        POST /api/notifications/{id}/mark_as_read/
        """
        try:
            notification = Notification.objects.get(
                id=pk,
                recipient=request.user
            )
            notification.mark_as_read()
            
            serializer = self.get_serializer(notification)
            return Response(serializer.data)
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notification not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def mark_as_unread(self, request, pk=None):
        """
        Mark a specific notification as unread.
        
        POST /api/notifications/{id}/mark_as_unread/
        """
        try:
            notification = Notification.objects.get(
                id=pk,
                recipient=request.user
            )
            notification.mark_as_unread()
            
            serializer = self.get_serializer(notification)
            return Response(serializer.data)
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notification not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Mark all notifications as read for the authenticated user.
        
        POST /api/notifications/mark_all_as_read/
        """
        count = mark_all_as_read(request.user)
        return Response({
            'message': f'{count} notifications marked as read',
            'count': count
        })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Get count of unread notifications.
        
        GET /api/notifications/unread_count/
        """
        count = get_unread_count(request.user)
        return Response({'count': count})
    
    def destroy(self, request, pk=None):
        """
        Delete a notification.
        
        DELETE /api/notifications/{id}/
        """
        try:
            notification = Notification.objects.get(
                id=pk,
                recipient=request.user
            )
            notification.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notification not found'},
                status=status.HTTP_404_NOT_FOUND
            )
