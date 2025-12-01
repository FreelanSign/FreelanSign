# apps/user/interface/views/user_views.py
from __future__ import annotations

import logging
from typing import Optional

from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

# Adapters
from apps.user.adapters.persistence.django_user_repository import DjangoUserRepository

# DTOs / VMs
from apps.user.application.dto.user_viewmodels import (
    ProfileViewModel,
    UserListViewModel,
    UserViewModel,
)
from apps.user.application.errors import DuplicateEmailError
from apps.user.application.usecases.change_password import ChangePassword
from apps.user.application.usecases.list_users import ListUsers
from apps.user.application.usecases.register_user import RegisterUser
from apps.user.application.usecases.update_profile import UpdateProfile

# Interface serializers
from apps.user.interface.serializers import (
    ChangePasswordInputSerializer,
    ProfilePatchInputSerializer,
    UserListOutputSerializer,
    UserOutputSerializer,
    UserRegistrationInputSerializer,
)

logger = logging.getLogger("apps.user.views")


def _user_vm_from_model(u) -> UserViewModel:
    """Mappe un modèle User (+profile) vers UserViewModel (lecture simple)."""
    p = getattr(u, "profile", None)
    first = getattr(p, "first_name", None) or ""
    last = getattr(p, "last_name", None) or ""
    full_display = (first + " " + last).strip()

    return UserViewModel(
        id=u.id,
        email=u.email,
        profile=ProfileViewModel(
            first_name=getattr(p, "first_name", None),
            last_name=getattr(p, "last_name", None),
            phone=getattr(p, "phone", None),
            avatar_url=getattr(p, "avatar_url", None),
            role=getattr(p, "role", "freelance"),
            full_name_display=full_display,
        ),
        created_at=getattr(u, "date_joined"),
        updated_at=getattr(p, "updated_at"),
    )


@extend_schema_view(
    list=extend_schema(
        summary="List all users",
        responses={200: OpenApiResponse(UserListOutputSerializer)},
        tags=["Users"],
    ),
    create=extend_schema(
        summary="Register a new user",
        request=UserRegistrationInputSerializer,
        responses={201: OpenApiResponse(UserOutputSerializer)},
        tags=["Users"],
    ),
    me=extend_schema(
        summary="Get or patch current authenticated user",
        responses={200: OpenApiResponse(UserOutputSerializer)},
        tags=["Users"],
    ),
    update_me_profile=extend_schema(
        summary="Update profile of current user",
        request=ProfilePatchInputSerializer,
        responses={200: OpenApiResponse(UserOutputSerializer)},
        tags=["Users"],
    ),
    change_password=extend_schema(
        summary="Change password for current user",
        request=ChangePasswordInputSerializer,
        responses={204: OpenApiResponse({"detail": "Password changed successfully"})},
        tags=["Users"],
    ),
)
class UserViewSet(viewsets.ViewSet):
    """
    HTTP <-> Use cases boundary for Users.
    """

    user_repo = DjangoUserRepository()

    def get_permissions(self):
        if self.action in ["create", "list"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        logger.info("users.list called", extra={"user_id": getattr(request.user, "id", None)})

        uc = ListUsers(self.user_repo)
        vm_list: UserListViewModel = uc.execute()

        payload = UserListOutputSerializer.from_vm_list(vm_list).data
        logger.debug("users.list returning %d users", payload["count"])
        return Response(payload, status=status.HTTP_200_OK)

    def create(self, request):
        logger.info(
            "users.create called",
            extra={"params": {k: v for k, v in request.data.items() if k != "password"}},
        )

        ser = UserRegistrationInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dto = ser.to_dto()

        uc = RegisterUser(self.user_repo)
        try:
            vm: UserViewModel = uc.execute(dto)
        except DuplicateEmailError as e:
            return Response(
                {"email": ["A user with this email already exists."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        logger.info("users.create succeeded for user_id=%s", vm.id)
        return Response(UserOutputSerializer.from_vm(vm).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get", "patch"], url_path="me", permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        GET  -> current user
        PATCH -> partial profile update
        """
        if request.method == "GET":
            logger.debug("users.me (GET) called", extra={"user_id": request.user.id})
            # petite lecture directe via repo, mapping présentation-only
            u = self.user_repo.get_by_id(request.user.id)
            vm = _user_vm_from_model(u)
            return Response(UserOutputSerializer.from_vm(vm).data, status=status.HTTP_200_OK)

        # PATCH
        logger.info("users.me (PATCH) called", extra={"user_id": request.user.id, "params": request.data})
        # accepte payload à plat ou sous `profile`
        payload = request.data.get("profile") if isinstance(request.data.get("profile"), dict) else request.data
        if not request.user.is_staff and isinstance(payload, dict) and "role" in payload:
            payload = {k: v for k, v in payload.items() if k != "role"}
        ser = ProfilePatchInputSerializer(data=payload)
        ser.is_valid(raise_exception=True)
        dto = ser.to_dto(user_id=request.user.id, updater_is_staff=request.user.is_staff)

        uc = UpdateProfile(self.user_repo)
        vm: UserViewModel = uc.execute(dto)

        logger.info("users.me (PATCH) succeeded", extra={"user_id": request.user.id})
        return Response(UserOutputSerializer.from_vm(vm).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["patch"], url_path="me/profile", permission_classes=[IsAuthenticated])
    def update_me_profile(self, request):
        logger.info("users.update_me_profile called", extra={"user_id": request.user.id, "params": request.data})

        ser = ProfilePatchInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dto = ser.to_dto(user_id=request.user.id, updater_is_staff=request.user.is_staff)

        uc = UpdateProfile(self.user_repo)
        vm: UserViewModel = uc.execute(dto)

        logger.info("users.update_me_profile succeeded for user_id=%s", request.user.id)
        return Response(UserOutputSerializer.from_vm(vm).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="me/change-password", permission_classes=[IsAuthenticated])
    def change_password(self, request):
        logger.info("change_password called", extra={"user_id": request.user.id})

        ser = ChangePasswordInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dto = ser.to_dto(user_id=request.user.id)

        uc = ChangePassword(self.user_repo)
        uc.execute(dto)

        logger.info("change_password succeeded for user_id=%s", request.user.id)
        return Response({"detail": "Password changed successfully"}, status=status.HTTP_204_NO_CONTENT)
