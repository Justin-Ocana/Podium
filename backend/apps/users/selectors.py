"""
Read-only queries for users app.

This module contains functions for fetching and filtering user data.
For write operations and business logic, see services.py
"""
from django.contrib.auth import get_user_model
from django.db.models import Q, Count

User = get_user_model()


def get_user_by_id(user_id):
    """
    Get user by ID.
    
    Args:
        user_id (int): User ID
        
    Returns:
        User or None: User instance if found, None otherwise
    """
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


def get_user_by_username(username, case_sensitive=False):
    """
    Get user by username.
    
    Args:
        username (str): Username to search for
        case_sensitive (bool): Whether to perform case-sensitive search
        
    Returns:
        User or None: User instance if found, None otherwise
    """
    try:
        if case_sensitive:
            return User.objects.get(username=username)
        else:
            return User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        return None


def get_user_by_email(email):
    """
    Get user by email (case-insensitive).
    
    Args:
        email (str): Email to search for
        
    Returns:
        User or None: User instance if found, None otherwise
    """
    try:
        return User.objects.get(email__iexact=email.lower())
    except User.DoesNotExist:
        return None


def search_users(query, active_only=True):
    """
    Search users by username or email.
    
    Args:
        query (str): Search term
        active_only (bool): Whether to return only active users
        
    Returns:
        QuerySet: Users matching the search query
    """
    queryset = User.objects.all()
    
    if active_only:
        queryset = queryset.filter(is_active=True)
    
    if query:
        queryset = queryset.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )
    
    return queryset.order_by('username')


def get_active_users():
    """
    Get all active users.
    
    Returns:
        QuerySet: Active users
    """
    return User.objects.filter(is_active=True).order_by('-created_at')


def get_user_stats(user):
    """
    Get statistics for a user.
    
    Aggregates data from related models (teams, tournaments, matches).
    
    Args:
        user (User): User instance
        
    Returns:
        dict: Statistics data
    """
    stats = {
        'teams_count': 0,
        'tournaments_played_count': 0,
        'tournaments_organized_count': 0,
        'matches_won_count': 0,
        'matches_lost_count': 0,
        'matches_total_count': 0,
        'winrate': 0.0,
    }
    
    # Get teams count using reverse relationship
    # Note: This assumes teams app has a relationship to User
    try:
        if hasattr(user, 'teams'):
            stats['teams_count'] = user.teams.count()
    except:
        pass
    
    # Get tournaments organized count
    try:
        if hasattr(user, 'organized_tournaments'):
            stats['tournaments_organized_count'] = user.organized_tournaments.count()
    except:
        pass
    
    # Get tournaments played count
    # This would require checking team memberships and their tournament participations
    try:
        if hasattr(user, 'teams'):
            # Count unique tournaments where user's teams participated
            tournaments_played = set()
            for team in user.teams.all():
                if hasattr(team, 'tournament_registrations'):
                    for registration in team.tournament_registrations.filter(status='approved'):
                        tournaments_played.add(registration.tournament_id)
            stats['tournaments_played_count'] = len(tournaments_played)
    except:
        pass
    
    # Get matches statistics
    # This would require checking matches where user's teams participated
    try:
        # Placeholder for when matches app is implemented
        # matches_won = Match.objects.filter(winner_team__members=user).count()
        # matches_lost = Match.objects.filter(loser_team__members=user).count()
        pass
    except:
        pass
    
    # Calculate totals
    stats['matches_total_count'] = stats['matches_won_count'] + stats['matches_lost_count']
    
    # Calculate winrate
    if stats['matches_total_count'] > 0:
        stats['winrate'] = round(
            (stats['matches_won_count'] / stats['matches_total_count']) * 100,
            2
        )
    
    return stats


def get_users_by_ids(user_ids):
    """
    Get multiple users by their IDs.
    
    Args:
        user_ids (list): List of user IDs
        
    Returns:
        QuerySet: Users with the given IDs
    """
    return User.objects.filter(id__in=user_ids)


def user_exists(username=None, email=None):
    """
    Check if a user exists by username or email.
    
    Args:
        username (str, optional): Username to check
        email (str, optional): Email to check
        
    Returns:
        bool: True if user exists, False otherwise
    """
    if username:
        if User.objects.filter(username__iexact=username).exists():
            return True
    
    if email:
        if User.objects.filter(email__iexact=email.lower()).exists():
            return True
    
    return False
