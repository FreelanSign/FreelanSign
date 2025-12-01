from __future__ import annotations

from uuid import UUID

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.branding.adapters.persistence.django_theme_repository import DjangoThemeRepository
from apps.branding.adapters.storage.django_logo_storage import DjangoLogoStorage
from apps.branding.application.dto.theme_inputs import (
    ActivateThemeDTO,
    CreateThemeDTO,
    DeactivateThemeDTO,
    DeleteThemeDTO,
    GetThemeDTO,
    UpdateThemeDTO,
)
from apps.branding.application.errors import (
    ActiveThemeConflictError,
    ThemeNotFoundError,
    ThemeOwnershipError,
    ThemeValidationError,
)
from apps.branding.application.usecases.activate_theme import ActivateThemeUseCase
from apps.branding.application.usecases.create_theme import CreateThemeUseCase
from apps.branding.application.usecases.deactivate_theme import DeactivateThemeUseCase
from apps.branding.application.usecases.delete_theme import DeleteThemeUseCase
from apps.branding.application.usecases.get_active_theme import GetActiveThemeUseCase
from apps.branding.application.usecases.list_themes import ListThemesUseCase
from apps.branding.application.usecases.update_theme import UpdateThemeUseCase
from apps.branding.interface.serializers import (
    CreateThemeSerializer,
    ThemeListItemSerializer,
    ThemeSerializer,
    UpdateThemeSerializer,
)
from apps.user.interface.permissions.account_permissions import HasAccountContext


class ThemeListCreateView(APIView):
    """
    GET: List all themes for the authenticated user.
    POST: Create a new theme.
    """

    permission_classes = [IsAuthenticated, HasAccountContext]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    @extend_schema(
        summary="List all themes for the authenticated user",
        responses={200: ThemeListItemSerializer(many=True)},
        tags=["Branding"],
    )
    def get(self, request):
        """List all themes for the authenticated user."""
        professional_id = request.account.id  # Phase 5.3: account context

        # Initialize dependencies
        repository = DjangoThemeRepository()
        use_case = ListThemesUseCase(theme_repository=repository)

        # Execute use case
        themes = use_case.execute(professional_id=professional_id)

        # Serialize and return
        serializer = ThemeListItemSerializer([t.to_dict() for t in themes], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create a new theme",
        request=CreateThemeSerializer,
        responses={201: ThemeSerializer},
        tags=["Branding"],
    )
    def post(self, request):
        """Create a new theme."""
        serializer = CreateThemeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        professional_id = request.account.id  # Phase 5.3: account context

        # Initialize dependencies
        repository = DjangoThemeRepository()
        storage = DjangoLogoStorage()
        use_case = CreateThemeUseCase(theme_repository=repository, logo_storage=storage)

        # Prepare DTO
        dto = CreateThemeDTO(
            professional_id=professional_id,
            name=serializer.validated_data["name"],
            is_active=serializer.validated_data.get("is_active", False),
            colors=serializer.validated_data["colors"],
            typography=serializer.validated_data["typography"],
            spacing=serializer.validated_data["spacing"],
            logo_file=serializer.validated_data.get("logo"),
        )

        try:
            # Execute use case
            theme_vm = use_case.execute(dto)

            # Serialize and return
            response_serializer = ThemeSerializer(theme_vm.to_dict())
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except ThemeValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ActiveThemeConflictError as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)


@extend_schema_view(
    get=extend_schema(summary="Retrieve a specific theme", responses={200: ThemeSerializer}, tags=["Branding"]),
    patch=extend_schema(
        summary="Update a specific theme",
        request=UpdateThemeSerializer,
        responses={200: ThemeSerializer},
        tags=["Branding"],
    ),
    delete=extend_schema(summary="Delete a specific theme", responses={204: None}, tags=["Branding"]),
)
class ThemeDetailView(APIView):
    """
    GET: Retrieve a specific theme.
    PUT/PATCH: Update a specific theme.
    DELETE: Delete a specific theme.
    """

    permission_classes = [IsAuthenticated, HasAccountContext]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request, theme_id):
        """Retrieve a specific theme."""
        professional_id = request.account.id  # Phase 5.3: account context

        # Initialize dependencies
        repository = DjangoThemeRepository()

        try:
            # Convert theme_id to UUID
            theme_uuid = UUID(theme_id) if isinstance(theme_id, str) else theme_id
            theme = repository.get_by_id(theme_id=theme_uuid, professional_id=professional_id)

            # Manual conversion to dict for serialization
            theme_dict = {
                "id": str(theme.id),
                "professional_id": str(theme.professional_id),
                "name": theme.name,
                "is_active": theme.is_active,
                "colors": theme.colors,
                "typography": theme.typography,
                "spacing": theme.spacing,
                "logo_url": theme.logo_url,
                "created_at": theme.created_at.isoformat(),
                "updated_at": theme.updated_at.isoformat(),
            }

            serializer = ThemeSerializer(theme_dict)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"error": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST)
        except ThemeNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ThemeOwnershipError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, theme_id):
        """Update a specific theme (partial update)."""
        serializer = UpdateThemeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        professional_id = request.account.id  # Phase 5.3: account context

        # Initialize dependencies
        repository = DjangoThemeRepository()
        storage = DjangoLogoStorage()
        use_case = UpdateThemeUseCase(theme_repository=repository, logo_storage=storage)

        try:
            # Convert theme_id to UUID if it's a string
            theme_uuid = UUID(theme_id) if isinstance(theme_id, str) else theme_id

            # Prepare DTO
            dto = UpdateThemeDTO(
                theme_id=theme_uuid,
                professional_id=professional_id,
                name=serializer.validated_data.get("name"),
                is_active=serializer.validated_data.get("is_active"),
                colors=serializer.validated_data.get("colors"),
                typography=serializer.validated_data.get("typography"),
                spacing=serializer.validated_data.get("spacing"),
                logo_file=serializer.validated_data.get("logo"),
            )

            # Execute use case
            theme_vm = use_case.execute(dto)

            # Serialize and return
            response_serializer = ThemeSerializer(theme_vm.to_dict())
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"error": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST)
        except ThemeNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ThemeOwnershipError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ThemeValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, theme_id):
        """Delete a specific theme."""
        professional_id = request.account.id  # Phase 5.3: account context

        # Initialize dependencies
        repository = DjangoThemeRepository()
        storage = DjangoLogoStorage()
        use_case = DeleteThemeUseCase(theme_repository=repository, logo_storage=storage)

        try:
            # Convert theme_id to UUID if it's a string
            theme_uuid = UUID(theme_id) if isinstance(theme_id, str) else theme_id

            # Prepare DTO
            dto = DeleteThemeDTO(theme_id=theme_uuid, professional_id=professional_id)

            # Execute use case
            use_case.execute(dto)
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ValueError:
            return Response({"error": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST)
        except ThemeNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ThemeOwnershipError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ActiveThemeConflictError as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)


@extend_schema_view(
    get=extend_schema(
        summary="Get the active theme for the authenticated user", responses={200: ThemeSerializer}, tags=["Branding"]
    ),
)
class ActiveThemeView(APIView):
    """
    GET: Get the active theme for the authenticated user.
    """

    permission_classes = [IsAuthenticated, HasAccountContext]

    def get(self, request):
        """Get the active theme for the authenticated user."""
        professional_id = request.account.id  # Phase 5.3: account context

        # Initialize dependencies
        repository = DjangoThemeRepository()
        use_case = GetActiveThemeUseCase(theme_repository=repository)

        # Execute use case
        theme_vm = use_case.execute(professional_id=professional_id)

        if theme_vm is None:
            return Response({"message": "No active theme found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize and return
        serializer = ThemeSerializer(theme_vm.to_dict())
        return Response(serializer.data, status=status.HTTP_200_OK)


class ActivateThemeView(APIView):
    """
    POST: Activate a specific theme (and deactivate others).
    """

    permission_classes = [IsAuthenticated, HasAccountContext]

    @extend_schema(
        summary="Activate a specific theme",
        responses={200: ThemeSerializer},
        tags=["Branding"],
    )
    def post(self, request, theme_id):
        """Activate a specific theme."""
        professional_id = request.account.id  # Phase 5.3: account context

        # Initialize dependencies
        repository = DjangoThemeRepository()
        use_case = ActivateThemeUseCase(theme_repository=repository)

        try:
            # Convert theme_id to UUID if it's a string
            theme_uuid = UUID(theme_id) if isinstance(theme_id, str) else theme_id

            # Prepare DTO
            dto = ActivateThemeDTO(theme_id=theme_uuid, professional_id=professional_id)

            # Execute use case
            theme_vm = use_case.execute(dto)

            # Serialize and return
            serializer = ThemeSerializer(theme_vm.to_dict())
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"error": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST)
        except ThemeNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ThemeOwnershipError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)


class DeactivateThemeView(APIView):
    """
    POST: Deactivate a specific theme.
    """

    permission_classes = [IsAuthenticated, HasAccountContext]

    @extend_schema(
        summary="Deactivate a specific theme",
        responses={200: ThemeSerializer},
        tags=["Branding"],
    )
    def post(self, request, theme_id):
        """Deactivate a specific theme."""
        professional_id = request.account.id  # Phase 5.3: account context

        # Initialize dependencies
        repository = DjangoThemeRepository()
        use_case = DeactivateThemeUseCase(theme_repository=repository)

        try:
            # Convert theme_id to UUID if it's a string
            theme_uuid = UUID(theme_id) if isinstance(theme_id, str) else theme_id

            # Prepare DTO
            dto = DeactivateThemeDTO(theme_id=theme_uuid, professional_id=professional_id)

            # Execute use case
            theme_vm = use_case.execute(dto)

            # Serialize and return
            serializer = ThemeSerializer(theme_vm.to_dict())
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError:
            return Response({"error": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST)
        except ThemeNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ThemeOwnershipError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
