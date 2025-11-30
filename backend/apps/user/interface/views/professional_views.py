# apps/user/interface/views/professional_views.py
from __future__ import annotations

import logging

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Adapters
from apps.user.adapters.persistence.django_user_repository import (
    DjangoProfessionalRepository,
    DjangoUserRepository,
)

# DTOs / VMs
from apps.user.application.dto.user_viewmodels import ProfessionalViewModel
from apps.user.application.usecases.create_professional import CreateProfessional
from apps.user.application.usecases.update_professional import UpdateProfessional

# Interface serializers
from apps.user.interface.serializers import (
    ProfessionalOutputSerializer,
    ProfessionalUpsertInputSerializer,
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
