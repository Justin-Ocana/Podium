"""
Custom permissions for tournaments app.
"""
from rest_framework import permissions
from apps.tournaments.selectors import is_tournament_organizer


class IsOrganizer(permissions.BasePermission):
    """Permission to only allow tournament organizers to perform actions."""
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return is_tournament_organizer(request.user, obj)


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """Read access to anyone, write access only to organizer."""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user or not request.user.is_authenticated:
            return False
        
        return is_tournament_organizer(request.user, obj)
