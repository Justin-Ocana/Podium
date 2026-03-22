"""
Clean ACCEPTED friend requests that don't have corresponding friendships.
This allows users to send new friend requests after removing friends.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.friends.models import FriendRequest, Friendship, FriendRequestStatus
from django.db.models import Q

def clean_orphaned_accepted_requests():
    """Remove ACCEPTED friend requests that don't have a corresponding friendship."""
    print("=== Cleaning Orphaned ACCEPTED Friend Requests ===\n")
    
    # Get all ACCEPTED requests
    accepted_requests = FriendRequest.objects.filter(status=FriendRequestStatus.ACCEPTED)
    print(f"Found {accepted_requests.count()} ACCEPTED requests")
    
    orphaned_count = 0
    
    for request in accepted_requests:
        # Check if friendship exists
        friendship_exists = Friendship.objects.filter(
            Q(user1=request.from_user, user2=request.to_user) |
            Q(user1=request.to_user, user2=request.from_user)
        ).exists()
        
        if not friendship_exists:
            print(f"  ✗ Deleting orphaned request: {request.from_user.username} -> {request.to_user.username}")
            request.delete()
            orphaned_count += 1
    
    if orphaned_count == 0:
        print("  ✓ No orphaned ACCEPTED requests found")
    else:
        print(f"\n✓ Deleted {orphaned_count} orphaned ACCEPTED request(s)")
    
    print("\n=== Summary ===")
    remaining = FriendRequest.objects.filter(status=FriendRequestStatus.ACCEPTED).count()
    print(f"Remaining ACCEPTED requests: {remaining}")
    print("✓ Done!")

if __name__ == '__main__':
    clean_orphaned_accepted_requests()
