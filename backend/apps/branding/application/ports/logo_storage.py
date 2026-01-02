# apps/branding/application/ports/local_storage.py
from __future__ import annotations

from typing import Protocol


class LogoStorage(Protocol):
    """
    Port for logo file storage.
    Concrete implementations (Django ORM) live in adapters/persistence.
    """

    def save_logo(self, *, file, account_id: str, theme_name: str) -> str:
        """
        Save a logo file and return its path/URL.

        Args:
            file: The logo file to save.
            account_id: The ID of the professional who owns the logo.
            theme_name: The name of the theme that the logo belongs to.

        Returns:
            The path/URL of the saved logo.
        """
        ...

    def delete_logo(self, *, account_id: str, theme_name: str) -> None:
        """
        Delete a logo file.
        Args:
            account_id: The ID of the professional who owns the logo.
            theme_name: The name of the theme that the logo belongs to.
        """
        ...
