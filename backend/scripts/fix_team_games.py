"""
Fix team_games table conflict.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def fix_team_games():
    """Drop team_games table and reapply migrations."""
    print("🔄 Fixing team_games conflict...")
    
    with connection.cursor() as cursor:
        # Drop team_games table
        print("❌ Dropping team_games table...")
        cursor.execute('DROP TABLE IF EXISTS "team_games" CASCADE')
        
        # Drop games table too since it's related
        print("❌ Dropping games table...")
        cursor.execute('DROP TABLE IF EXISTS "games" CASCADE')
        
        connection.commit()
        print("✅ Tables dropped successfully")
    
    # Now apply the migration
    from django.core.management import call_command
    print("\n🔄 Applying teams.0002_game_and_more migration...")
    call_command('migrate', 'teams', '0002', verbosity=2)
    print("\n✅ Migration applied successfully!")

if __name__ == '__main__':
    fix_team_games()
