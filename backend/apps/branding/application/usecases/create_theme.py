# apps/branding/application/usecases/create_theme.py
from __future__ import annotations

import uuid

from apps.branding.application.dto.theme_inputs import CreateThemeDTO
from apps.branding.application.dto.theme_viewmodels import ThemeViewModel
from apps.branding.application.errors import ThemeValidationError
from apps.branding.application.ports.logo_storage import LogoStorage
from apps.branding.application.ports.theme_repository import ThemeRepository
from apps.branding.domain.policies.theme_policy import validate_single_active_theme
from apps.branding.domain.services.theme_validator import ThemeValidator
from apps.branding.domain.value_objects.color_palette import ColorPalette
from apps.branding.domain.value_objects.spacing_config import SpacingConfig
from apps.branding.domain.value_objects.typography_config import TypographyConfig


class CreateThemeUseCase:
    """Use case for creating a new brand theme."""

    def __init__(
        self,
        theme_repository: ThemeRepository,
        logo_storage: LogoStorage,
    ):
        self.theme_repository = theme_repository
        self.logo_storage = logo_storage

    def execute(self, dto: CreateThemeDTO) -> ThemeViewModel:
        """
        Create a new theme.

        Args:
            dto: The create theme DTO.

        Returns:
            The created theme view model.

        Raises:
            ThemeValidationError: If the theme validation fails.
            ActiveThemeConflictError: If there is already an active theme for the professional.
            RepositoryError: If the theme creation fails.
        """
        # 1. Validate Value Objects
        try:
            colors = ColorPalette.from_dict(dto.colors)
            typography = TypographyConfig.from_dict(dto.typography)
            spacing = SpacingConfig.from_dict(dto.spacing)
        except ValueError as e:
            raise ThemeValidationError(f"Invalid theme configuration: {e}") from e

        # 2. Validate Theme
        ThemeValidator.validate_theme(dto.name, colors, typography, spacing)

        # 3. Check active theme policy
        if dto.is_active:
            existing_themes = self.theme_repository.list_themes(account_id=dto.account_id)
            active_count = sum(1 for t in existing_themes if t.is_active)
            validate_single_active_theme(active_count, is_activating=True)

        # 4. Handle logo upload
        logo_path = None
        if dto.logo_file:
            logo_path = self.logo_storage.save_logo(
                file=dto.logo_file,
                account_id=str(dto.account_id),
                theme_name=dto.name,
            )

        # 5. Create theme via repository
        theme = self.theme_repository.create_theme(
            account_id=dto.account_id,
            name=dto.name,
            is_active=dto.is_active,
            colors=colors.to_dict(),
            typography=typography.to_dict(),
            spacing=spacing.to_dict(),
            logo_path=logo_path,
        )

        # 6. Return view model
        return self._to_viewmodel(theme)

    def _to_viewmodel(self, theme) -> ThemeViewModel:
        """Convert repository result to view model."""
        return ThemeViewModel(
            id=theme.id,
            account_id=theme.account_id,
            name=theme.name,
            is_active=theme.is_active,
            colors=theme.colors,
            typography=theme.typography,
            spacing=theme.spacing,
            logo_url=theme.logo_url,
            created_at=theme.created_at.isoformat(),
            updated_at=theme.updated_at.isoformat(),
        )
