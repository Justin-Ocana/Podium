from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for custom User model.
    """
    list_display = ['username', 'email', 'avatar_preview', 'created_at', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    # Fieldsets for detail view
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('avatar', 'bio', 'created_at', 'updated_at')
        }),
    )
    
    # Read-only fields
    readonly_fields = ['created_at', 'updated_at', 'date_joined', 'last_login']
    
    # Fields for add user form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'avatar', 'bio')
        }),
    )
    
    def avatar_preview(self, obj):
        """Display avatar thumbnail in list view."""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="30" height="30" style="border-radius: 50%;" />',
                obj.get_avatar_url()
            )
        return '-'
    
    avatar_preview.short_description = 'Avatar'

