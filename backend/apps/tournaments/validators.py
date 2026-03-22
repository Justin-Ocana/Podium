from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.utils import timezone


def validate_tournament_name(value):
    """
    Validate tournament name format.
    
    Rules:
    - Length between 3 and 100 characters
    - Cannot be only whitespace
    
    Args:
        value (str): Tournament name to validate
        
    Raises:
        ValidationError: If tournament name doesn't meet requirements
    """
    if not value:
        raise ValidationError('Tournament name is required.')
    
    if not value.strip():
        raise ValidationError('Tournament name cannot be only whitespace.')
    
    if len(value.strip()) < 3:
        raise ValidationError('Tournament name must be at least 3 characters long.')
    if len(value) > 100:
        raise ValidationError('Tournament name cannot exceed 100 characters.')


def validate_tournament_banner(file):
    """
    Validate tournament banner file format and size.
    
    Rules:
    - Format must be JPEG, PNG, or WebP
    - File size must not exceed 10MB
    
    Args:
        file: Uploaded file object
        
    Raises:
        ValidationError: If file doesn't meet requirements
    """
    if not file:
        return
    
    # Check file size (10MB = 10 * 1024 * 1024 bytes)
    max_size = 10 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError(
            f'Tournament banner file size cannot exceed 10MB. Current size: {file.size / (1024 * 1024):.2f}MB'
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


def validate_tournament_description(value):
    """
    Validate tournament description text length.
    
    Rules:
    - Maximum 2000 characters
    
    Args:
        value (str): Tournament description to validate
        
    Raises:
        ValidationError: If description exceeds maximum length
    """
    if value and len(value) > 2000:
        raise ValidationError(
            f'Tournament description cannot exceed 2000 characters. Current length: {len(value)}'
        )


def validate_tournament_dates(registration_start, registration_end, start_date):
    """
    Validate tournament date logic.
    
    Rules:
    - registration_start must be in the future
    - registration_end must be after registration_start
    - start_date must be after registration_end
    
    Args:
        registration_start (datetime): When registration opens
        registration_end (datetime): When registration closes
        start_date (datetime): When tournament starts
        
    Raises:
        ValidationError: If dates don't follow logical order
    """
    now = timezone.now()
    
    if registration_start < now:
        raise ValidationError({
            'registration_start': 'Registration start date must be in the future.'
        })
    
    if registration_end <= registration_start:
        raise ValidationError({
            'registration_end': 'Registration end date must be after registration start date.'
        })
    
    if start_date <= registration_end:
        raise ValidationError({
            'start_date': 'Tournament start date must be after registration end date.'
        })


def validate_max_participants(value):
    """
    Validate maximum participants value.
    
    Rules:
    - Must be a power of 2 for elimination brackets (2, 4, 8, 16, 32, 64, 128, 256)
    - Minimum 2 participants
    
    Args:
        value (int): Maximum participants
        
    Raises:
        ValidationError: If value is invalid
    """
    if value < 2:
        raise ValidationError('Tournament must allow at least 2 participants.')
    
    # Check if power of 2
    if value & (value - 1) != 0:
        raise ValidationError(
            'Maximum participants must be a power of 2 (2, 4, 8, 16, 32, 64, 128, 256).'
        )
    
    if value > 256:
        raise ValidationError('Maximum participants cannot exceed 256.')
