# apps/branding/application/usecases/update_theme.py
from __future__ import annotations

from apps.branding.application.dto.theme_inputs import UpdateThemeDTO
from apps.branding.application.dto.theme_viewmodels import ThemeViewModel
from apps.branding.application.errors import ThemeValidationError
from apps.branding.application.ports.logo_storage import LogoStorage
from apps.branding.application.ports.theme_repository import ThemeRepository
from apps.branding.domain.policies.theme_policy import validate_single_active_theme, validate_theme_ownership
from apps.branding.domain.services.theme_validator import ThemeValidator
from apps.branding.domain.value_objects.color_palette import ColorPalette
from apps.branding.domain.value_objects.spacing_config import SpacingConfig
from apps.branding.domain.value_objects.typography_config import TypographyConfig


class UpdateThemeUseCase:
    """Use case for updating an existing brand theme."""

    def __init__(self, theme_repository: ThemeRepository, logo_storage: LogoStorage):
        self.theme_repository = theme_repository
        self.logo_storage = logo_storage

    def execute(self, dto: UpdateThemeDTO) -> ThemeViewModel:
        """
        Update an existing theme.

        Args:
            dto: The update theme DTO.

        Returns:
            The updated theme view model.

        Raises:
            ThemeValidationError: If the theme validation fails.
            ThemeOwnershipError: If the theme is not owned by the professional.
            RepositoryError: If the theme update fails.
        """
        # 1. Get existing theme
        theme = self.theme_repository.get_by_id(theme_id=dto.theme_id, account_id=dto.account_id)

        # 2. Validate ownership
        validate_theme_ownership(theme_account_id=theme.account_id, requester_account_id=dto.account_id)

        # 3. Validate new values if provided
        if dto.colors:
            try:
                colors = ColorPalette.from_dict(dto.colors)
            except (ValueError, KeyError) as e:
                raise ThemeValidationError(f"Invalid color configuration: {e}") from e

        if dto.typography:
            try:
                typography = TypographyConfig.from_dict(dto.typography)
            except (ValueError, KeyError) as e:
                raise ThemeValidationError(f"Invalid typography configuration: {e}") from e

        if dto.spacing:
            try:
                spacing = SpacingConfig.from_dict(dto.spacing)
            except (ValueError, KeyError) as e:
                raise ThemeValidationError(f"Invalid spacing configuration: {e}") from e

        # 4. Check active theme policy
        if dto.is_active is not None and dto.is_active and not theme.is_active:
            existing_themes = self.theme_repository.list_themes(account_id=dto.account_id)
            active_count = sum(1 for t in existing_themes if t.is_active and t.id != dto.theme_id)
            validate_single_active_theme(active_count, is_activating=True)

        # 5. Handle logo upload
        logo_path = None
        if dto.logo_file:
            # Delete old logo if exists
            if theme.logo_url:
                try:
                    self.logo_storage.delete_logo(logo_url=theme.logo_url)
                except Exception:
                    # Log error but continue
                    pass

            # Upload new logo
            logo_path = self.logo_storage.save_logo(
                file=dto.logo_file,
                account_id=str(dto.account_id),
                theme_name=theme.name,
            )

        # 6. Update theme via repository
        updated_theme = self.theme_repository.update_theme(
            theme_id=dto.theme_id,
            account_id=dto.account_id,
            name=dto.name,
            is_active=dto.is_active,
            colors=colors.to_dict(),
            typography=typography.to_dict(),
            spacing=spacing.to_dict(),
            logo_path=logo_path,
        )

        # 7. Return view model
        return self._to_viewmodel(updated_theme)

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
