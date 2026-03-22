from django.contrib.auth.models import BaseUserManager
from django.db.models import Q


class UserManager(BaseUserManager):
    """
    Custom manager for User model.
    
    Provides methods for creating users and superusers with proper
    email normalization and password hashing.
    """
    
    def create_user(self, username, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given username, email and password.
        
        Args:
            username (str): Username for the user
            email (str): Email address for the user
            password (str, optional): Password for the user
            **extra_fields: Additional fields for the user model
            
        Returns:
            User: The created user instance
            
        Raises:
            ValueError: If username or email is not provided
        """
        if not username:
            raise ValueError('The Username field must be set')
        if not email:
            raise ValueError('The Email field must be set')
        
        # Normalize email to lowercase
        email = self.normalize_email(email)
        email = email.lower()
        
        # Create user instance
        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )
        
        # Hash password
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given username, email and password.
        
        Args:
            username (str): Username for the superuser
            email (str): Email address for the superuser
            password (str, optional): Password for the superuser
            **extra_fields: Additional fields for the user model
            
        Returns:
            User: The created superuser instance
        """
        # Set superuser flags
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)
    
    def active_users(self):
        """
        Return queryset of active users only.
        
        Returns:
            QuerySet: Active users
        """
        return self.filter(is_active=True)
    
    def search(self, query):
        """
        Search users by username (case-insensitive).
        
        Args:
            query (str): Search term
            
        Returns:
            QuerySet: Users matching the search query
        """
        if not query:
            return self.none()
        
        return self.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )
    
    def by_username(self, username):
        """
        Get user by username (case-insensitive).
        
        Args:
            username (str): Username to search for
            
        Returns:
            User or None: User instance if found, None otherwise
        """
        try:
            return self.get(username__iexact=username)
        except self.model.DoesNotExist:
            return None
