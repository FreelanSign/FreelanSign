# apps/branding/application/usecases/get_theme_for_rendering.py
from __future__ import annotations

from uuid import UUID

from apps.branding.application.ports.theme_repository import ThemeRepository
from apps.branding.domain.value_objects.color_palette import ColorPalette
from apps.branding.domain.value_objects.spacing_config import SpacingConfig
from apps.branding.domain.value_objects.typography_config import TypographyConfig


class GetThemeForRenderingUseCase:
    """
    Use case for getting a theme for rendering.
    Return default theme if no active theme is found.
    """

    def __init__(self, theme_repository: ThemeRepository):
        self.theme_repository = theme_repository

    def execute(self, *, account_id: UUID) -> dict:
        """
        Get active theme or fallback to default theme.

        Args:
            account_id: The ID of the account to get the theme for.

        Returns:
            A dictionary ready for template rendering with keys :
                - name: str
                - logo_url: str | None
                - colors: dict
                - typography: dict
                - spacing: dict
        """
        theme = self.theme_repository.get_active_theme(account_id=account_id)
        if theme is None:
            # Return default theme
            return self._default_theme()

        # Return theme
        return {
            "name": theme.name,
            "logo_url": theme.logo_url,
            "colors": theme.colors,
            "typography": theme.typography,
            "spacing": theme.spacing,
        }

    @staticmethod
    def _default_theme() -> dict:
        """
        Return the default theme.
        """
        colors = ColorPalette.default()
        typography = TypographyConfig.default()
        spacing = SpacingConfig.default()

        return {
            "name": "FreelanSign",
            "logo_url": None,  # TODO: Add default logo URL
            "colors": colors.to_dict(),
            "typography": typography.to_dict(),
            "spacing": spacing.to_dict(),
        }
