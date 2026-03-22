"""
Authentication views for users app.

Handles user registration, login, logout, and password management.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

from apps.users.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    PasswordChangeSerializer,
    TokenSerializer,
    UserDetailSerializer,
)
from apps.users.services import register_user, change_password


class RegisterView(APIView):
    """
    API endpoint for user registration.
    
    POST /api/users/auth/register/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Register a new user.
        
        Returns user data and authentication token.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            # Create user and token
            user, token = register_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            
            # Serialize response
            user_serializer = UserDetailSerializer(user)
            token_serializer = TokenSerializer(token)
            
            return Response({
                'user': user_serializer.data,
                'auth': token_serializer.data,
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API endpoint for user login.
    
    POST /api/users/auth/login/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Authenticate user and return token.
        
        Accepts username or email along with password.
        """
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Get or create token
            token, created = Token.objects.get_or_create(user=user)
            
            # Serialize response
            user_serializer = UserDetailSerializer(user)
            token_serializer = TokenSerializer(token)
            
            return Response({
                'user': user_serializer.data,
                'auth': token_serializer.data,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    API endpoint for user logout.
    
    POST /api/users/auth/logout/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Logout user by deleting their authentication token.
        """
        try:
            # Delete the user's token
            request.user.auth_token.delete()
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Logout failed'
            }, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    """
    API endpoint for changing user password.
    
    POST /api/users/me/change-password/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Change user password after validating current password.
        """
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            try:
                # Change password
                change_password(
                    user=request.user,
                    current_password=serializer.validated_data['current_password'],
                    new_password=serializer.validated_data['new_password']
                )
                
                # Delete old token and create new one for security
                Token.objects.filter(user=request.user).delete()
                token = Token.objects.create(user=request.user)
                token_serializer = TokenSerializer(token)
                
                return Response({
                    'message': 'Password changed successfully',
                    'auth': token_serializer.data
                }, status=status.HTTP_200_OK)
                
            except ValueError as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
