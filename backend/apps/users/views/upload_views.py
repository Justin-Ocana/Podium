"""
Upload views for handling avatar and banner uploads to Cloudinary.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import cloudinary.uploader
from apps.users.models import User


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    """
    Upload user avatar to Cloudinary.
    Expects: multipart/form-data with 'avatar' file
    Returns: { avatar_url: str }
    """
    if 'avatar' not in request.FILES:
        return Response(
            {'error': 'No avatar file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    avatar_file = request.FILES['avatar']
    
    # Validate file size (max 5MB)
    if avatar_file.size > 5 * 1024 * 1024:
        return Response(
            {'error': 'Avatar file size must be less than 5MB'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if avatar_file.content_type not in allowed_types:
        return Response(
            {'error': 'Avatar must be a JPEG, PNG, or WebP image'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Upload to Cloudinary with transformations
        upload_result = cloudinary.uploader.upload(
            avatar_file,
            folder=f'podium/avatars/{request.user.id}',
            public_id=f'avatar_{request.user.id}',
            overwrite=True,
            transformation=[
                {'width': 400, 'height': 400, 'crop': 'fill', 'gravity': 'face'},
                {'quality': 'auto:good'},
                {'fetch_format': 'auto'}
            ]
        )
        
        avatar_url = upload_result['secure_url']
        
        # Update user model
        request.user.avatar_url = avatar_url
        request.user.save(update_fields=['avatar_url'])
        
        return Response({
            'avatar_url': avatar_url,
            'message': 'Avatar uploaded successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to upload avatar: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_banner(request):
    """
    Upload user profile banner to Cloudinary.
    Expects: multipart/form-data with 'banner' file
    Returns: { banner_url: str }
    """
    if 'banner' not in request.FILES:
        return Response(
            {'error': 'No banner file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    banner_file = request.FILES['banner']
    
    # Validate file size (max 10MB)
    if banner_file.size > 10 * 1024 * 1024:
        return Response(
            {'error': 'Banner file size must be less than 10MB'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if banner_file.content_type not in allowed_types:
        return Response(
            {'error': 'Banner must be a JPEG, PNG, or WebP image'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Upload to Cloudinary with transformations
        upload_result = cloudinary.uploader.upload(
            banner_file,
            folder=f'podium/banners/{request.user.id}',
            public_id=f'banner_{request.user.id}',
            overwrite=True,
            transformation=[
                {'width': 1920, 'height': 400, 'crop': 'fill'},
                {'quality': 'auto:good'},
                {'fetch_format': 'auto'}
            ]
        )
        
        banner_url = upload_result['secure_url']
        
        # Update user model (you'll need to add banner_url field to User model)
        request.user.banner_url = banner_url
        request.user.save(update_fields=['banner_url'])
        
        return Response({
            'banner_url': banner_url,
            'message': 'Banner uploaded successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to upload banner: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_avatar(request):
    """
    Delete user avatar from Cloudinary and reset to default.
    """
    try:
        # Delete from Cloudinary
        public_id = f'podium/avatars/{request.user.id}/avatar_{request.user.id}'
        cloudinary.uploader.destroy(public_id)
        
        # Reset user avatar
        request.user.avatar_url = None
        request.user.save(update_fields=['avatar_url'])
        
        return Response({
            'message': 'Avatar deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to delete avatar: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_banner(request):
    """
    Delete user banner from Cloudinary.
    """
    try:
        # Delete from Cloudinary
        public_id = f'podium/banners/{request.user.id}/banner_{request.user.id}'
        cloudinary.uploader.destroy(public_id)
        
        # Reset user banner
        request.user.banner_url = None
        request.user.save(update_fields=['banner_url'])
        
        return Response({
            'message': 'Banner deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to delete banner: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
