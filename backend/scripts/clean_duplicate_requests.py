"""
Script to clean up duplicate and declined friend requests.
Run this to fix existing data issues.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.friends.models import FriendRequest, FriendRequestStatus
from django.db.models import Count

def clean_duplicate_requests():
    """Remove duplicate and declined friend requests."""
    
    # Delete all DECLINED requests (they should have been deleted)
    declined_count = FriendRequest.objects.filter(
        status=FriendRequestStatus.DECLINED
    ).count()
    
    if declined_count > 0:
        print(f"Found {declined_count} DECLINED requests. Deleting...")
        FriendRequest.objects.filter(
            status=FriendRequestStatus.DECLINED
        ).delete()
        print(f"✓ Deleted {declined_count} DECLINED requests")
    else:
        print("✓ No DECLINED requests found")
    
    # Find and remove duplicate PENDING requests (keep the oldest one)
    duplicates = FriendRequest.objects.filter(
        status=FriendRequestStatus.PENDING
    ).values('from_user', 'to_user').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    if duplicates:
        print(f"\nFound {len(duplicates)} sets of duplicate PENDING requests")
        for dup in duplicates:
            requests = FriendRequest.objects.filter(
                from_user_id=dup['from_user'],
                to_user_id=dup['to_user'],
                status=FriendRequestStatus.PENDING
            ).order_by('created_at')
            
            # Keep the first (oldest), delete the rest
            to_delete = list(requests[1:])
            if to_delete:
                print(f"  Keeping request {requests[0].id}, deleting {len(to_delete)} duplicates")
                for req in to_delete:
                    req.delete()
        print("✓ Cleaned up duplicate PENDING requests")
    else:
        print("✓ No duplicate PENDING requests found")
    
    # Show summary
    total_pending = FriendRequest.objects.filter(
        status=FriendRequestStatus.PENDING
    ).count()
    total_accepted = FriendRequest.objects.filter(
        status=FriendRequestStatus.ACCEPTED
    ).count()
    
    print(f"\n=== Summary ===")
    print(f"PENDING requests: {total_pending}")
    print(f"ACCEPTED requests: {total_accepted}")
    print(f"Total: {total_pending + total_accepted}")

if __name__ == '__main__':
    print("=== Cleaning Friend Requests ===\n")
    clean_duplicate_requests()
    print("\n✓ Done!")
