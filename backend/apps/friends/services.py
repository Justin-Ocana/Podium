"""
Friends services.

Business logic for managing friendships and friend requests.
"""
from typing import Optional
from django.db import transaction
from django.db.models import Q
from apps.users.models import User
from apps.notifications.models import NotificationType
from .models import FriendRequest, Friendship, FriendRequestStatus
import logging

logger = logging.getLogger(__name__)


def create_notification_with_websocket(recipient, notification_type, message, actor=None, related_object=None):
    """
    Create a notification with WebSocket support (falls back to DB only if Redis unavailable).
    """
    try:
        from apps.notifications.services import create_notification
        return create_notification(
            recipient=recipient,
            notification_type=notification_type,
            message=message,
            actor=actor,
            related_object=related_object
        )
    except Exception as e:
        logger.warning(f"WebSocket unavailable, creating notification without real-time: {e}")
        from apps.notifications.models import Notification
        from django.contrib.contenttypes.models import ContentType
        
        content_type = None
        object_id = None
        
        if related_object:
            content_type = ContentType.objects.get_for_model(related_object)
            object_id = related_object.pk
        
        notification = Notification.objects.create(
            recipient=recipient,
            actor=actor,
            type=notification_type,
            message=message,
            content_type=content_type,
            object_id=object_id
        )
        return notification


@transaction.atomic
def send_friend_request(from_user: User, to_user: User) -> FriendRequest:
    """
    Send a friend request from one user to another.
    
    Logic:
    - Cannot send request to yourself
    - Cannot send if already friends
    - Cannot send if there's already a PENDING request (in either direction)
    - CAN send if previous request was DECLINED or if friendship was removed
    
    Args:
        from_user: User sending the request
        to_user: User receiving the request
    
    Returns:
        Created FriendRequest instance
    
    Raises:
        ValueError: If request cannot be sent
    """
    # Check if users are the same
    if from_user.id == to_user.id:
        raise ValueError("Cannot send friend request to yourself")
    
    # Check if already friends
    if are_friends(from_user, to_user):
        raise ValueError("Users are already friends")
    
    # Check if there's a PENDING request in either direction
    pending_request = FriendRequest.objects.filter(
        Q(from_user=from_user, to_user=to_user, status=FriendRequestStatus.PENDING) |
        Q(from_user=to_user, to_user=from_user, status=FriendRequestStatus.PENDING)
    ).first()
    
    if pending_request:
        if pending_request.from_user == from_user:
            raise ValueError("You already sent a friend request to this user")
        else:
            raise ValueError("This user already sent you a friend request")
    
    # Delete any old DECLINED requests between these users
    # This allows users to send new requests after being declined
    FriendRequest.objects.filter(
        Q(from_user=from_user, to_user=to_user) |
        Q(from_user=to_user, to_user=from_user)
    ).exclude(status=FriendRequestStatus.PENDING).delete()
    
    # Create new friend request
    friend_request = FriendRequest.objects.create(
        from_user=from_user,
        to_user=to_user,
        status=FriendRequestStatus.PENDING
    )
    
    # Send notification
    try:
        create_notification_with_websocket(
            recipient=to_user,
            notification_type=NotificationType.FRIEND_REQUEST,
            message=f"{from_user.username} sent you a friend request",
            actor=from_user,
            related_object=friend_request
        )
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
    
    logger.info(f"Friend request created: {from_user.username} → {to_user.username}")
    return friend_request


@transaction.atomic
def accept_friend_request(request_id: int, user: User) -> Friendship:
    """
    Accept a friend request.
    
    Deletes the FriendRequest, creates a Friendship, deletes the request notification,
    and sends an acceptance notification.
    
    Args:
        request_id: ID of the FriendRequest to accept
        user: User accepting the request (must be the recipient)
    
    Returns:
        Created Friendship instance
    
    Raises:
        FriendRequest.DoesNotExist: If request not found
        ValueError: If user is not the recipient or request is not pending
    """
    friend_request = FriendRequest.objects.select_for_update().get(id=request_id)
    
    # Verify user is the recipient
    if friend_request.to_user.id != user.id:
        raise ValueError("You are not the recipient of this friend request")
    
    # Verify request is pending
    if friend_request.status != FriendRequestStatus.PENDING:
        raise ValueError("Friend request is not pending")
    
    # Store user info before deleting the request
    from_user = friend_request.from_user
    to_user = friend_request.to_user
    
    # Create friendship (ensure user1.id < user2.id for consistency)
    user1, user2 = sorted([from_user, to_user], key=lambda u: u.id)
    friendship = Friendship.objects.create(
        user1=user1,
        user2=user2
    )
    
    # Delete the friend request notification
    try:
        from apps.notifications.models import Notification
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model(friend_request)
        Notification.objects.filter(
            recipient=user,
            content_type=content_type,
            object_id=friend_request.id
        ).delete()
    except Exception as e:
        logger.error(f"Failed to delete request notification: {e}")
    
    # Delete the friend request
    friend_request.delete()
    
    # Send notification to the requester
    create_notification_with_websocket(
        recipient=from_user,
        notification_type=NotificationType.FRIEND_ACCEPTED,
        message=f"{user.username} accepted your friend request",
        actor=user,
        related_object=friendship
    )
    
    logger.info(f"Friend request accepted: {from_user.username} ↔ {to_user.username}")
    return friendship


@transaction.atomic
def decline_friend_request(request_id: int, user: User) -> None:
    """
    Decline a friend request.
    
    Deletes the FriendRequest and its associated notification.
    This allows the sender to send a new request in the future.
    
    Args:
        request_id: ID of the FriendRequest to decline
        user: User declining the request (must be the recipient)
    
    Raises:
        FriendRequest.DoesNotExist: If request not found
        ValueError: If user is not the recipient or request is not pending
    """
    friend_request = FriendRequest.objects.get(id=request_id)
    
    # Verify user is the recipient
    if friend_request.to_user.id != user.id:
        raise ValueError("You are not the recipient of this friend request")
    
    # Verify request is pending
    if friend_request.status != FriendRequestStatus.PENDING:
        raise ValueError("Friend request is not pending")
    
    # Delete the associated notification first
    try:
        from apps.notifications.models import Notification
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model(friend_request)
        Notification.objects.filter(
            recipient=user,
            content_type=content_type,
            object_id=friend_request.id
        ).delete()
    except Exception as e:
        logger.error(f"Failed to delete notification: {e}")
    
    # Delete the friend request completely (allows new requests in the future)
    friend_request.delete()
    logger.info(f"Friend request declined: {friend_request.from_user.username} → {user.username}")


@transaction.atomic
def cancel_friend_request(request_id: int, user: User) -> None:
    """
    Cancel a friend request (sender only).
    
    Args:
        request_id: ID of the FriendRequest to cancel
        user: User canceling the request (must be the sender)
    
    Raises:
        FriendRequest.DoesNotExist: If request not found
        ValueError: If user is not the sender or request is not pending
    """
    friend_request = FriendRequest.objects.get(id=request_id)
    
    # Verify user is the sender
    if friend_request.from_user.id != user.id:
        raise ValueError("You are not the sender of this friend request")
    
    # Verify request is pending
    if friend_request.status != FriendRequestStatus.PENDING:
        raise ValueError("Friend request is not pending")
    
    # Delete associated notification
    try:
        from apps.notifications.models import Notification
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model(friend_request)
        Notification.objects.filter(
            recipient=friend_request.to_user,
            content_type=content_type,
            object_id=friend_request.id
        ).delete()
    except Exception as e:
        logger.error(f"Failed to delete notification: {e}")
    
    # Delete the request
    friend_request.delete()
    logger.info(f"Friend request cancelled: {user.username} → {friend_request.to_user.username}")


@transaction.atomic
def remove_friend(user: User, friend: User) -> None:
    """
    Remove a friendship between two users.
    
    Also cleans up any old friend requests between these users
    to allow sending new requests in the future.
    
    Args:
        user: User removing the friend
        friend: User to be removed as friend
    
    Raises:
        ValueError: If friendship does not exist
    """
    # Find and delete the friendship
    friendship = Friendship.objects.filter(
        Q(user1=user, user2=friend) |
        Q(user1=friend, user2=user)
    ).first()
    
    if not friendship:
        raise ValueError("Friendship does not exist")
    
    friendship.delete()
    
    # Clean up any old friend requests between these users
    # This ensures they can send new requests after removing friendship
    FriendRequest.objects.filter(
        Q(from_user=user, to_user=friend) |
        Q(from_user=friend, to_user=user)
    ).delete()
    
    logger.info(f"Friendship removed: {user.username} ↔ {friend.username}")


def are_friends(user1: User, user2: User) -> bool:
    """
    Check if two users are friends.
    
    Args:
        user1: First user
        user2: Second user
    
    Returns:
        True if users are friends, False otherwise
    """
    return Friendship.objects.filter(
        Q(user1=user1, user2=user2) |
        Q(user1=user2, user2=user1)
    ).exists()


def get_friends(user: User):
    """
    Get all friends of a user.
    
    Args:
        user: User to get friends for
    
    Returns:
        QuerySet of User objects who are friends with the user
    """
    # Get all friendships where user is either user1 or user2
    friendships = Friendship.objects.filter(
        Q(user1=user) | Q(user2=user)
    ).select_related('user1', 'user2')
    
    # Extract the friend users
    friend_ids = []
    for friendship in friendships:
        if friendship.user1.id == user.id:
            friend_ids.append(friendship.user2.id)
        else:
            friend_ids.append(friendship.user1.id)
    
    return User.objects.filter(id__in=friend_ids)


def get_pending_requests(user: User):
    """
    Get all pending friend requests received by a user.
    
    Args:
        user: User to get requests for
    
    Returns:
        QuerySet of FriendRequest objects
    """
    return FriendRequest.objects.filter(
        to_user=user,
        status=FriendRequestStatus.PENDING
    ).select_related('from_user')


def get_sent_requests(user: User):
    """
    Get all pending friend requests sent by a user.
    
    Args:
        user: User to get sent requests for
    
    Returns:
        QuerySet of FriendRequest objects
    """
    return FriendRequest.objects.filter(
        from_user=user,
        status=FriendRequestStatus.PENDING
    ).select_related('to_user')
