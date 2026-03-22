"""
Debug script to see all friend requests in the database.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.friends.models import FriendRequest, FriendRequestStatus
from apps.users.models import User

def debug_requests():
    """Show all friend requests with details."""
    
    print("=== ALL FRIEND REQUESTS ===\n")
    
    all_requests = FriendRequest.objects.all().order_by('-created_at')
    
    if not all_requests:
        print("No friend requests found in database")
        return
    
    for req in all_requests:
        print(f"ID: {req.id}")
        print(f"  From: {req.from_user.username} (ID: {req.from_user.id})")
        print(f"  To: {req.to_user.username} (ID: {req.to_user.id})")
        print(f"  Status: {req.status}")
        print(f"  Created: {req.created_at}")
        print(f"  Updated: {req.updated_at}")
        print()
    
    print(f"\n=== SUMMARY ===")
    print(f"Total requests: {all_requests.count()}")
    print(f"PENDING: {all_requests.filter(status=FriendRequestStatus.PENDING).count()}")
    print(f"ACCEPTED: {all_requests.filter(status=FriendRequestStatus.ACCEPTED).count()}")
    print(f"DECLINED: {all_requests.filter(status=FriendRequestStatus.DECLINED).count()}")
    
    print(f"\n=== USERS ===")
    users = User.objects.all()
    for user in users:
        print(f"{user.username} (ID: {user.id})")

if __name__ == '__main__':
    debug_requests()
