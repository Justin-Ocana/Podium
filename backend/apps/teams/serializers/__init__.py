"""
Serializers for the teams app.

This package contains serializers for team and membership operations:
- team_serializers.py: Serializers for team CRUD operations
- membership_serializers.py: Serializers for membership and invitation operations
- game_serializers.py: Serializers for game search and cache
"""

from .team_serializers import (
    TeamCreateSerializer,
    TeamSerializer,
    TeamUpdateSerializer,
    TeamListSerializer,
    CaptainNestedSerializer,
)

from .membership_serializers import (
    MembershipSerializer,
    InvitePlayerSerializer,
    TransferCaptainSerializer,
    RemoveMemberSerializer,
    UserNestedSerializer,
    TeamMembershipSerializer,
)

from .game_serializers import (
    GameSerializer,
    GameSearchSerializer,
)

__all__ = [
    'TeamCreateSerializer',
    'TeamSerializer',
    'TeamUpdateSerializer',
    'TeamListSerializer',
    'CaptainNestedSerializer',
    'MembershipSerializer',
    'InvitePlayerSerializer',
    'TransferCaptainSerializer',
    'RemoveMemberSerializer',
    'UserNestedSerializer',
    'TeamMembershipSerializer',
    'GameSerializer',
    'GameSearchSerializer',
]
