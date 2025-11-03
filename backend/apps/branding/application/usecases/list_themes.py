# apps/branding/application/usecases/list_themes.py
from __future__ import annotations

from uuid import UUID

from apps.branding.application.dto.theme_viewmodels import ThemeListItemViewModel
from apps.branding.application.ports.theme_repository import ThemeRepository


class ListThemesUseCase:
    """Use case for listing all themes for a professional."""

    def __init__(self, theme_repository: ThemeRepository):
        self.theme_repository = theme_repository

    def execute(self, professional_id: UUID) -> list[ThemeListItemViewModel]:
        """
        List all themes for a professional.

        Args:
            professional_id: The ID of the professional to list the themes for.

        Returns:
            A list of theme list item view models.
        """
        themes = self.theme_repository.list_themes(professional_id=professional_id)
        return [
            ThemeListItemViewModel(
                id=theme.id,
                name=theme.name,
                is_active=theme.is_active,
                logo_url=theme.logo_url,
                updated_at=theme.updated_at.isoformat(),
            )
            for theme in themes
        ]
