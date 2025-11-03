# apps/branding/application/usecases/deactivate_theme.py
from __future__ import annotations

from apps.branding.application.dto.theme_inputs import DeactivateThemeDTO
from apps.branding.application.dto.theme_viewmodels import ThemeViewModel
from apps.branding.application.ports.theme_repository import ThemeRepository
from apps.branding.domain.policies.theme_policy import validate_theme_ownership


class DeactivateThemeUseCase:
    """Use case for deactivating a brand theme."""

    def __init__(self, theme_repository: ThemeRepository):
        self.theme_repository = theme_repository

    def execute(self, dto: DeactivateThemeDTO) -> ThemeViewModel:
        """
        Deactivate a brand theme.

        Args:
            dto: The deactivate theme DTO.

        Returns:
            The deactivated theme view model.
        """
        # 1. Get existing theme
        theme = self.theme_repository.get_by_id(theme_id=dto.theme_id, professional_id=dto.professional_id)

        # 2. Validate ownership
        validate_theme_ownership(theme_professional_id=theme.professional_id, requester_professional_id=dto.professional_id)

        # 3. Deactivate theme via repository
        updated_theme = self.theme_repository.deactivate_theme(theme_id=dto.theme_id, professional_id=dto.professional_id)

        if updated_theme is None:
            updated_theme = self.theme_repository.get_by_id(theme_id=dto.theme_id, professional_id=dto.professional_id)

        # 4. Return view model
        return ThemeViewModel(
            id=updated_theme.id,
            professional_id=theme.professional_id,
            name=updated_theme.name,
            is_active=updated_theme.is_active,
            colors=updated_theme.colors,
            typography=updated_theme.typography,
            spacing=updated_theme.spacing,
            logo_url=updated_theme.logo_url,
            created_at=updated_theme.created_at,
            updated_at=updated_theme.updated_at,
        )
