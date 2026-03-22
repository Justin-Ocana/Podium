from django.contrib import admin
from apps.tournaments.models import Tournament, TournamentSettings, TournamentRules


class TournamentSettingsInline(admin.StackedInline):
    """Inline admin for tournament settings."""
    model = TournamentSettings
    can_delete = False
    verbose_name_plural = 'Settings'


class TournamentRulesInline(admin.StackedInline):
    """Inline admin for tournament rules."""
    model = TournamentRules
    can_delete = False
    verbose_name_plural = 'Rules'


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    """Admin interface for Tournament model."""
    list_display = ['name', 'game', 'organizer', 'status', 'start_date', 'created_at']
    list_filter = ['status', 'format', 'participant_type', 'game']
    search_fields = ['name', 'slug', 'game', 'organizer__username']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'game', 'banner', 'organizer')
        }),
        ('Configuration', {
            'fields': ('format', 'participant_type', 'max_participants')
        }),
        ('Dates', {
            'fields': ('registration_start', 'registration_end', 'start_date')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [TournamentSettingsInline, TournamentRulesInline]
