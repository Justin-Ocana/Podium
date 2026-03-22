"""
Script to check user teams and memberships.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.teams.models import TeamMembership, Team
from apps.users.models import User

# Get user - change this to your username
username = "TestXD"

try:
    user = User.objects.get(username=username)
    print(f"\n{'='*60}")
    print(f"Checking teams for user: {username} (ID: {user.id})")
    print(f"{'='*60}\n")
    
    # Check teams where user is captain
    print("1. Teams where user is CAPTAIN:")
    captain_teams = Team.objects.filter(captain=user)
    print(f"   Found {captain_teams.count()} teams")
    for team in captain_teams:
        print(f"   - {team.name} ({team.tag}) - ID: {team.id}")
    
    # Check active memberships
    print("\n2. ACTIVE TeamMemberships:")
    active_memberships = TeamMembership.objects.filter(user=user, status='active')
    print(f"   Found {active_memberships.count()} active memberships")
    for m in active_memberships:
        print(f"   - {m.team.name} ({m.team.tag}) - Role: {m.role} - Status: {m.status}")
    
    # Check ALL memberships
    print("\n3. ALL TeamMemberships (any status):")
    all_memberships = TeamMembership.objects.filter(user=user)
    print(f"   Found {all_memberships.count()} total memberships")
    for m in all_memberships:
        print(f"   - {m.team.name} ({m.team.tag}) - Role: {m.role} - Status: {m.status}")
    
    # Check if captain teams have memberships
    print("\n4. Checking if captain teams have membership records:")
    for team in captain_teams:
        membership_exists = TeamMembership.objects.filter(user=user, team=team).exists()
        if membership_exists:
            membership = TeamMembership.objects.get(user=user, team=team)
            print(f"   ✓ {team.name}: Membership EXISTS - Role: {membership.role}, Status: {membership.status}")
        else:
            print(f"   ✗ {team.name}: NO MEMBERSHIP RECORD!")
    
    print(f"\n{'='*60}\n")
    
except User.DoesNotExist:
    print(f"User '{username}' not found!")
