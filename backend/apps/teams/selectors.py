"""
Read-only queries for teams app.

This module contains functions for fetching and filtering team data.
For write operations and business logic, see services.py
"""
from django.db.models import Q, Count, Case, When, IntegerField, Prefetch
from apps.teams.models import (
    Team, TeamMembership, TeamJoinRequest, TeamInvite,
    TeamGame, TeamStats, TeamSocial, TeamSettings
)


def get_team_by_id(team_id):
    """Get team by ID with related data."""
    try:
        return Team.objects.select_related('captain').prefetch_related(
            'games',
            'social_links',
            'settings',
            'stats'
        ).get(id=team_id)
    except Team.DoesNotExist:
        return None


def get_team_by_slug(slug):
    """Get team by slug with related data."""
    try:
        return Team.objects.select_related('captain').prefetch_related(
            'games',
            'social_links',
            'settings',
            'stats'
        ).get(slug=slug)
    except Team.DoesNotExist:
        return None


def get_team_by_tag(tag):
    """Get team by tag."""
    try:
        return Team.objects.select_related('captain').get(tag__iexact=tag)
    except Team.DoesNotExist:
        return None


def get_team_members(team, status='active'):
    """
    Get team members ordered by role (captain first).
    
    Args:
        team (Team): Team instance
        status (str): Filter by status (default: 'active')
        
    Returns:
        QuerySet: TeamMembership queryset
    """
    return TeamMembership.objects.filter(
        team=team,
        status=status
    ).select_related('user').annotate(
        role_order=Case(
            When(role='captain', then=0),
            When(role='manager', then=1),
            When(role='coach', then=2),
            When(role='player', then=3),
            default=4,
            output_field=IntegerField()
        )
    ).order_by('role_order', 'joined_at')


def get_team_stats(team):
    """
    Get team statistics.
    
    Args:
        team (Team): Team instance
        
    Returns:
        dict: Statistics data
    """
    try:
        stats = team.stats
        return {
            'matches_played': stats.matches_played,
            'matches_won': stats.matches_won,
            'matches_lost': stats.matches_lost,
            'tournaments_played': stats.tournaments_played,
            'tournaments_won': stats.tournaments_won,
            'winrate': float(stats.winrate),
        }
    except TeamStats.DoesNotExist:
        return {
            'matches_played': 0,
            'matches_won': 0,
            'matches_lost': 0,
            'tournaments_played': 0,
            'tournaments_won': 0,
            'winrate': 0.0,
        }


def search_teams(query=None, game=None, country=None, region=None, page=1, page_size=20):
    """
    Search teams with filters and pagination.
    
    Args:
        query (str): Search term for name or tag
        game (str): Filter by game
        country (str): Filter by country
        region (str): Filter by region
        page (int): Page number
        page_size (int): Results per page
        
    Returns:
        dict: Paginated results
    """
    queryset = Team.objects.select_related('captain').annotate(
        member_count=Count('memberships', filter=Q(memberships__status='active'))
    )
    
    # Apply filters
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) | Q(tag__icontains=query)
        )
    
    if game:
        queryset = queryset.filter(games__game=game)
    
    if country:
        queryset = queryset.filter(country__iexact=country)
    
    if region:
        queryset = queryset.filter(region__iexact=region)
    
    # Order by created_at descending
    queryset = queryset.order_by('-created_at')
    
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


def get_user_teams(user, status='active'):
    """
    Get teams where user has membership.
    
    Args:
        user (User): User instance
        status (str): Filter by membership status
        
    Returns:
        QuerySet: Team queryset
    """
    return Team.objects.filter(
        memberships__user=user,
        memberships__status=status
    ).select_related('captain').distinct().order_by('-created_at')


def get_user_team_memberships(user, status='active'):
    """
    Get user's team memberships with team details.
    
    Args:
        user (User): User instance
        status (str): Filter by status
        
    Returns:
        QuerySet: TeamMembership queryset
    """
    return TeamMembership.objects.filter(
        user=user,
        status=status
    ).select_related('team', 'team__captain').order_by('-joined_at')


def is_team_captain(user, team):
    """Check if user is the captain of the team."""
    return TeamMembership.objects.filter(
        user=user,
        team=team,
        role='captain',
        status='active'
    ).exists()


def is_team_manager(user, team):
    """Check if user is a manager of the team."""
    return TeamMembership.objects.filter(
        user=user,
        team=team,
        role='manager',
        status='active'
    ).exists()


def is_team_member(user, team, status='active'):
    """Check if user is a member of the team."""
    return TeamMembership.objects.filter(
        user=user,
        team=team,
        status=status
    ).exists()


def can_manage_team(user, team):
    """Check if user can manage team (captain or manager)."""
    return TeamMembership.objects.filter(
        user=user,
        team=team,
        role__in=['captain', 'manager'],
        status='active'
    ).exists()


# ============================================================================
# JOIN REQUESTS
# ============================================================================

def get_team_join_requests(team, status='pending'):
    """
    Get join requests for a team.
    
    Args:
        team (Team): Team instance
        status (str): Filter by status
        
    Returns:
        QuerySet: TeamJoinRequest queryset
    """
    return TeamJoinRequest.objects.filter(
        team=team,
        status=status
    ).select_related('user').order_by('-created_at')


def get_user_join_requests(user, status='pending'):
    """
    Get user's join requests.
    
    Args:
        user (User): User instance
        status (str): Filter by status
        
    Returns:
        QuerySet: TeamJoinRequest queryset
    """
    return TeamJoinRequest.objects.filter(
        user=user,
        status=status
    ).select_related('team', 'team__captain').order_by('-created_at')


def get_join_request_by_id(request_id):
    """Get join request by ID."""
    try:
        return TeamJoinRequest.objects.select_related('team', 'user').get(id=request_id)
    except TeamJoinRequest.DoesNotExist:
        return None


# ============================================================================
# INVITES
# ============================================================================

def get_team_invites(team, status='pending'):
    """
    Get invites sent by a team.
    
    Args:
        team (Team): Team instance
        status (str): Filter by status
        
    Returns:
        QuerySet: TeamInvite queryset
    """
    return TeamInvite.objects.filter(
        team=team,
        status=status
    ).select_related('invited_user', 'invited_by').order_by('-created_at')


def get_user_invites(user, status='pending'):
    """
    Get invites received by a user.
    
    Args:
        user (User): User instance
        status (str): Filter by status
        
    Returns:
        QuerySet: TeamInvite queryset
    """
    return TeamInvite.objects.filter(
        invited_user=user,
        status=status
    ).select_related('team', 'team__captain', 'invited_by').order_by('-created_at')


def get_invite_by_id(invite_id):
    """Get invite by ID."""
    try:
        return TeamInvite.objects.select_related(
            'team', 'invited_user', 'invited_by'
        ).get(id=invite_id)
    except TeamInvite.DoesNotExist:
        return None


# ============================================================================
# TEAM GAMES
# ============================================================================

def get_team_games(team):
    """Get games that a team competes in."""
    return TeamGame.objects.filter(team=team).order_by('created_at')


def get_teams_by_game(game):
    """Get teams that compete in a specific game."""
    return Team.objects.filter(
        games__game=game
    ).select_related('captain').distinct().order_by('-created_at')


# ============================================================================
# TEAM SOCIAL LINKS
# ============================================================================

def get_team_social_links(team):
    """Get team's social media links."""
    return TeamSocial.objects.filter(team=team).order_by('platform')


# ============================================================================
# TEAM SETTINGS
# ============================================================================

def get_team_settings(team):
    """Get team settings."""
    try:
        return team.settings
    except TeamSettings.DoesNotExist:
        # Create default settings if not exists
        return TeamSettings.objects.create(team=team)
