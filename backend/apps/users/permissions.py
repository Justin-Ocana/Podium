"""
Custom permissions for users app.
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow owners of an object to edit it.
    
    Read permissions are allowed to any request.
    Write permissions are only allowed to the owner of the object.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to access the object.
        
        Args:
            request: HTTP request
            view: View being accessed
            obj: Object being accessed (User instance)
            
        Returns:
            bool: True if permission granted, False otherwise
        """
        # Read permissions are allowed to any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj == request.user


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Permission to allow read access to anyone, but write access only to authenticated users.
    """
    
    def has_permission(self, request, view):
        """
        Check if user has permission to access the view.
        
        Args:
            request: HTTP request
            view: View being accessed
            
        Returns:
            bool: True if permission granted, False otherwise
        """
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions require authentication
        return request.user and request.user.is_authenticated
