"""
Custom permissions for teams app.
"""
from rest_framework import permissions
from apps.teams.selectors import is_team_captain


class IsCaptain(permissions.BasePermission):
    """
    Permission to only allow team captains to perform actions.
    
    Checks if the authenticated user is the captain of the team.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is the captain of the team.
        
        Args:
            request: HTTP request
            view: View being accessed
            obj: Object being accessed (Team instance)
            
        Returns:
            bool: True if user is captain, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is the captain of the team
        return is_team_captain(request.user, obj)


class IsCaptainOrReadOnly(permissions.BasePermission):
    """
    Permission to allow read access to anyone, but write access only to team captain.
    
    Read permissions are allowed to any request.
    Write permissions are only allowed to the team captain.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to access the object.
        
        Args:
            request: HTTP request
            view: View being accessed
            obj: Object being accessed (Team instance)
            
        Returns:
            bool: True if permission granted, False otherwise
        """
        # Read permissions are allowed to any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # User must be authenticated for write operations
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Write permissions are only allowed to the captain
        return is_team_captain(request.user, obj)


class IsTeamMember(permissions.BasePermission):
    """
    Permission to only allow active team members to access resources.
    
    Checks if the authenticated user has an active membership in the team.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is an active member of the team.
        
        Args:
            request: HTTP request
            view: View being accessed
            obj: Object being accessed (Team instance)
            
        Returns:
            bool: True if user is active member, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has active membership in the team
        from apps.teams.models import TeamMembership
        return TeamMembership.objects.filter(
            user=request.user,
            team=obj,
            status='active'
        ).exists()
