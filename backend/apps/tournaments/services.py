"""
Business logic for tournaments app.
"""
import os
from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from apps.tournaments.models import Tournament, TournamentSettings, TournamentRules


@transaction.atomic
def create_tournament(organizer, **data):
    """
    Create a new tournament with optional settings and rules.
    
    Args:
        organizer (User): User creating the tournament
        **data: Tournament fields including optional settings and rules
        
    Returns:
        Tournament: Created tournament instance
    """
    # Extract nested data
    settings_data = data.pop('settings', None)
    rules_data = data.pop('rules', None)
    
    # Create tournament
    tournament = Tournament.objects.create(
        organizer=organizer,
        **data
    )
    
    # Create settings if provided
    if settings_data:
        TournamentSettings.objects.create(
            tournament=tournament,
            **settings_data
        )
    
    # Create rules if provided
    if rules_data:
        TournamentRules.objects.create(
            tournament=tournament,
            **rules_data
        )
    
    return tournament


@transaction.atomic
def update_tournament(tournament, user, **fields):
    """
    Update tournament fields with permission validation.
    
    Only the organizer can update tournament information.
    Cannot update if tournament is in_progress or finished.
    
    Args:
        tournament (Tournament): Tournament instance to update
        user (User): User attempting the update
        **fields: Fields to update
        
    Returns:
        Tournament: Updated tournament instance
    """
    # Validate organizer permission
    if tournament.organizer != user:
        raise PermissionDenied('Only the tournament organizer can update tournament information.')
    
    # Validate tournament status
    if tournament.status in ['in_progress', 'finished']:
        raise ValidationError('Cannot update tournament that is in progress or finished.')
    
    # Extract nested data
    settings_data = fields.pop('settings', None)
    rules_data = fields.pop('rules', None)
    
    # Update tournament fields
    for field, value in fields.items():
        setattr(tournament, field, value)
    
    # Handle banner update
    if 'banner' in fields and fields['banner']:
        if tournament.banner:
            delete_old_banner(tournament)
    
    tournament.save()
    
    # Update settings if provided
    if settings_data:
        if hasattr(tournament, 'settings'):
            for field, value in settings_data.items():
                setattr(tournament.settings, field, value)
            tournament.settings.save()
        else:
            TournamentSettings.objects.create(
                tournament=tournament,
                **settings_data
            )
    
    # Update rules if provided
    if rules_data:
        if hasattr(tournament, 'rules'):
            for field, value in rules_data.items():
                setattr(tournament.rules, field, value)
            tournament.rules.save()
        else:
            TournamentRules.objects.create(
                tournament=tournament,
                **rules_data
            )
    
    return tournament


@transaction.atomic
def delete_tournament(tournament, user):
    """
    Delete tournament.
    
    Only the organizer can delete the tournament.
    Cannot delete if tournament is in_progress.
    
    Args:
        tournament (Tournament): Tournament instance to delete
        user (User): User attempting the deletion
    """
    # Validate organizer permission
    if tournament.organizer != user:
        raise PermissionDenied('Only the tournament organizer can delete the tournament.')
    
    # Validate tournament status
    if tournament.status == 'in_progress':
        raise ValidationError('Cannot delete tournament that is in progress.')
    
    tournament.delete()


@transaction.atomic
def open_tournament(tournament, user):
    """
    Open tournament for registrations.
    
    Changes status from 'draft' to 'open'.
    
    Args:
        tournament (Tournament): Tournament to open
        user (User): User attempting the action
        
    Returns:
        Tournament: Updated tournament
    """
    if tournament.organizer != user:
        raise PermissionDenied('Only the tournament organizer can open the tournament.')
    
    if tournament.status != 'draft':
        raise ValidationError('Only draft tournaments can be opened.')
    
    tournament.status = 'open'
    tournament.save(update_fields=['status'])
    
    return tournament


@transaction.atomic
def close_tournament(tournament, user):
    """
    Close tournament registrations.
    
    Changes status from 'open' to 'closed'.
    
    Args:
        tournament (Tournament): Tournament to close
        user (User): User attempting the action
        
    Returns:
        Tournament: Updated tournament
    """
    if tournament.organizer != user:
        raise PermissionDenied('Only the tournament organizer can close the tournament.')
    
    if tournament.status != 'open':
        raise ValidationError('Only open tournaments can be closed.')
    
    tournament.status = 'closed'
    tournament.save(update_fields=['status'])
    
    return tournament


@transaction.atomic
def start_tournament(tournament, user):
    """
    Start tournament.
    
    Changes status from 'closed' to 'in_progress'.
    This will trigger bracket generation in the brackets app.
    
    Args:
        tournament (Tournament): Tournament to start
        user (User): User attempting the action
        
    Returns:
        Tournament: Updated tournament
    """
    if tournament.organizer != user:
        raise PermissionDenied('Only the tournament organizer can start the tournament.')
    
    if tournament.status != 'closed':
        raise ValidationError('Only closed tournaments can be started.')
    
    # TODO: Validate minimum participants
    # TODO: Trigger bracket generation
    
    tournament.status = 'in_progress'
    tournament.save(update_fields=['status'])
    
    return tournament


@transaction.atomic
def cancel_tournament(tournament, user):
    """
    Cancel tournament.
    
    Changes status to 'cancelled'.
    Cannot cancel finished tournaments.
    
    Args:
        tournament (Tournament): Tournament to cancel
        user (User): User attempting the action
        
    Returns:
        Tournament: Updated tournament
    """
    if tournament.organizer != user:
        raise PermissionDenied('Only the tournament organizer can cancel the tournament.')
    
    if tournament.status == 'finished':
        raise ValidationError('Cannot cancel finished tournaments.')
    
    tournament.status = 'cancelled'
    tournament.save(update_fields=['status'])
    
    return tournament


@transaction.atomic
def finish_tournament(tournament, user):
    """
    Mark tournament as finished.
    
    Changes status from 'in_progress' to 'finished'.
    
    Args:
        tournament (Tournament): Tournament to finish
        user (User): User attempting the action
        
    Returns:
        Tournament: Updated tournament
    """
    if tournament.organizer != user:
        raise PermissionDenied('Only the tournament organizer can finish the tournament.')
    
    if tournament.status != 'in_progress':
        raise ValidationError('Only in-progress tournaments can be finished.')
    
    tournament.status = 'finished'
    tournament.save(update_fields=['status'])
    
    return tournament


def delete_old_banner(tournament):
    """Delete old banner file when uploading a new one."""
    if tournament.banner:
        banner_path = tournament.banner.path
        
        if os.path.isfile(banner_path):
            try:
                os.remove(banner_path)
            except Exception as e:
                print(f"Error deleting old banner: {e}")
