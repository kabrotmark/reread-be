from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import json


@method_decorator(csrf_exempt, name='dispatch')
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except json.JSONDecodeError:
        return Response({
            'error': 'Invalid JSON'
        }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'Username already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        return Response({
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_201_CREATED)
        
    except json.JSONDecodeError:
        return Response({
            'error': 'Invalid JSON'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_info_view(request):
    if request.user.is_authenticated:
        return Response({
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email
            }
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Not authenticated'
        }, status=status.HTTP_401_UNAUTHORIZED)