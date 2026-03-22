"""
URL configuration for teams app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TeamViewSet,
    TeamMembersListView,
    InvitePlayerView,
    AcceptInvitationView,
    RejectInvitationView,
    RemoveMemberView,
    LeaveTeamView,
    TransferCaptainView,
    search_games,
    get_game_detail,
    list_cached_games,
)
from .views.upload_views import (
    upload_team_logo,
    upload_team_banner,
    delete_team_logo,
    delete_team_banner
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'teams', TeamViewSet, basename='team')

# URL patterns
urlpatterns = [
    # Game endpoints
    path('games/search/', search_games, name='games-search'),
    path('games/<int:rawg_id>/', get_game_detail, name='game-detail'),
    path('games/', list_cached_games, name='games-list'),
    
    # Membership endpoints under /api/teams/{id}/
    path('teams/<int:pk>/members/', TeamMembersListView.as_view(), name='team-members'),
    path('teams/<int:pk>/invite/', InvitePlayerView.as_view(), name='team-invite'),
    path('teams/<int:pk>/accept-invite/', AcceptInvitationView.as_view(), name='team-accept-invite'),
    path('teams/<int:pk>/reject-invite/', RejectInvitationView.as_view(), name='team-reject-invite'),
    path('teams/<int:pk>/remove-member/', RemoveMemberView.as_view(), name='team-remove-member'),
    path('teams/<int:pk>/leave/', LeaveTeamView.as_view(), name='team-leave'),
    path('teams/<int:pk>/transfer-captain/', TransferCaptainView.as_view(), name='team-transfer-captain'),
    
    # Upload endpoints
    path('teams/<int:team_id>/upload-logo/', upload_team_logo, name='upload-team-logo'),
    path('teams/<int:team_id>/upload-banner/', upload_team_banner, name='upload-team-banner'),
    path('teams/<int:team_id>/delete-logo/', delete_team_logo, name='delete-team-logo'),
    path('teams/<int:team_id>/delete-banner/', delete_team_banner, name='delete-team-banner'),
    
    # Include router URLs (handles /api/teams/, /api/teams/{id}/, /api/teams/{slug}/)
    path('', include(router.urls)),
]
