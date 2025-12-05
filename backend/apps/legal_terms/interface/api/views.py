"""
DRF views for legal terms API endpoints.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.legal_terms.adapters.persistence.django_attached_terms_repository import (
    DjangoAttachedTermsRepository,
)
from apps.legal_terms.adapters.persistence.django_legal_profile_repository import (
    DjangoLegalProfileRepository,
)
from apps.legal_terms.adapters.persistence.django_legal_template_repository import (
    DjangoLegalTemplateRepository,
)
from apps.legal_terms.adapters.rendering.template_renderer import TemplateRenderer
from apps.legal_terms.adapters.services.account_service_adapter import (
    AccountServiceAdapter,
)
from apps.legal_terms.application.dtos.legal_profile_dto import (
    LegalProfileDTO,
    UpdateClauseInput,
)
from apps.legal_terms.application.dtos.preview_dto import PreviewLegalTermsInput
from apps.legal_terms.application.use_cases.preview_legal_terms import (
    PreviewLegalTermsUseCase,
)
from apps.legal_terms.application.use_cases.update_legal_profile import (
    UpdateLegalProfileUseCase,
)
from apps.legal_terms.domain.exceptions import (
    ClauseNotFoundError,
    MandatoryClauseModificationError,
    MissingTemplateVariablesError,
    NoActiveTemplateError,
    ProfileNotFoundError,
)
from apps.legal_terms.domain.services.legal_terms_assembler import LegalTermsAssembler
from apps.legal_terms.interface.api.serializers import (
    LegalProfileSerializer,
    PreviewLegalTermsOutputSerializer,
    UpdateLegalProfileInputSerializer,
)
from apps.user.interface.permissions.account_permissions import (
    HasAccountContext,
    IsAccountOwner,
)


class LegalProfileView(APIView):
    """
    API endpoint for managing legal profile.

    GET /api/legal-terms/profile/
    - Returns legal profile for current account

    PATCH /api/legal-terms/profile/
    - Updates legal profile clause overrides
    """

    permission_classes = [IsAuthenticated, HasAccountContext, IsAccountOwner]

    def _get_account_id(self, request) -> str:
        """Extract account ID from request."""
        # Le middleware HasAccountContext place déjà l'account dans request.account.
        account = getattr(request, "account", None)
        if account is not None:
            return str(account.id)

        # Fallback de sécurité si pour une raison quelconque le middleware n'a
        # pas injecté l'account : on prend le premier account actif de l'utilisateur.
        account = request.user.accounts.filter(is_active=True).first()
        if account:
            return str(account.id)

        # Aucun account disponible : mieux vaut une erreur explicite qu'un AttributeError.
        raise ValueError("No active account found for authenticated user")

    def _build_update_use_case(self) -> UpdateLegalProfileUseCase:
        """Build UpdateLegalProfileUseCase with dependencies."""
        profile_repo = DjangoLegalProfileRepository()
        template_repo = DjangoLegalTemplateRepository()

        return UpdateLegalProfileUseCase(
            profile_repository=profile_repo,
            template_repository=template_repo,
        )

    def get(self, request):
        """Get legal profile for current account."""
        try:
            account_id = self._get_account_id(request)
            profile_repo = DjangoLegalProfileRepository()
            template_repo = DjangoLegalTemplateRepository()

            # Get or create profile
            template = template_repo.get_active_for_jurisdiction("FR")
            if not template:
                return Response(
                    {"error": "No active legal template found"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            profile = profile_repo.get_or_create_for_account(
                account_id=account_id,
                template_id=template.id,
                template_version=template.version,
            )

            # Convert to DTO and serialize
            profile_dto = LegalProfileDTO(
                id=profile.id,
                account_id=profile.account_id,
                template_id=profile.template_id,
                template_version=profile.template_version,
                clause_overrides=profile.clause_overrides,
            )

            serializer = LegalProfileSerializer(profile_dto)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request):
        """Update legal profile clause overrides."""
        try:
            account_id = self._get_account_id(request)

            # Validate input
            serializer = UpdateLegalProfileInputSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Convert to DTOs
            update_inputs = [
                UpdateClauseInput(
                    identifier=update["identifier"],
                    is_active=update.get("is_active"),
                    custom_title=update.get("custom_title"),
                    custom_body=update.get("custom_body"),
                    custom_order=update.get("custom_order"),
                )
                for update in serializer.validated_data["updates"]
            ]

            # Execute use case
            use_case = self._build_update_use_case()
            updated_profile = use_case.execute(account_id, update_inputs)

            # Serialize response
            response_serializer = LegalProfileSerializer(updated_profile)
            return Response(response_serializer.data)

        except ProfileNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ClauseNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except MandatoryClauseModificationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LegalTermsPreviewView(APIView):
    """
    API endpoint for previewing legal terms.

    GET /api/legal-terms/preview/
    - Returns rendered preview of legal terms for current account
    """

    permission_classes = [IsAuthenticated, HasAccountContext, IsAccountOwner]

    def _get_account_id(self, request) -> str:
        """Extract account ID from request."""
        account = getattr(request, "account", None)
        if account is not None:
            return str(account.id)

        account = request.user.accounts.filter(is_active=True).first()
        if account:
            return str(account.id)

        raise ValueError("No active account found for authenticated user")

    def _build_preview_use_case(self) -> PreviewLegalTermsUseCase:
        """Build PreviewLegalTermsUseCase with dependencies."""
        profile_repo = DjangoLegalProfileRepository()
        template_repo = DjangoLegalTemplateRepository()
        account_service = AccountServiceAdapter()
        renderer = TemplateRenderer()
        assembler = LegalTermsAssembler()

        return PreviewLegalTermsUseCase(
            profile_repository=profile_repo,
            template_repository=template_repo,
            account_service=account_service,
            template_renderer=renderer,
            assembler=assembler,
        )

    def get(self, request):
        """Preview legal terms for current account."""
        try:
            account_id = self._get_account_id(request)

            # Build use case and execute
            use_case = self._build_preview_use_case()
            input_dto = PreviewLegalTermsInput(account_id=account_id)
            output = use_case.execute(input_dto)

            # Serialize response
            serializer = PreviewLegalTermsOutputSerializer(output)
            return Response(serializer.data)

        except NoActiveTemplateError as e:
            return Response(
                {"error": f"No active legal template found: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except MissingTemplateVariablesError as e:
            return Response(
                {"error": f"Missing required legal information: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
