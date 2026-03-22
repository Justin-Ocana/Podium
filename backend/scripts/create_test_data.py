"""
Create test data for development.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from apps.teams.models import Team, TeamMembership

User = get_user_model()

def create_test_data():
    """Create test users and teams."""
    print("🔄 Creating test data...")
    
    # Create or get test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✅ Created user: {user.username}")
    else:
        print(f"ℹ️  User already exists: {user.username}")
    
    # Create or get token
    token, created = Token.objects.get_or_create(user=user)
    if created:
        print(f"✅ Created token for {user.username}: {token.key}")
    else:
        print(f"ℹ️  Token already exists for {user.username}: {token.key}")
    
    # Create a test team
    team, created = Team.objects.get_or_create(
        name='Phoenix Esports',
        defaults={
            'tag': 'PHX',
            'description': 'A competitive esports team',
            'captain': user
        }
    )
    
    if created:
        print(f"✅ Created team: {team.name} ({team.tag})")
        
        # Create membership for captain
        membership, _ = TeamMembership.objects.get_or_create(
            team=team,
            user=user,
            defaults={
                'role': 'captain',
                'status': 'active'
            }
        )
        print(f"✅ Created membership for {user.username} in {team.name}")
    else:
        print(f"ℹ️  Team already exists: {team.name}")
    
    print("\n✅ Test data created successfully!")
    print(f"\nLogin credentials:")
    print(f"  Username: testuser")
    print(f"  Password: testpass123")
    print(f"  Token: {token.key}")

if __name__ == '__main__':
    create_test_data()
