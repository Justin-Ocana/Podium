"""
Membership views for Podium platform.

This module contains API views for team membership operations:
- List team members
- Invite players to teams
- Accept/reject invitations
- Remove members from teams
- Leave teams
- Transfer team captaincy
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError, PermissionDenied
from apps.teams.models import Team
from apps.teams.selectors import get_team_by_id, get_team_members
from apps.teams.services import (
    invite_player,
    accept_invite,
    decline_invite,
    remove_member,
    leave_team,
    transfer_captain
)
from apps.teams.serializers.membership_serializers import (
    MembershipSerializer,
    InvitePlayerSerializer,
    TransferCaptainSerializer,
    RemoveMemberSerializer
)
from apps.teams.permissions import IsCaptain


class TeamMembersListView(APIView):
    """
    GET /api/teams/{id}/members/
    
    List all active members of a team.
    """
    
    def get(self, request, pk):
        """
        List active team members.
        
        Returns members ordered by captain first, then by joined_at.
        """
        team = get_team_by_id(pk)
        if not team:
            return Response(
                {'detail': 'Team not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        members = get_team_members(team)
        serializer = MembershipSerializer(members, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class InvitePlayerView(APIView):
    """
    POST /api/teams/{id}/invite/
    
    Invite a player to join the team.
    Only the team captain can invite players.
    """
    permission_classes = [IsAuthenticated, IsCaptain]
    
    def post(self, request, pk):
        """
        Invite a player to the team.
        
        Request body:
            {
                "user_id": 123
            }
        """
        team = get_team_by_id(pk)
        if not team:
            return Response(
                {'detail': 'Team not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check captain permission
        self.check_object_permissions(request, team)
        
        serializer = InvitePlayerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            membership = invite_player(
                team=team,
                captain=request.user,
                user_id=serializer.validated_data['user_id']
            )
            
            response_serializer = MembershipSerializer(membership)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        except ValidationError as e:
            return Response(
                e.message_dict if hasattr(e, 'message_dict') else {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionDenied as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


class AcceptInvitationView(APIView):
    """
    POST /api/teams/{id}/accept-invite/
    
    Accept a team invitation.
    User must have a pending invitation to the team.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        """
        Accept invitation to join the team.
        """
        team = get_team_by_id(pk)
        if not team:
            return Response(
                {'detail': 'Team not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            membership = accept_invite(
                team=team,
                user=request.user
            )
            
            serializer = MembershipSerializer(membership)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        
        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class RejectInvitationView(APIView):
    """
    POST /api/teams/{id}/reject-invite/
    
    Reject a team invitation.
    User must have a pending invitation to the team.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        """
        Reject invitation to join the team.
        """
        team = get_team_by_id(pk)
        if not team:
            return Response(
                {'detail': 'Team not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            decline_invite(
                team=team,
                user=request.user
            )
            
            return Response(
                {'detail': 'Invitation rejected successfully.'},
                status=status.HTTP_200_OK
            )
        
        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class RemoveMemberView(APIView):
    """
    POST /api/teams/{id}/remove-member/
    
    Remove a member from the team.
    Only the team captain can remove members.
    """
    permission_classes = [IsAuthenticated, IsCaptain]
    
    def post(self, request, pk):
        """
        Remove a member from the team.
        
        Request body:
            {
                "user_id": 123
            }
        """
        team = get_team_by_id(pk)
        if not team:
            return Response(
                {'detail': 'Team not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check captain permission
        self.check_object_permissions(request, team)
        
        serializer = RemoveMemberSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            membership = remove_member(
                team=team,
                captain=request.user,
                user_id=serializer.validated_data['user_id']
            )
            
            response_serializer = MembershipSerializer(membership)
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )
        
        except ValidationError as e:
            return Response(
                e.message_dict if hasattr(e, 'message_dict') else {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionDenied as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


class LeaveTeamView(APIView):
    """
    POST /api/teams/{id}/leave/
    
    Leave a team.
    Captain cannot leave without transferring captaincy first.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        """
        Leave the team.
        """
        team = get_team_by_id(pk)
        if not team:
            return Response(
                {'detail': 'Team not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            membership = leave_team(
                team=team,
                user=request.user
            )
            
            serializer = MembershipSerializer(membership)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        
        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TransferCaptainView(APIView):
    """
    POST /api/teams/{id}/transfer-captain/
    
    Transfer team captaincy to another active player.
    Only the current captain can transfer captaincy.
    """
    permission_classes = [IsAuthenticated, IsCaptain]
    
    def post(self, request, pk):
        """
        Transfer captaincy to another player.
        
        Request body:
            {
                "user_id": 123
            }
        """
        team = get_team_by_id(pk)
        if not team:
            return Response(
                {'detail': 'Team not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check captain permission
        self.check_object_permissions(request, team)
        
        serializer = TransferCaptainSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            old_membership, new_membership = transfer_captain(
                team=team,
                current_captain=request.user,
                new_captain_id=serializer.validated_data['user_id']
            )
            
            return Response(
                {
                    'detail': 'Captaincy transferred successfully.',
                    'old_captain': MembershipSerializer(old_membership).data,
                    'new_captain': MembershipSerializer(new_membership).data
                },
                status=status.HTTP_200_OK
            )
        
        except ValidationError as e:
            return Response(
                e.message_dict if hasattr(e, 'message_dict') else {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionDenied as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
