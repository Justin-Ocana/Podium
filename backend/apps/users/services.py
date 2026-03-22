"""
Business logic for users app.

This module contains functions for write operations and complex business logic.
For read-only queries, see selectors.py
"""
import os
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


@transaction.atomic
def register_user(username, email, password):
    """
    Register a new user and create authentication token.
    
    Args:
        username (str): Username for the new user
        email (str): Email address for the new user
        password (str): Password for the new user
        
    Returns:
        tuple: (user, token) - Created user instance and auth token
        
    Raises:
        ValidationError: If validation fails
    """
    # Normalize email
    email = email.lower().strip()
    
    # Create user (password will be hashed by manager)
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    # Create authentication token
    token, created = Token.objects.get_or_create(user=user)
    
    return user, token


def change_password(user, current_password, new_password):
    """
    Change user password after validating current password.
    
    Args:
        user (User): User instance
        current_password (str): Current password for verification
        new_password (str): New password to set
        
    Returns:
        bool: True if password was changed successfully
        
    Raises:
        ValueError: If current password is incorrect
    """
    # Verify current password
    if not user.check_password(current_password):
        raise ValueError('Current password is incorrect.')
    
    # Verify new password is different
    if current_password == new_password:
        raise ValueError('New password must be different from current password.')
    
    # Set new password (will be hashed automatically)
    user.set_password(new_password)
    user.save(update_fields=['password'])
    
    return True


@transaction.atomic
def update_user_profile(user, **fields):
    """
    Update user profile fields.
    
    Handles special cases like avatar upload and email normalization.
    
    Args:
        user (User): User instance to update
        **fields: Fields to update
        
    Returns:
        User: Updated user instance
    """
    # Normalize email if provided
    if 'email' in fields:
        fields['email'] = fields['email'].lower().strip()
    
    # Handle avatar upload
    if 'avatar' in fields and fields['avatar']:
        # Delete old avatar if exists
        if user.avatar:
            delete_old_avatar(user)
        user.avatar = fields.pop('avatar')
    
    # Update other fields
    for field, value in fields.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    user.save()
    return user


def delete_old_avatar(user):
    """
    Delete old avatar file when uploading a new one.
    
    Args:
        user (User): User instance
    """
    if user.avatar:
        # Get the file path
        avatar_path = user.avatar.path
        
        # Delete the file if it exists
        if os.path.isfile(avatar_path):
            try:
                os.remove(avatar_path)
            except Exception as e:
                # Log error but don't fail the operation
                print(f"Error deleting old avatar: {e}")


def deactivate_user(user):
    """
    Deactivate user account (soft delete).
    
    Args:
        user (User): User instance to deactivate
        
    Returns:
        User: Deactivated user instance
    """
    user.is_active = False
    user.save(update_fields=['is_active'])
    return user


def activate_user(user):
    """
    Activate user account.
    
    Args:
        user (User): User instance to activate
        
    Returns:
        User: Activated user instance
    """
    user.is_active = True
    user.save(update_fields=['is_active'])
    return user
