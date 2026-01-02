# apps/branding/application/usecases/get_active_theme.py
from __future__ import annotations

from apps.branding.application.dto.theme_viewmodels import ThemeViewModel
from apps.branding.application.ports.theme_repository import ThemeRepository


class GetActiveThemeUseCase:
    """Use case for getting the active theme for a professional."""

    def __init__(self, theme_repository: ThemeRepository):
        self.theme_repository = theme_repository

    def execute(self, account_id: int | str) -> ThemeViewModel | None:
        """
        Get the active theme for a professional.

        Args:
            account_id: The ID of the professional to get the active theme for.

        Returns:
            The active theme view model if found, otherwise None.

        Raises:
            RepositoryError: If the theme retrieval fails.
        """
        theme = self.theme_repository.get_active_theme(account_id=account_id)
        if theme is None:
            return None

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
