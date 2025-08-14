# apps/user/interface/views.py
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.interface.serializers import (
    UserSerializer, UserRegistrationSerializer, ProfileUpdateSerializer, ChangePasswordSerializer, LogoutSerializer
)
from apps.user.services.user_service import UserService
from apps.user.infrastructure.user_repository import UserRepository
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    list=extend_schema(
        summary="List all users",
        responses={200: OpenApiResponse(UserSerializer(many=True))},
        tags=["Users"]
    ),
    create=extend_schema(
        summary="Register a new user",
        request=UserRegistrationSerializer,
        responses={201: OpenApiResponse(UserSerializer)},
        tags=["Users"]
    ),
    me=extend_schema(
        summary="Get current authenticated user",
        responses={200: OpenApiResponse(UserSerializer)},
        tags=["Users"]
    ),
    update_me_profile=extend_schema(
        summary="Update profile of current user",
        request=ProfileUpdateSerializer,
        responses={200: OpenApiResponse(UserSerializer)},
        tags=["Users"]
    ),
    change_password=extend_schema(
        summary="Change password for current user",
        request=ChangePasswordSerializer,
        responses={204: OpenApiResponse({"detail": "Password changed successfully"})},
        tags=["Users"]
    ),
    logout=extend_schema(
        summary="Logout current user",
        request=LogoutSerializer,
        responses={204: OpenApiResponse({"detail": "Logged out successfully"})},
        tags=["Auth"]
    )
)
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
        permission_classes=[IsAuthenticated]
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

    @action(detail=False, methods=["post"], url_path="me/change-password",
        permission_classes=[IsAuthenticated])
    def change_password(self, request):
        ser = ChangePasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(ser.validated_data["current_password"]):
            return Response({"current_password": "Incorrect password"}, status=400)
        user.set_password(ser.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password changed successfully"}, status=204)

    @action(detail=False, methods=["post"], url_path="logout",
        permission_classes=[IsAuthenticated])
    def logout(self, request):
        ser = LogoutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            token = RefreshToken(ser.validated_data["refresh"])
            token.blacklist()
        except Exception:
            return Response({"refresh": ["Invalid token"]}, status=400)
        return Response({"detail": "Logged out successfully"}, status=204)
