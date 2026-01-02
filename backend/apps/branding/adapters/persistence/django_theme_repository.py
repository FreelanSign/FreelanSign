# apps/branding/adapters/persistence/django_theme_repository.py
from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist

from apps.branding.application.errors import ThemeNotFoundError, ThemeOwnershipError
from apps.branding.models import BrandTheme


class DjangoThemeRepository:
    """Django ORM implementation of the ThemeRepository."""

    def get_by_id(self, *, theme_id: int | str, account_id: int | str) -> BrandTheme:
        """
        Get a theme by ID, ensuring it belongs to the specified account.

        Args:
            theme_id: The ID of the theme to get.
            account_id: The ID of the account who owns the theme.

        Returns:
            The theme if found, otherwise None.

        Raises:
            ThemeNotFoundError: If the theme is not found.
            ThemeOwnershipError: If the theme is not owned by the account.
        """
        try:
            theme = BrandTheme.objects.get(id=theme_id)
        except ObjectDoesNotExist:
            raise ThemeNotFoundError(f"Theme {theme_id} not found")

        if theme.account_id != account_id:
            raise ThemeOwnershipError(f"Theme {theme_id} does not belong to account {account_id}")

        return theme

    def get_active_theme(self, *, account_id) -> BrandTheme | None:
        """
        Get the active theme for an account.

        Args:
            account_id: The ID of the account to get the active theme for.

        Returns:
            The active theme if found, otherwise None.
        """
        try:
            return BrandTheme.objects.get(account_id=account_id, is_active=True)
        except ObjectDoesNotExist:
            return None

    def list_themes(self, *, account_id) -> list[BrandTheme]:
        """
        List all themes for an account.

        Args:
            account_id: The ID of the account to list the themes for.

        Returns:
            A list of themes.
        """
        return BrandTheme.objects.filter(account_id=account_id)

    def create_theme(
        self,
        *,
        account_id,
        name: str,
        is_active: bool,
        colors: dict,
        typography: dict,
        spacing: dict,
        logo_path: str | None = None,
    ) -> BrandTheme:
        """
        Create a new theme for an account.

        Args:
            account_id: The ID of the account to create the theme for.
            name: The name of the theme.
            is_active: Whether the theme is active.
            colors: The color palette of the theme.
            typography: The typography configuration of the theme.
            spacing: The spacing configuration of the theme.
            logo_path: The path to the logo image file.

        Returns:
            The created theme.
        """
        theme = BrandTheme.objects.create(
            account_id=account_id,
            name=name,
            is_active=is_active,
            colors=colors,
            typography=typography,
            spacing=spacing,
        )

        # Handle logo separately to avoid race conditions
        if logo_path:
            theme.logo = logo_path
            theme.save(update_fields=["logo"])

        return theme

    def update_theme(
        self,
        *,
        theme_id: int | str,
        account_id,
        name: str,
        is_active: bool,
        colors: dict,
        typography: dict,
        spacing: dict,
        logo_path: str | None = None,
    ) -> BrandTheme:
        """
        Update an existing theme for an account.

        Args:
            theme_id: The ID of the theme to update.
            account_id: The ID of the account who owns the theme.
            name: The name of the theme.
            is_active: Whether the theme is active.
            colors: The color palette of the theme.
            typography: The typography configuration of the theme.
            spacing: The spacing configuration of the theme.
            logo_path: The path to the logo image file.

        Returns:
            The updated theme.

        Raises:
            ThemeNotFoundError: If the theme is not found.
            ThemeOwnershipError: If the theme is not owned by the account.
        """
        theme = self.get_by_id(theme_id=theme_id, account_id=account_id)

        updated_fields = []
        if name is not None:
            theme.name = name
            updated_fields.append("name")
        if is_active is not None:
            theme.is_active = is_active
            updated_fields.append("is_active")
        if colors is not None:
            theme.colors = colors
            updated_fields.append("colors")
        if typography is not None:
            theme.typography = typography
            updated_fields.append("typography")
        if spacing is not None:
            theme.spacing = spacing
            updated_fields.append("spacing")
        if logo_path is not None:
            theme.logo = logo_path
            updated_fields.append("logo")

        if updated_fields:
            updated_fields.append("updated_at")
            theme.save(update_fields=updated_fields)

        return theme

    def delete_theme(self, *, theme_id: int | str, account_id) -> None:
        """
        Delete a theme for an account.

        Args:
            theme_id: The ID of the theme to delete.
            account_id: The ID of the account who owns the theme.

        Raises:
            ThemeNotFoundError: If the theme is not found.
            ThemeOwnershipError: If the theme is not owned by the account.
        """
        theme = self.get_by_id(theme_id=theme_id, account_id=account_id)
        theme.delete()

        # Delete logo if exists
        if theme.logo:
            try:
                self.logo_storage.delete_logo(logo_url=theme.logo_url)
            except Exception:
                # Log error but continue
                pass

    def activate_theme(self, *, theme_id: int | str, account_id: int | str) -> BrandTheme:
        """
        Activate a theme for an account.

        Args:
            theme_id: The ID of the theme to activate.
            account_id: The ID of the account who owns the theme.

        Returns:
            The activated theme.
        """
        BrandTheme.objects.filter(account_id=account_id, is_active=True).update(is_active=False)
        BrandTheme.objects.filter(id=theme_id, account_id=account_id).update(is_active=True)
        return BrandTheme.objects.get(id=theme_id, account_id=account_id)

    def deactivate_theme(self, *, theme_id: int | str, account_id: int | str) -> BrandTheme:
        """
        Deactivate a theme for an account.

        Args:
            theme_id: The ID of the theme to deactivate.
            account_id: The ID of the account who owns the theme.

        Returns:
            The deactivated theme.
        """
        obj = BrandTheme.objects.get(id=theme_id, account_id=account_id)
        obj.is_active = False
        obj.save(update_fields=["is_active", "updated_at"])
        return obj

    def deactivate_all_themes(self, *, account_id: int | str) -> None:
        """
        Deactivate all themes for an account.

        Args:
            account_id: The ID of the account who owns the themes.
        """
        BrandTheme.objects.filter(account_id=account_id, is_active=True).update(is_active=False)
