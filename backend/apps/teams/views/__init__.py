"""
Views for the teams app.

This package contains views for team and membership operations:
- team_views.py: ViewSets for team CRUD operations
- membership_views.py: Views for membership and invitation operations
- game_views.py: Views for game search and cache
"""
from apps.teams.views.team_views import TeamViewSet
from apps.teams.views.membership_views import (
    TeamMembersListView,
    InvitePlayerView,
    AcceptInvitationView,
    RejectInvitationView,
    RemoveMemberView,
    LeaveTeamView,
    TransferCaptainView
)
from apps.teams.views.game_views import (
    search_games,
    get_game_detail,
    list_cached_games
)

__all__ = [
    'TeamViewSet',
    'TeamMembersListView',
    'InvitePlayerView',
    'AcceptInvitationView',
    'RejectInvitationView',
    'RemoveMemberView',
    'LeaveTeamView',
    'TransferCaptainView',
    'search_games',
    'get_game_detail',
    'list_cached_games',
]
