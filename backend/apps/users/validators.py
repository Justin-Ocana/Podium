import re
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions


def validate_username(value):
    """
    Validate username format.
    
    Rules:
    - Only alphanumeric characters and underscores
    - Length between 3 and 30 characters
    - Cannot start with a number
    - Cannot contain spaces
    
    Args:
        value (str): Username to validate
        
    Raises:
        ValidationError: If username doesn't meet requirements
    """
    if not value:
        raise ValidationError('Username is required.')
    
    # Check length
    if len(value) < 3:
        raise ValidationError('Username must be at least 3 characters long.')
    if len(value) > 30:
        raise ValidationError('Username cannot exceed 30 characters.')
    
    # Check for spaces
    if ' ' in value:
        raise ValidationError('Username cannot contain spaces.')
    
    # Check if starts with number
    if value[0].isdigit():
        raise ValidationError('Username cannot start with a number.')
    
    # Check for valid characters (alphanumeric and underscore only)
    if not re.match(r'^[a-zA-Z0-9_]+$', value):
        raise ValidationError(
            'Username can only contain letters, numbers, and underscores.'
        )


def validate_avatar_file(file):
    """
    Validate avatar file format and size.
    
    Rules:
    - Format must be JPEG, PNG, or WebP
    - File size must not exceed 5MB
    
    Args:
        file: Uploaded file object
        
    Raises:
        ValidationError: If file doesn't meet requirements
    """
    if not file:
        return
    
    # Check file size (5MB = 5 * 1024 * 1024 bytes)
    max_size = 5 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError(
            f'Avatar file size cannot exceed 5MB. Current size: {file.size / (1024 * 1024):.2f}MB'
        )
    
    # Check file format
    valid_extensions = ['jpg', 'jpeg', 'png', 'webp']
    file_extension = file.name.split('.')[-1].lower()
    
    if file_extension not in valid_extensions:
        raise ValidationError(
            f'Invalid file format. Allowed formats: {", ".join(valid_extensions).upper()}'
        )
    
    # Verify it's actually an image
    try:
        get_image_dimensions(file)
    except Exception:
        raise ValidationError('Uploaded file is not a valid image.')


def validate_bio(value):
    """
    Validate bio text length.
    
    Rules:
    - Maximum 500 characters
    
    Args:
        value (str): Bio text to validate
        
    Raises:
        ValidationError: If bio exceeds maximum length
    """
    if value and len(value) > 500:
        raise ValidationError(
            f'Bio cannot exceed 500 characters. Current length: {len(value)}'
        )
