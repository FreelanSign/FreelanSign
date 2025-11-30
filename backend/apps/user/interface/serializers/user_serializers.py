# apps/user/interface/serializers/user_serializers.py
"""
Interface serializers (API boundary).
- Input serializers: validate API payload shape and convert to application DTOs.
- Output serializers: render application ViewModels to API payloads.
No business rules here (kept in domain). No DB access here.
"""
from __future__ import annotations

from typing import Optional
from urllib.parse import unquote

from rest_framework import serializers

from apps.user.application.dto.user_inputs import (
    ChangePasswordInput,
    CreateProfessionalInput,
    RegisterUserInput,
    UpdateProfessionalInput,
    UpdateProfileInput,
)
from apps.user.application.dto.user_viewmodels import ProfessionalViewModel, ProfileViewModel, UserListViewModel, UserViewModel

# Only imported for enum/choices exposure at the boundary (not for persistence)
from apps.user.models.models import Profile

# =============================================================================
# Inputs (API -> DTO)
# =============================================================================


class UserRegistrationInputSerializer(serializers.Serializer):
    """
    Shape validator for user registration. Converts to RegisterUserInput DTO.
    Supports both legacy nested `profile` and flat fields.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    # Optional (flat)
    full_name = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    birthday = serializers.DateField(required=False)
    avatar_url = serializers.URLField(required=False, allow_blank=True)
    role = serializers.ChoiceField(required=False, choices=Profile.Role.choices)

    # Optional legacy shape
    profile = serializers.DictField(required=False)

    def to_dto(self) -> RegisterUserInput:
        d = self.validated_data
        prof = d.get("profile") or {}
        return RegisterUserInput(
            email=(d["email"] or "").strip().lower(),
            password=d["password"],
            first_name=d.get("first_name") or prof.get("first_name"),
            last_name=d.get("last_name") or prof.get("last_name"),
            phone=d.get("phone") or prof.get("phone"),
            birthday=d.get("birthday") or prof.get("birthday"),
            avatar_url=d.get("avatar_url") or prof.get("avatar_url"),
            role=d.get("role") or prof.get("role") or Profile.Role.FREELANCE,
            full_name=d.get("full_name"),
        )


class ProfilePatchInputSerializer(serializers.Serializer):
    """
    Shape validator for partial profile updates (PATCH).
    Converts to UpdateProfileInput DTO using context (user_id, is_staff).
    """

    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    birthday = serializers.DateField(required=False, allow_null=True)
    avatar_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    role = serializers.ChoiceField(required=False, choices=Profile.Role.choices)

    def to_dto(self, *, user_id: int, updater_is_staff: bool) -> UpdateProfileInput:
        d = self.validated_data
        # Only include keys that were actually provided
        return UpdateProfileInput(
            user_id=user_id,
            first_name=d.get("first_name") if "first_name" in d else None,
            last_name=d.get("last_name") if "last_name" in d else None,
            phone=d.get("phone") if "phone" in d else None,
            birthday=d.get("birthday") if "birthday" in d else None,
            avatar_url=d.get("avatar_url") if "avatar_url" in d else None,
            role=d.get("role") if "role" in d else None,
            updater_is_staff=updater_is_staff,
        )


class ChangePasswordInputSerializer(serializers.Serializer):
    """
    Shape validator for password change. Converts to ChangePasswordInput DTO.
    """

    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def to_dto(self, *, user_id: int) -> ChangePasswordInput:
        d = self.validated_data
        return ChangePasswordInput(
            user_id=user_id,
            current_password=d["current_password"],
            new_password=d["new_password"],
        )


class ProfessionalUpsertInputSerializer(serializers.Serializer):
    """
    Shape validator for creating/updating a professional profile.
    Converts to CreateProfessionalInput or UpdateProfessionalInput DTO.
    """

    name = serializers.CharField(required=False, allow_blank=True)
    status_juridique = serializers.CharField(required=False, allow_blank=True)
    domaine_id = serializers.IntegerField(required=False, allow_null=True)
    tjm_cents = serializers.IntegerField(required=False)
    number_pro = serializers.CharField(required=False, allow_blank=True)
    service_type_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )

    def to_create_dto(self, *, user_id: int) -> CreateProfessionalInput:
        d = self.validated_data
        return CreateProfessionalInput(
            user_id=user_id,
            name=d.get("name"),
            status_juridique=d.get("status_juridique"),
            domaine_id=d.get("domaine_id"),
            tjm_cents=d.get("tjm_cents", 0),
            number_pro=d.get("number_pro"),
            service_type_ids=d.get("service_type_ids") or [],
        )

    def to_update_dto(
        self,
        *,
        professional_id: int,
        user_id: int,
        updater_is_staff: bool,
    ) -> UpdateProfessionalInput:
        d = self.validated_data
        return UpdateProfessionalInput(
            professional_id=professional_id,
            user_id=user_id,
            name=d.get("name") if "name" in d else None,
            status_juridique=d.get("status_juridique") if "status_juridique" in d else None,
            domaine_id=d.get("domaine_id") if "domaine_id" in d else None,
            tjm_cents=d.get("tjm_cents") if "tjm_cents" in d else None,
            number_pro=d.get("number_pro") if "number_pro" in d else None,
            service_type_ids=d.get("service_type_ids") if "service_type_ids" in d else None,
            updater_is_staff=updater_is_staff,
        )


class LogoutSerializer(serializers.Serializer):
    """
    Minimal shape for logout endpoint (refresh token blacklisting).
    """

    refresh = serializers.CharField()


# =============================================================================
# Outputs (VM -> API)
# =============================================================================


class ProfileOutputSerializer(serializers.Serializer):
    """
    Renders ProfileViewModel to API payload.
    """

    first_name = serializers.CharField(allow_null=True)
    last_name = serializers.CharField(allow_null=True)
    birthday = serializers.DateField(allow_null=True)
    phone = serializers.CharField(allow_null=True)
    avatar_url = serializers.CharField(allow_null=True)
    role = serializers.CharField()
    full_name_display = serializers.CharField()

    @staticmethod
    def from_vm(vm: ProfileViewModel) -> "ProfileOutputSerializer":
        # DRF accepts dataclass instances when used as `instance`
        return ProfileOutputSerializer(instance=vm)


class UserOutputSerializer(serializers.Serializer):
    """
    Renders UserViewModel to API payload.
    """

    id = serializers.IntegerField()
    email = serializers.EmailField()
    profile = ProfileOutputSerializer()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    @staticmethod
    def from_vm(vm: UserViewModel) -> "UserOutputSerializer":
        return UserOutputSerializer(instance=vm)


class UserListOutputSerializer(serializers.Serializer):
    """
    Renders UserListViewModel to paginated-like payload.
    """

    count = serializers.IntegerField()
    results = UserOutputSerializer(many=True)

    @staticmethod
    def from_vm_list(vm: UserListViewModel) -> "UserListOutputSerializer":
        payload = {
            "count": vm.total_count,
            "results": [UserOutputSerializer.from_vm(u).data for u in vm.users],
        }
        return UserListOutputSerializer(instance=payload)


class ProfessionalOutputSerializer(serializers.Serializer):
    """
    Renders ProfessionalViewModel to API payload.
    """

    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    name = serializers.CharField(allow_null=True)
    status_juridique = serializers.CharField(allow_null=True)
    domaine_id = serializers.IntegerField(allow_null=True)
    domaine_name = serializers.CharField(allow_null=True)
    tjm_cents = serializers.IntegerField()
    tjm_display = serializers.CharField()
    number_pro = serializers.CharField(allow_null=True)
    service_type_ids = serializers.ListField(child=serializers.IntegerField())
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    @staticmethod
    def from_vm(vm: ProfessionalViewModel) -> "ProfessionalOutputSerializer":
        return ProfessionalOutputSerializer(instance=vm)


class RequestPasswordResetSerializer(serializers.Serializer):
    """
    Input shape for requesting a password reset
    """

    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    """
    Input shape for resetting a password from a signed token.
    """

    token = serializers.CharField()
    new_password = serializers.CharField()

    # appelé automatiquement par .is_valid()
    def validate_token(self, value: str) -> str:
        """
        Decode the token from URL-encoded format.
        """
        return unquote(value)
