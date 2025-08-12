# apps/user/interface/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from apps.user.infrastructure.user_repository import UserRepository
from apps.user.interface.serializers import UserSerializer, UserRegistrationSerializer, ProfileUpdateSerializer, ProfileSerializer
from apps.user.services.user_service import UserService


class UserViewSet(viewsets.ViewSet):
    service = UserService(user_repository=UserRepository())

    def get_permissions(self):
        """Define permissions for the viewset."""
        if self.action in ['create', 'list']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        """List all users."""
        users = self.service.list_users()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Register a new user."""
        reg = UserRegistrationSerializer(data=request.data)
        reg.is_valid(raise_exception=True)
        user = self.service.register_user(**reg.validated_data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='me', permission_classes=[IsAuthenticated()])
    def me(self, request):
        """Retrieve the authenticated user's profile."""
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=['patch'], url_path='me/profile', permission_classes=[IsAuthenticated()])
    def update_me_profile(self, request):
        """Update the authenticated user's profile."""
        ser = ProfileUpdateSerializer(instance=request.user.profile, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(UserSerializer(request.user).data)
