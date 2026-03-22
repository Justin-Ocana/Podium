from django.core.exceptions import ValidationError
import re


def validate_team_name(value):
    """
    Validate team name format.
    
    Rules:
    - Length between 3 and 50 characters
    - Cannot be only whitespace
    
    Args:
        value (str): Team name to validate
        
    Raises:
        ValidationError: If team name doesn't meet requirements
    """
    if not value:
        raise ValidationError('Team name is required.')
    
    # Check if only whitespace
    if not value.strip():
        raise ValidationError('Team name cannot be only whitespace.')
    
    # Check length
    if len(value.strip()) < 3:
        raise ValidationError('Team name must be at least 3 characters long.')
    if len(value) > 50:
        raise ValidationError('Team name cannot exceed 50 characters.')


def validate_team_tag(value):
    """
    Validate team tag format.
    
    Rules:
    - Length between 2 and 5 characters
    - Only letters and numbers
    - Cannot be only whitespace
    
    Args:
        value (str): Team tag to validate
        
    Raises:
        ValidationError: If team tag doesn't meet requirements
    """
    if not value:
        raise ValidationError('Team tag is required.')
    
    # Check if only whitespace
    if not value.strip():
        raise ValidationError('Team tag cannot be only whitespace.')
    
    # Check length
    if len(value.strip()) < 2:
        raise ValidationError('Team tag must be at least 2 characters long.')
    if len(value) > 5:
        raise ValidationError('Team tag cannot exceed 5 characters.')
    
    # Check format (only letters and numbers)
    if not re.match(r'^[A-Za-z0-9]+$', value.strip()):
        raise ValidationError('Team tag can only contain letters and numbers.')


def validate_team_description(value):
    """
    Validate team description text length.
    
    Rules:
    - Maximum 1000 characters
    
    Args:
        value (str): Team description to validate
        
    Raises:
        ValidationError: If description exceeds maximum length
    """
    if value and len(value) > 1000:
        raise ValidationError(
            f'Team description cannot exceed 1000 characters. Current length: {len(value)}'
        )


def validate_hex_color(value):
    """
    Validate hex color format.
    
    Rules:
    - Must be in format #RRGGBB
    
    Args:
        value (str): Hex color to validate
        
    Raises:
        ValidationError: If color format is invalid
    """
    if not value:
        return
    
    if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
        raise ValidationError('Color must be in hex format (e.g., #ff4655).')


def validate_url(value):
    """
    Validate URL format.
    
    Args:
        value (str): URL to validate
        
    Raises:
        ValidationError: If URL format is invalid
    """
    if not value:
        return
    
    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(value):
        raise ValidationError('Invalid URL format.')


def validate_join_request_message(value):
    """
    Validate join request message length.
    
    Rules:
    - Maximum 500 characters
    
    Args:
        value (str): Message to validate
        
    Raises:
        ValidationError: If message exceeds maximum length
    """
    if value and len(value) > 500:
        raise ValidationError(
            f'Message cannot exceed 500 characters. Current length: {len(value)}'
        )
