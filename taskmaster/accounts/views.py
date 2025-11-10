"""
Views for the accounts app.
Demonstrates Django REST Framework viewsets and API views.
"""

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.cache import cache
from .models import User, UserProfile
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model.
    Demonstrates CRUD operations with caching.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally filter users by search query.
        Demonstrates query optimization with select_related.
        """
        queryset = User.objects.select_related('profile').filter(is_active=True)
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                email__icontains=search
            ) | queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            )
        return queryset

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a user with Redis caching.
        Demonstrates caching pattern.
        """
        user_id = kwargs.get('pk')
        cache_key = f'user_{user_id}'

        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # If not in cache, get from database
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Store in cache for 5 minutes
        cache.set(cache_key, data, 300)

        return Response(data)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user's information.
        Endpoint: /api/accounts/users/me/
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """
        Update current user's profile.
        Endpoint: /api/accounts/users/update_profile/
        """
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Invalidate cache
        cache_key = f'user_{request.user.id}'
        cache.delete(cache_key)

        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Change current user's password.
        Endpoint: /api/accounts/users/change_password/
        """
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Endpoint: /api/accounts/register/
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'user': UserSerializer(user).data,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
