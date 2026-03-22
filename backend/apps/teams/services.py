"""
Business logic for teams app.

This module contains functions for write operations and complex business logic.
For read-only queries, see selectors.py
"""
from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from apps.teams.models import (
    Team, TeamMembership, TeamJoinRequest, TeamInvite,
    TeamGame, TeamStats, TeamSocial, TeamSettings
)
from apps.users.models import User


@transaction.atomic
def create_team(creator, name, tag, description='', **optional_fields):
    """
    Create a new team and assign creator as captain.
    
    Creates Team, TeamMembership (captain), TeamStats, and TeamSettings.
    
    Args:
        creator (User): User creating the team (becomes captain)
        name (str): Team name (3-50 characters)
        tag (str): Team tag/abbreviation (2-5 characters)
        description (str): Team description
        **optional_fields: logo_url, banner_url, country, region, colors, etc.
        
    Returns:
        Team: Created team instance
    """
    # Normalize inputs
    name = name.strip()
    tag = tag.upper().strip()
    
    # Validate name uniqueness (case-insensitive)
    if Team.objects.filter(name__iexact=name).exists():
        raise ValidationError({'name': 'A team with this name already exists.'})
    
    # Validate tag uniqueness
    if Team.objects.filter(tag__iexact=tag).exists():
        raise ValidationError({'tag': 'A team with this tag already exists.'})
    
    # Create team
    team = Team.objects.create(
        name=name,
        tag=tag,
        description=description,
        captain=creator,
        **optional_fields
    )
    
    # Create captain membership
    TeamMembership.objects.create(
        user=creator,
        team=team,
        role='captain',
        status='active'
    )
    
    # Create team stats
    TeamStats.objects.create(team=team)
    
    # Create team settings
    TeamSettings.objects.create(team=team)
    
    return team


@transaction.atomic
def update_team(team, user, **fields):
    """
    Update team fields with permission validation.
    
    Only captain can update team information.
    
    Args:
        team (Team): Team to update
        user (User): User attempting update
        **fields: Fields to update
        
    Returns:
        Team: Updated team
    """
    # Validate captain permission
    if team.captain != user:
        raise PermissionDenied('Only the team captain can update team information.')
    
    # Handle name update
    if 'name' in fields:
        new_name = fields['name'].strip()
        if Team.objects.filter(name__iexact=new_name).exclude(pk=team.pk).exists():
            raise ValidationError({'name': 'A team with this name already exists.'})
        team.name = new_name
    
    # Handle tag update
    if 'tag' in fields:
        new_tag = fields['tag'].upper().strip()
        if Team.objects.filter(tag__iexact=new_tag).exclude(pk=team.pk).exists():
            raise ValidationError({'tag': 'A team with this tag already exists.'})
        team.tag = new_tag
    
    # Update other fields
    for field in ['description', 'logo_url', 'banner_url', 'country', 'region',
                  'primary_color', 'secondary_color', 'sponsor', 'founded_year', 'website']:
        if field in fields:
            setattr(team, field, fields[field])
    
    team.save()
    return team


@transaction.atomic
def delete_team(team, user):
    """
    Delete team and all associated data.
    
    Only captain can delete the team.
    
    Args:
        team (Team): Team to delete
        user (User): User attempting deletion
    """
    if team.captain != user:
        raise PermissionDenied('Only the team captain can delete the team.')
    
    team.delete()


# ============================================================================
# JOIN REQUEST MANAGEMENT
# ============================================================================

@transaction.atomic
def create_join_request(team, user, message=''):
    """
    Create a join request from user to team.
    
    Args:
        team (Team): Team to join
        user (User): User requesting to join
        message (str): Optional message
        
    Returns:
        TeamJoinRequest: Created request
    """
    # Check team settings
    if hasattr(team, 'settings'):
        if not team.settings.allow_requests:
            raise ValidationError('This team does not accept join requests.')
        
        if team.settings.join_policy == 'invite_only':
            raise ValidationError('This team is invite-only.')
    
    # Check if user already has active membership
    if TeamMembership.objects.filter(user=user, team=team, status='active').exists():
        raise ValidationError('You are already a member of this team.')
    
    # Check if pending request exists
    if TeamJoinRequest.objects.filter(team=team, user=user, status='pending').exists():
        raise ValidationError('You already have a pending request to this team.')
    
    # Create request
    request = TeamJoinRequest.objects.create(
        team=team,
        user=user,
        message=message,
        status='pending'
    )
    
    return request


@transaction.atomic
def accept_join_request(request, user):
    """
    Accept a join request (captain/manager only).
    
    Args:
        request (TeamJoinRequest): Request to accept
        user (User): User accepting (must be captain/manager)
        
    Returns:
        TeamMembership: Created membership
    """
    # Validate permission
    membership = TeamMembership.objects.filter(
        team=request.team,
        user=user,
        role__in=['captain', 'manager'],
        status='active'
    ).first()
    
    if not membership:
        raise PermissionDenied('Only captain or manager can accept join requests.')
    
    # Validate request status
    if request.status != 'pending':
        raise ValidationError('This request has already been processed.')
    
    # Check max members
    if hasattr(request.team, 'settings'):
        active_count = TeamMembership.objects.filter(
            team=request.team,
            status='active'
        ).count()
        
        if active_count >= request.team.settings.max_members:
            raise ValidationError('Team has reached maximum member limit.')
    
    # Update request status
    request.status = 'accepted'
    request.save(update_fields=['status', 'updated_at'])
    
    # Create membership
    new_membership = TeamMembership.objects.create(
        user=request.user,
        team=request.team,
        role='player',
        status='active'
    )
    
    return new_membership


@transaction.atomic
def reject_join_request(request, user):
    """
    Reject a join request (captain/manager only).
    
    Args:
        request (TeamJoinRequest): Request to reject
        user (User): User rejecting (must be captain/manager)
    """
    # Validate permission
    membership = TeamMembership.objects.filter(
        team=request.team,
        user=user,
        role__in=['captain', 'manager'],
        status='active'
    ).first()
    
    if not membership:
        raise PermissionDenied('Only captain or manager can reject join requests.')
    
    # Validate request status
    if request.status != 'pending':
        raise ValidationError('This request has already been processed.')
    
    # Update request status
    request.status = 'rejected'
    request.save(update_fields=['status', 'updated_at'])


@transaction.atomic
def cancel_join_request(request, user):
    """
    Cancel own join request.
    
    Args:
        request (TeamJoinRequest): Request to cancel
        user (User): User cancelling (must be request owner)
    """
    if request.user != user:
        raise PermissionDenied('You can only cancel your own requests.')
    
    if request.status != 'pending':
        raise ValidationError('This request has already been processed.')
    
    request.status = 'cancelled'
    request.save(update_fields=['status', 'updated_at'])


# ============================================================================
# INVITE MANAGEMENT
# ============================================================================

@transaction.atomic
def invite_player(team, inviter, user_id):
    """
    Invite a player to join the team (captain/manager only).
    
    Args:
        team (Team): Team sending invite
        inviter (User): User sending invite (must be captain/manager)
        user_id (int): ID of user to invite
        
    Returns:
        TeamInvite: Created invite
    """
    # Validate permission
    membership = TeamMembership.objects.filter(
        team=team,
        user=inviter,
        role__in=['captain', 'manager'],
        status='active'
    ).first()
    
    if not membership:
        raise PermissionDenied('Only captain or manager can invite players.')
    
    # Get user to invite
    try:
        invited_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise ValidationError({'user_id': 'User not found.'})
    
    # Check if user already has active membership
    if TeamMembership.objects.filter(user=invited_user, team=team, status='active').exists():
        raise ValidationError('User is already a member of this team.')
    
    # Check if pending invite exists
    if TeamInvite.objects.filter(team=team, invited_user=invited_user, status='pending').exists():
        raise ValidationError('User already has a pending invitation to this team.')
    
    # Create invite
    invite = TeamInvite.objects.create(
        team=team,
        invited_user=invited_user,
        invited_by=inviter,
        status='pending'
    )
    
    return invite


@transaction.atomic
def accept_invite(invite, user):
    """
    Accept a team invitation.
    
    Args:
        invite (TeamInvite): Invite to accept
        user (User): User accepting (must be invited user)
        
    Returns:
        TeamMembership: Created membership
    """
    if invite.invited_user != user:
        raise PermissionDenied('You can only accept your own invitations.')
    
    if invite.status != 'pending':
        raise ValidationError('This invitation has already been processed.')
    
    # Check max members
    if hasattr(invite.team, 'settings'):
        active_count = TeamMembership.objects.filter(
            team=invite.team,
            status='active'
        ).count()
        
        if active_count >= invite.team.settings.max_members:
            raise ValidationError('Team has reached maximum member limit.')
    
    # Update invite status
    invite.status = 'accepted'
    invite.save(update_fields=['status', 'updated_at'])
    
    # Create membership
    membership = TeamMembership.objects.create(
        user=user,
        team=invite.team,
        role='player',
        status='active'
    )
    
    return membership


@transaction.atomic
def decline_invite(invite, user):
    """
    Decline a team invitation.
    
    Args:
        invite (TeamInvite): Invite to decline
        user (User): User declining (must be invited user)
    """
    if invite.invited_user != user:
        raise PermissionDenied('You can only decline your own invitations.')
    
    if invite.status != 'pending':
        raise ValidationError('This invitation has already been processed.')
    
    invite.status = 'declined'
    invite.save(update_fields=['status', 'updated_at'])


# ============================================================================
# MEMBERSHIP MANAGEMENT
# ============================================================================

@transaction.atomic
def remove_member(team, remover, user_id):
    """
    Remove a member from the team (captain/manager only).
    
    Args:
        team (Team): Team to remove member from
        remover (User): User removing (must be captain/manager)
        user_id (int): ID of user to remove
        
    Returns:
        TeamMembership: Updated membership
    """
    # Validate permission
    remover_membership = TeamMembership.objects.filter(
        team=team,
        user=remover,
        role__in=['captain', 'manager'],
        status='active'
    ).first()
    
    if not remover_membership:
        raise PermissionDenied('Only captain or manager can remove members.')
    
    # Get user to remove
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise ValidationError({'user_id': 'User not found.'})
    
    # Cannot remove captain
    if user == team.captain:
        raise ValidationError('Cannot remove the team captain. Transfer captaincy first.')
    
    # Get membership
    try:
        membership = TeamMembership.objects.get(
            user=user,
            team=team,
            status='active'
        )
    except TeamMembership.DoesNotExist:
        raise ValidationError('User is not an active member of this team.')
    
    # Update status
    membership.status = 'inactive'
    membership.save(update_fields=['status'])
    
    return membership


@transaction.atomic
def leave_team(team, user):
    """
    Leave a team.
    
    Captain cannot leave without transferring captaincy first.
    
    Args:
        team (Team): Team to leave
        user (User): User leaving
        
    Returns:
        TeamMembership: Updated membership
    """
    if user == team.captain:
        raise ValidationError('Captain cannot leave the team. Transfer captaincy first.')
    
    try:
        membership = TeamMembership.objects.get(
            user=user,
            team=team,
            status='active'
        )
    except TeamMembership.DoesNotExist:
        raise ValidationError('You are not an active member of this team.')
    
    membership.status = 'left'
    membership.save(update_fields=['status'])
    
    return membership


@transaction.atomic
def transfer_captain(team, current_captain, new_captain_id):
    """
    Transfer team captaincy to another active member.
    
    Args:
        team (Team): Team to transfer captaincy in
        current_captain (User): Current captain
        new_captain_id (int): ID of new captain
        
    Returns:
        tuple: (old_membership, new_membership)
    """
    if team.captain != current_captain:
        raise PermissionDenied('Only the team captain can transfer captaincy.')
    
    # Get new captain
    try:
        new_captain = User.objects.get(pk=new_captain_id)
    except User.DoesNotExist:
        raise ValidationError({'user_id': 'User not found.'})
    
    # Validate new captain is active member
    try:
        new_captain_membership = TeamMembership.objects.get(
            user=new_captain,
            team=team,
            status='active'
        )
    except TeamMembership.DoesNotExist:
        raise ValidationError('User must be an active member to become captain.')
    
    # Get current captain membership
    current_captain_membership = TeamMembership.objects.get(
        user=current_captain,
        team=team,
        status='active',
        role='captain'
    )
    
    # Atomic transfer
    current_captain_membership.role = 'player'
    current_captain_membership.save(update_fields=['role'])
    
    new_captain_membership.role = 'captain'
    new_captain_membership.save(update_fields=['role'])
    
    # Update team captain
    team.captain = new_captain
    team.save(update_fields=['captain'])
    
    return current_captain_membership, new_captain_membership


@transaction.atomic
def update_member_role(team, updater, user_id, new_role):
    """
    Update a member's role (captain only).
    
    Args:
        team (Team): Team
        updater (User): User updating (must be captain)
        user_id (int): ID of user to update
        new_role (str): New role (player, manager, coach)
        
    Returns:
        TeamMembership: Updated membership
    """
    if team.captain != updater:
        raise PermissionDenied('Only the team captain can update member roles.')
    
    if new_role not in ['player', 'manager', 'coach']:
        raise ValidationError('Invalid role. Must be player, manager, or coach.')
    
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise ValidationError({'user_id': 'User not found.'})
    
    if user == team.captain:
        raise ValidationError('Cannot change captain role. Use transfer captaincy instead.')
    
    try:
        membership = TeamMembership.objects.get(
            user=user,
            team=team,
            status='active'
        )
    except TeamMembership.DoesNotExist:
        raise ValidationError('User is not an active member of this team.')
    
    membership.role = new_role
    membership.save(update_fields=['role'])
    
    return membership


# ============================================================================
# TEAM GAMES MANAGEMENT
# ============================================================================

@transaction.atomic
def add_team_game(team, user, game):
    """
    Add a game to team's roster (captain only).
    
    Args:
        team (Team): Team
        user (User): User adding (must be captain)
        game (str): Game identifier
        
    Returns:
        TeamGame: Created team game
    """
    if team.captain != user:
        raise PermissionDenied('Only the team captain can add games.')
    
    # Check if already exists
    if TeamGame.objects.filter(team=team, game=game).exists():
        raise ValidationError('Team already competes in this game.')
    
    team_game = TeamGame.objects.create(
        team=team,
        game=game
    )
    
    return team_game


@transaction.atomic
def remove_team_game(team, user, game):
    """
    Remove a game from team's roster (captain only).
    
    Args:
        team (Team): Team
        user (User): User removing (must be captain)
        game (str): Game identifier
    """
    if team.captain != user:
        raise PermissionDenied('Only the team captain can remove games.')
    
    try:
        team_game = TeamGame.objects.get(team=team, game=game)
        team_game.delete()
    except TeamGame.DoesNotExist:
        raise ValidationError('Team does not compete in this game.')


# ============================================================================
# TEAM SOCIAL LINKS MANAGEMENT
# ============================================================================

@transaction.atomic
def add_social_link(team, user, platform, url):
    """
    Add or update a social media link (captain only).
    
    Args:
        team (Team): Team
        user (User): User adding (must be captain)
        platform (str): Platform identifier
        url (str): URL to profile
        
    Returns:
        TeamSocial: Created or updated social link
    """
    if team.captain != user:
        raise PermissionDenied('Only the team captain can manage social links.')
    
    social, created = TeamSocial.objects.update_or_create(
        team=team,
        platform=platform,
        defaults={'url': url}
    )
    
    return social


@transaction.atomic
def remove_social_link(team, user, platform):
    """
    Remove a social media link (captain only).
    
    Args:
        team (Team): Team
        user (User): User removing (must be captain)
        platform (str): Platform identifier
    """
    if team.captain != user:
        raise PermissionDenied('Only the team captain can manage social links.')
    
    try:
        social = TeamSocial.objects.get(team=team, platform=platform)
        social.delete()
    except TeamSocial.DoesNotExist:
        raise ValidationError('Social link not found.')


# ============================================================================
# TEAM SETTINGS MANAGEMENT
# ============================================================================

@transaction.atomic
def update_team_settings(team, user, **settings):
    """
    Update team settings (captain only).
    
    Args:
        team (Team): Team
        user (User): User updating (must be captain)
        **settings: Settings to update
        
    Returns:
        TeamSettings: Updated settings
    """
    if team.captain != user:
        raise PermissionDenied('Only the team captain can update team settings.')
    
    team_settings, created = TeamSettings.objects.get_or_create(team=team)
    
    for field in ['visibility', 'join_policy', 'allow_requests', 'max_members']:
        if field in settings:
            setattr(team_settings, field, settings[field])
    
    team_settings.save()
    
    return team_settings
