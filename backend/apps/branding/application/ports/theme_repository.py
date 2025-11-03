# apps/branding/application/ports/theme_repository.py
from __future__ import annotations

from typing import Any, Protocol


class ThemeRepository(Protocol):
    """
    Port for theme persistence.
    Concrete implementations (Django ORM) live in adapters/persistence.
    """

    def get_by_id(self, *, theme_id: int | str, professional_id) -> Any:
        """
        Get a theme by ID, ensuring it belongs to the specified professional.

        Args:
            theme_id: The ID of the theme to get.
            professional_id: The ID of the professional who owns the theme.

        Returns:
            The theme if found, otherwise None.
        """
        ...

    def get_active_theme(self, *, professional_id) -> list[Any]:
        """
        Get the active theme for a professional.

        Args:
            professional_id: The ID of the professional to get the active theme for.

        Returns:
            The active theme if found, otherwise None.
        """
        ...

    def create_theme(
        self,
        *,
        professional_id,
        name: str,
        is_active: bool,
        colors: dict,
        typography: dict,
        spacing: dict,
        logo_path: str | None = None,
    ) -> Any:
        """
        Create a new theme for a professional.

        Args:
            professional_id: The ID of the professional to create the theme for.
            name: The name of the theme.
            is_active: Whether the theme is active.
            colors: The color palette of the theme.
            typography: The typography configuration of the theme.
            spacing: The spacing configuration of the theme.
            logo_path: The path to the logo image file.

        Returns:
            The created theme.
        """
        ...

    def update_theme(
        self,
        *,
        theme_id: int | str,
        professional_id,
        name: str | None = None,
        is_active: bool | None = None,
        colors: dict | None = None,
        typography: dict | None = None,
        spacing: dict | None = None,
        logo_path: str | None = None,
    ) -> Any:
        """
        Update an existing theme for a professional.

        Args:
            theme_id: The ID of the theme to update.
            professional_id: The ID of the professional who owns the theme.
            name: The name of the theme.
            is_active: Whether the theme is active.
            colors: The color palette of the theme.
            typography: The typography configuration of the theme.
            spacing: The spacing configuration of the theme.
            logo_path: The path to the logo image file.

        Returns:
            The updated theme.
        """
        ...

    def delete_theme(self, *, theme_id: int | str, professional_id) -> None:
        """
        Delete a theme.

        Args:
            theme_id: The theme UUID.
            professional_id: The professional UUID (for ownership check).
        """
        ...

    def deactivate_all_themes(self, *, professional_id) -> None:
        """
        Deactivate all themes for a professional.

        Args:
            professional_id: The professional UUID.
        """
        ...

    def deactivate_theme(self, *, theme_id: int | str, professional_id) -> None:
        """
        Deactivate a theme.

        Args:
            theme_id: The theme UUID.
            professional_id: The professional UUID (for ownership check).
        """
        ...

    def activate_theme(self, *, theme_id: int | str, professional_id) -> None:
        """
        Activate a theme.

        Args:
            theme_id: The theme UUID.
            professional_id: The professional UUID (for ownership check).

        Returns:
            The activated theme.
        """
        ...
