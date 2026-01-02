# apps/branding/application/usecases/activate_theme.py
from __future__ import annotations

from apps.branding.application.dto.theme_inputs import ActivateThemeDTO
from apps.branding.application.dto.theme_viewmodels import ThemeViewModel
from apps.branding.application.ports.theme_repository import ThemeRepository
from apps.branding.domain.policies.theme_policy import validate_theme_ownership


class ActivateThemeUseCase:
    """Use case for activating a brand theme."""

    def __init__(self, theme_repository: ThemeRepository):
        self.theme_repository = theme_repository

    def execute(self, dto: ActivateThemeDTO) -> ThemeViewModel:
        """
        Activate a brand theme.

        Args:
            dto: The activate theme DTO.

        Returns:
            The activated theme view model.

        Raises:
            ThemeOwnershipError: If the theme is not owned by the professional.
            ActiveThemeConflictError: If the theme is already active.
            RepositoryError: If the theme activation fails.
        """
        # 1. Get existing theme
        theme = self.theme_repository.get_by_id(theme_id=dto.theme_id, account_id=dto.account_id)

        # 2. Validate ownership
        validate_theme_ownership(theme_account_id=theme.account_id, requester_account_id=dto.account_id)

        # 3. Deactivate all other active themes
        self.theme_repository.deactivate_all_themes(account_id=dto.account_id)

        # 4. Activate theme via repository
        updated_theme = self.theme_repository.activate_theme(theme_id=dto.theme_id, account_id=dto.account_id)

        # 5. Return view model
        return ThemeViewModel(
            id=updated_theme.id,
            account_id=updated_theme.account_id,
            name=updated_theme.name,
            is_active=updated_theme.is_active,
            colors=updated_theme.colors,
            typography=updated_theme.typography,
            spacing=updated_theme.spacing,
            logo_url=updated_theme.logo_url,
            created_at=updated_theme.created_at,
            updated_at=updated_theme.updated_at,
        )
