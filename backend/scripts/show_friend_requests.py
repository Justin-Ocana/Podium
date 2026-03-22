"""
Show all friend requests in the database.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.friends.models import FriendRequest, Friendship

def show_requests():
    print("=== All Friend Requests ===\n")
    
    requests = FriendRequest.objects.all().order_by('-created_at')
    
    for req in requests:
        print(f"ID: {req.id}")
        print(f"  From: {req.from_user.username}")
        print(f"  To: {req.to_user.username}")
        print(f"  Status: {req.status}")
        print(f"  Created: {req.created_at}")
        
        # Check if friendship exists
        friendship = Friendship.objects.filter(
            models.Q(user1=req.from_user, user2=req.to_user) |
            models.Q(user1=req.to_user, user2=req.from_user)
        ).first()
        
        if friendship:
            print(f"  ✓ Friendship exists")
        else:
            print(f"  ✗ NO friendship (orphaned)")
        print()
    
    print(f"Total requests: {requests.count()}")
    
    print("\n=== All Friendships ===\n")
    friendships = Friendship.objects.all()
    for f in friendships:
        print(f"  {f.user1.username} <-> {f.user2.username}")
    print(f"\nTotal friendships: {friendships.count()}")

if __name__ == '__main__':
    from django.db import models
    show_requests()
