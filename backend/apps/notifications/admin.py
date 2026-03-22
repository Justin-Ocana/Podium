from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model."""
    
    list_display = [
        'id',
        'recipient',
        'actor',
        'type',
        'is_read',
        'created_at',
    ]
    
    list_filter = [
        'type',
        'is_read',
        'created_at',
    ]
    
    search_fields = [
        'recipient__username',
        'actor__username',
        'message',
    ]
    
    readonly_fields = [
        'created_at',
        'read_at',
    ]
    
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        """Notifications should be created programmatically."""
        return False

