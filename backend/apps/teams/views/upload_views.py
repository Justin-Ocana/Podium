"""
Upload views for handling team logo and banner uploads to Cloudinary.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import cloudinary.uploader
from apps.teams.models import Team, TeamMembership


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_team_logo(request, team_id):
    """
    Upload team logo to Cloudinary.
    
    POST /api/teams/{team_id}/upload-logo/
    
    Expects: multipart/form-data with 'logo' file
    Returns: { logo_url: str }
    
    Only captain can upload logo.
    """
    # Get team
    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        return Response(
            {'error': 'Team not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if user is captain
    if team.captain != request.user:
        return Response(
            {'error': 'Only the team captain can upload the logo'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if 'logo' not in request.FILES:
        return Response(
            {'error': 'No logo file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    logo_file = request.FILES['logo']
    
    # Validate file size (max 5MB)
    if logo_file.size > 5 * 1024 * 1024:
        return Response(
            {'error': 'Logo file size must be less than 5MB'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if logo_file.content_type not in allowed_types:
        return Response(
            {'error': 'Logo must be a JPEG, PNG, or WebP image'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Upload to Cloudinary with transformations (square logo)
        upload_result = cloudinary.uploader.upload(
            logo_file,
            folder=f'podium/teams/{team.id}/logo',
            public_id=f'logo_{team.id}',
            overwrite=True,
            transformation=[
                {'width': 400, 'height': 400, 'crop': 'fill'},
                {'quality': 'auto:good'},
                {'fetch_format': 'auto'}
            ]
        )
        
        logo_url = upload_result['secure_url']
        
        # Update team model
        team.logo_url = logo_url
        team.save(update_fields=['logo_url'])
        
        return Response({
            'logo_url': logo_url,
            'message': 'Logo uploaded successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to upload logo: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_team_banner(request, team_id):
    """
    Upload team banner to Cloudinary.
    
    POST /api/teams/{team_id}/upload-banner/
    
    Expects: multipart/form-data with 'banner' file
    Returns: { banner_url: str }
    
    Only captain can upload banner.
    """
    # Get team
    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        return Response(
            {'error': 'Team not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if user is captain
    if team.captain != request.user:
        return Response(
            {'error': 'Only the team captain can upload the banner'},
            status=status.HTTP_403_FORBIDDEN
        )
    
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
        # Upload to Cloudinary with transformations (wide banner)
        upload_result = cloudinary.uploader.upload(
            banner_file,
            folder=f'podium/teams/{team.id}/banner',
            public_id=f'banner_{team.id}',
            overwrite=True,
            transformation=[
                {'width': 1200, 'height': 400, 'crop': 'fill'},
                {'quality': 'auto:good'},
                {'fetch_format': 'auto'}
            ]
        )
        
        banner_url = upload_result['secure_url']
        
        # Update team model
        team.banner_url = banner_url
        team.save(update_fields=['banner_url'])
        
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
def delete_team_logo(request, team_id):
    """
    Delete team logo from Cloudinary.
    
    DELETE /api/teams/{team_id}/delete-logo/
    
    Only captain can delete logo.
    """
    # Get team
    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        return Response(
            {'error': 'Team not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if user is captain
    if team.captain != request.user:
        return Response(
            {'error': 'Only the team captain can delete the logo'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if not team.logo_url:
        return Response(
            {'error': 'Team has no logo to delete'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Delete from Cloudinary
        public_id = f'podium/teams/{team.id}/logo/logo_{team.id}'
        cloudinary.uploader.destroy(public_id)
        
        # Update team model
        team.logo_url = None
        team.save(update_fields=['logo_url'])
        
        return Response({
            'message': 'Logo deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to delete logo: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_team_banner(request, team_id):
    """
    Delete team banner from Cloudinary.
    
    DELETE /api/teams/{team_id}/delete-banner/
    
    Only captain can delete banner.
    """
    # Get team
    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        return Response(
            {'error': 'Team not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if user is captain
    if team.captain != request.user:
        return Response(
            {'error': 'Only the team captain can delete the banner'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if not team.banner_url:
        return Response(
            {'error': 'Team has no banner to delete'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Delete from Cloudinary
        public_id = f'podium/teams/{team.id}/banner/banner_{team.id}'
        cloudinary.uploader.destroy(public_id)
        
        # Update team model
        team.banner_url = None
        team.save(update_fields=['banner_url'])
        
        return Response({
            'message': 'Banner deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to delete banner: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
