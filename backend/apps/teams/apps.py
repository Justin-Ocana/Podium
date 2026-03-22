from django.apps import AppConfig


class TeamsConfig(AppConfig):
    """
    Configuration for the teams app.
    
    This app manages competitive teams, memberships, invitations and team profiles
    for the Podium tournament platform.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.teams'
    verbose_name = 'Teams'
