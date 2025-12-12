# apps/user/interface/views/user_views.py
from __future__ import annotations

import logging
from typing import Optional

from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.core.models.audit import AuditLog

# Core services
from apps.core.services.audit import log_audit

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
    export_data=extend_schema(
        summary="Export all user data (RGPD Article 20)",
        description="Export complete user data including profile, accounts, clients, and quotes in JSON format",
        responses={200: OpenApiResponse(description="User data exported successfully")},
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

    @action(detail=False, methods=["get"], url_path="export-data", permission_classes=[IsAuthenticated])
    def export_data(self, request):
        """
        Export complet des données de l'utilisateur (RGPD Art. 20 - Portabilité).

        Returns all user data in JSON format including:
        - User profile information
        - Accounts information
        - Clients list
        - Quotes summary
        """
        logger.info("export_data called", extra={"user_id": request.user.id})
        user = request.user

        # Collect all user data
        data = {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "date_joined": user.date_joined.isoformat() if user.date_joined else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            },
            "profile": {},
            "accounts": [],
            "clients": [],
            "quotes": [],
        }

        # Profile data
        # AIDEV_NOTE: user profile est l'ancien model de Account, à vérifier si on doit le garder ici ou non.
        if hasattr(user, "profile") and user.profile:
            profile = user.profile
            data["profile"] = {
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "phone": profile.phone,
                "avatar_url": profile.avatar_url,
                "role": profile.role,
                "created_at": profile.created_at.isoformat() if hasattr(profile, "created_at") else None,
                "updated_at": profile.updated_at.isoformat() if hasattr(profile, "updated_at") else None,
            }

        # Accounts data
        if hasattr(user, "accounts"):
            for account in user.accounts.filter(is_active=True):
                data["accounts"].append(
                    {
                        "id": str(account.id),
                        "display_name": account.display_name,
                        "legal_form": account.legal_form,
                        "legal_id": account.legal_id,
                        "created_at": account.created_at.isoformat() if hasattr(account, "created_at") else None,
                    }
                )

                # Clients for this account
                if hasattr(account, "clients"):
                    for client in account.clients.filter(is_deleted=False):
                        data["clients"].append(
                            {
                                "id": str(client.id),
                                "account_id": str(account.id),
                                "name": client.name,
                                "email": client.email,
                                "phone": client.phone,
                                "created_at": client.created_at.isoformat() if hasattr(client, "created_at") else None,
                            }
                        )

                # Quotes for this account
                if hasattr(account, "quotes"):
                    for quote in account.quotes.all():
                        data["quotes"].append(
                            {
                                "id": str(quote.id),
                                "account_id": str(account.id),
                                "reference": quote.reference,
                                "title": quote.title,
                                "total": str(quote.total) if hasattr(quote, "total") else None,
                                "currency": quote.currency if hasattr(quote, "currency") else "EUR",
                                "status": quote.status,
                                "issue_date": (
                                    quote.issue_date.isoformat() if hasattr(quote, "issue_date") and quote.issue_date else None
                                ),
                                "created_at": quote.created_at.isoformat() if hasattr(quote, "created_at") else None,
                            }
                        )

        # Log the export action
        log_audit(
            action=AuditLog.Action.DATA_EXPORT_REQUESTED,
            actor=user,
            target_model="User",
            target_id=user.id,
            request=request,
            metadata={"export_type": "full"},
        )

        logger.info("export_data succeeded for user_id=%s", request.user.id)
        return Response(data, status=status.HTTP_200_OK)
