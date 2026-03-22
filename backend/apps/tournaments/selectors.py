"""
Read-only queries for tournaments app.
"""
from django.db.models import Q, Count
from django.utils import timezone
from apps.tournaments.models import Tournament


def get_tournament_by_id(tournament_id):
    """Get tournament by ID."""
    try:
        return Tournament.objects.select_related('organizer').get(id=tournament_id)
    except Tournament.DoesNotExist:
        return None


def get_tournament_by_slug(slug):
    """Get tournament by slug."""
    try:
        return Tournament.objects.select_related('organizer').get(slug=slug)
    except Tournament.DoesNotExist:
        return None


def search_tournaments(query=None, status=None, game=None, page=1, page_size=20):
    """
    Search tournaments with filters and pagination.
    
    Args:
        query (str, optional): Search term for tournament name
        status (str, optional): Filter by status
        game (str, optional): Filter by game
        page (int): Page number
        page_size (int): Results per page
        
    Returns:
        dict: Paginated results
    """
    queryset = Tournament.objects.select_related('organizer')
    
    # Apply filters
    if query:
        queryset = queryset.filter(name__icontains=query)
    
    if status:
        queryset = queryset.filter(status=status)
    
    if game:
        queryset = queryset.filter(game__icontains=game)
    
    # Order by start date
    queryset = queryset.order_by('-start_date')
    
    # Get total count
    total_count = queryset.count()
    
    # Calculate pagination
    num_pages = (total_count + page_size - 1) // page_size
    page = max(1, min(page, num_pages if num_pages > 0 else 1))
    
    # Apply pagination
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    results = queryset[start_index:end_index]
    
    return {
        'results': results,
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'num_pages': num_pages,
    }


def get_user_tournaments(user):
    """Get tournaments organized by user."""
    return Tournament.objects.filter(
        organizer=user
    ).order_by('-created_at')


def is_tournament_organizer(user, tournament):
    """Check if user is the organizer of the tournament."""
    return tournament.organizer == user


def get_upcoming_tournaments(limit=10):
    """Get upcoming tournaments (open or closed status)."""
    return Tournament.objects.filter(
        status__in=['open', 'closed'],
        start_date__gte=timezone.now()
    ).select_related('organizer').order_by('start_date')[:limit]


def get_active_tournaments(limit=10):
    """Get currently active tournaments (in_progress status)."""
    return Tournament.objects.filter(
        status='in_progress'
    ).select_related('organizer').order_by('-start_date')[:limit]
