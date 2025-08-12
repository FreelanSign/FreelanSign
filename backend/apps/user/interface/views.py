from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.user.interface.serializers import (
    UserSerializer, UserRegistrationSerializer, ProfileUpdateSerializer
)
from apps.user.services.user_service import UserService
from apps.user.infrastructure.user_repository import UserRepository


class UserViewSet(viewsets.ViewSet):
    service = UserService(user_repository=UserRepository())

    def get_permissions(self):
        if self.action in ["create", "list"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(
        responses=UserSerializer(many=True)
    )
    def list(self, request):
        users = self.service.list_users()
        return Response(UserSerializer(users, many=True).data)

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: UserSerializer},
        summary="Register a new user"
    )
    def create(self, request):
        reg = UserRegistrationSerializer(data=request.data)
        reg.is_valid(raise_exception=True)
        user = self.service.register_user(**reg.validated_data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(
        detail=False, methods=["get"], url_path="me",
        permission_classes=[IsAuthenticated]   # ⚠️ classe, pas instance
    )
    @extend_schema(
        responses=UserSerializer,
        summary="Get current authenticated user"
    )
    def me(self, request):
        return Response(UserSerializer(request.user).data)

    @action(
        detail=False, methods=["patch"], url_path="me/profile",
        permission_classes=[IsAuthenticated]
    )
    @extend_schema(
        request=ProfileUpdateSerializer,
        responses=UserSerializer,
        summary="Update profile of current user"
    )
    def update_me_profile(self, request):
        ser = ProfileUpdateSerializer(request.user.profile, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(UserSerializer(request.user).data)
