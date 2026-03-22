"""
Script to populate test data for friends system.
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.friends.models import FriendRequest, Friendship, FriendRequestStatus
from django.db.models import Q


def populate_friends():
    """Create test users and friend relationships."""
    
    print("Creating test users...")
    
    # Get or create test users
    users = []
    usernames = ['testuser', 'ProGamer123', 'ElitePlayer', 'SkillMaster', 'TeamCaptain', 'NightHawk']
    
    for username in usernames:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username.lower()}@example.com',
                'country': 'United States',
                'region': 'California'
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"Created user: {username}")
        else:
            print(f"User already exists: {username}")
        users.append(user)
    
    testuser = users[0]
    
    print("\nCreating friendships...")
    
    # Make testuser friends with ProGamer123 and ElitePlayer
    for friend in users[1:3]:
        try:
            # Create accepted friend request
            request, created = FriendRequest.objects.get_or_create(
                from_user=friend,
                to_user=testuser,
                defaults={'status': FriendRequestStatus.ACCEPTED}
            )
            if created:
                print(f"Friend request created from {friend.username} to {testuser.username}")
            
            # Create friendship
            user1, user2 = sorted([testuser, friend], key=lambda u: u.id)
            friendship, created = Friendship.objects.get_or_create(
                user1=user1,
                user2=user2
            )
            if created:
                print(f"✅ {testuser.username} and {friend.username} are now friends")
            else:
                print(f"Already friends: {testuser.username} and {friend.username}")
        except Exception as e:
            print(f"Error creating friendship with {friend.username}: {e}")
    
    print("\nCreating pending friend requests...")
    
    # Create pending requests from SkillMaster and TeamCaptain to testuser
    for requester in users[3:5]:
        try:
            request, created = FriendRequest.objects.get_or_create(
                from_user=requester,
                to_user=testuser,
                defaults={'status': FriendRequestStatus.PENDING}
            )
            if created:
                print(f"✅ Pending friend request from {requester.username} to {testuser.username}")
            else:
                print(f"Request already exists from {requester.username}")
        except Exception as e:
            print(f"Error creating request from {requester.username}: {e}")
    
    print("\n✅ Friend data populated successfully!")
    print(f"\nTest user: {testuser.username}")
    print(f"Password: password123")
    print(f"Friends: {', '.join([u.username for u in users[1:3]])}")
    print(f"Pending requests: {', '.join([u.username for u in users[3:5]])}")


if __name__ == '__main__':
    populate_friends()
