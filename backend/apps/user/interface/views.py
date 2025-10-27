# apps/user/interface/views.py
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Adapters (implémentations concrètes des ports)
from apps.user.adapters.persistence.django_user_repository import (
    DjangoProfessionalRepository,
    DjangoUserRepository,
)

# DTOs / VMs
from apps.user.application.dto.user_inputs import GetUserInput
from apps.user.application.dto.user_viewmodels import (
    ProfessionalViewModel,
    ProfileViewModel,
    UserListViewModel,
    UserViewModel,
)
from apps.user.application.errors import DuplicateEmailError
from apps.user.application.usecases.change_password import ChangePassword
from apps.user.application.usecases.create_professional import CreateProfessional

# Use cases
from apps.user.application.usecases.list_users import ListUsers
from apps.user.application.usecases.register_user import RegisterUser
from apps.user.application.usecases.update_professional import UpdateProfessional
from apps.user.application.usecases.update_profile import UpdateProfile

# Interface serializers (boundary)
from apps.user.interface.serializers import (
    ChangePasswordInputSerializer,
    ProfessionalOutputSerializer,
    ProfessionalUpsertInputSerializer,
    ProfilePatchInputSerializer,
    UserListOutputSerializer,
    UserOutputSerializer,
    UserRegistrationInputSerializer,
)

logger = logging.getLogger("apps.user.views")


# ---------------------------------------------------------------------------
# Helpers (presentation-only): builder de VMs depuis modèles quand on lit
# (pas de règles métier ici; formatage simple côté présentation)
# ---------------------------------------------------------------------------


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
            birthday=getattr(p, "birthday", None),
            phone=getattr(p, "phone", None),
            avatar_url=getattr(p, "avatar_url", None),
            role=getattr(p, "role", "freelance"),
            full_name_display=full_display,
        ),
        created_at=getattr(u, "date_joined"),
        updated_at=getattr(p, "updated_at"),
    )


def _professional_vm_from_model(pro) -> ProfessionalViewModel:
    """Mappe un modèle ProfessionalUser vers ProfessionalViewModel (lecture simple)."""
    domaine = getattr(pro, "domaine", None)
    domaine_name = getattr(domaine, "name", None) if domaine else None
    # formatter lisible pour la sortie
    tjm_cents = getattr(pro, "tjm_cents", 0) or 0
    tjm_display = f"{tjm_cents/100:.2f}"

    service_type_ids = []
    if hasattr(pro, "service_types"):
        try:
            service_type_ids = list(pro.service_types.values_list("id", flat=True))
        except Exception:
            # si pas de M2M préchargé
            service_type_ids = [st.id for st in pro.service_types.all()]

    return ProfessionalViewModel(
        id=pro.id,
        user_id=pro.user_id,
        name=getattr(pro, "name", None),
        status_juridique=getattr(pro, "status_juridique", None),
        domaine_id=getattr(pro, "domaine_id", None),
        domaine_name=domaine_name,
        tjm_cents=tjm_cents,
        tjm_display=tjm_display,
        number_pro=getattr(pro, "number_pro", None),
        service_type_ids=service_type_ids,
        created_at=getattr(pro, "created_at"),
        updated_at=getattr(pro, "updated_at"),
    )


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Professional (me + onboarding)
# ---------------------------------------------------------------------------


class ProfessionalUserMeView(APIView):
    permission_classes = [IsAuthenticated]
    logger = logging.getLogger("apps.user.views.ProfessionalUserMeView")

    pro_repo = DjangoProfessionalRepository()
    user_repo = DjangoUserRepository()

    @extend_schema(
        responses={
            200: OpenApiResponse(ProfessionalOutputSerializer),
            404: OpenApiResponse(description="Professional profile not found."),
        },
        summary="Get professional profile for current authenticated user",
        tags=["Professional Users"],
    )
    def get(self, request):
        self.logger.info("ProfessionalUserMeView.get called", extra={"user_id": request.user.id})
        pro = self.pro_repo.get_by_user_id(request.user.id)
        if not pro:
            self.logger.debug("ProfessionalUserMeView.get: no professional for user_id=%s", request.user.id)
            return Response({"detail": "Professional profile not found."}, status=status.HTTP_404_NOT_FOUND)

        vm = _professional_vm_from_model(pro)
        return Response(ProfessionalOutputSerializer.from_vm(vm).data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ProfessionalUpsertInputSerializer,
        responses={200: OpenApiResponse(ProfessionalOutputSerializer)},
        summary="Patch (create if missing) professional profile for current user",
        tags=["Professional Users"],
    )
    def patch(self, request):
        self.logger.info("ProfessionalUserMeView.patch called", extra={"user_id": request.user.id, "params": request.data})

        pro = self.pro_repo.get_by_user_id(request.user.id)
        ser = ProfessionalUpsertInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        if not pro:
            # create
            dto = ser.to_create_dto(user_id=request.user.id)
            uc = CreateProfessional(self.user_repo, self.pro_repo)
            vm: ProfessionalViewModel = uc.execute(dto)
            status_code = status.HTTP_201_CREATED
            action = "create"
        else:
            # update
            dto = ser.to_update_dto(
                professional_id=pro.id,
                user_id=request.user.id,
                updater_is_staff=request.user.is_staff,
            )
            uc = UpdateProfessional(self.user_repo, self.pro_repo)
            vm: ProfessionalViewModel = uc.execute(dto)
            status_code = status.HTTP_200_OK
            action = "update"

        self.logger.info("ProfessionalUserMeView.patch %s succeeded for user_id=%s", action, request.user.id)
        return Response(ProfessionalOutputSerializer.from_vm(vm).data, status=status_code)


class OnboardingProfessionalView(APIView):
    """
    POST pour créer/mettre à jour le profil pro durant l'onboarding.
    (Même logique que PATCH /professional/me mais en POST pour flows front.)
    """

    permission_classes = [IsAuthenticated]
    logger = logging.getLogger("apps.user.views.OnboardingProfessionalView")

    pro_repo = DjangoProfessionalRepository()
    user_repo = DjangoUserRepository()

    @extend_schema(
        request=ProfessionalUpsertInputSerializer,
        responses={201: OpenApiResponse(ProfessionalOutputSerializer), 200: OpenApiResponse(ProfessionalOutputSerializer)},
        summary="Create or update professional entity during onboarding",
        tags=["Professional Users"],
    )
    def post(self, request):
        self.logger.info("OnboardingProfessionalView.post called", extra={"user_id": request.user.id, "params": request.data})

        pro = self.pro_repo.get_by_user_id(request.user.id)
        ser = ProfessionalUpsertInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        if not pro:
            dto = ser.to_create_dto(user_id=request.user.id)
            uc = CreateProfessional(self.user_repo, self.pro_repo)
            vm: ProfessionalViewModel = uc.execute(dto)
            status_code = status.HTTP_201_CREATED
            action = "create"
        else:
            dto = ser.to_update_dto(
                professional_id=pro.id,
                user_id=request.user.id,
                updater_is_staff=request.user.is_staff,
            )
            uc = UpdateProfessional(self.user_repo, self.pro_repo)
            vm: ProfessionalViewModel = uc.execute(dto)
            status_code = status.HTTP_200_OK
            action = "update"

        self.logger.info(
            "OnboardingProfessionalView.post %s succeeded professional_id=%s user_id=%s",
            action,
            getattr(vm, "id", None),
            request.user.id,
        )
        return Response(ProfessionalOutputSerializer.from_vm(vm).data, status=status_code)
