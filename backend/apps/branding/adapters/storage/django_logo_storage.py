# apps/branding/adapters/persistence/django_logo_storage.py
from __future__ import annotations

import os
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage


class DjangoLogoStorage:
    """Django file storage implementation of the LogoStorage."""

    def save_logo(self, *, file, account_id: str, theme_name: str) -> str:
        """
        Save a logo file and return its path.

        Args:
            file: The uploaded file object.
            account_id: The ID of the professional who owns the logo.
            theme_name: The name of the theme that the logo belongs to.

        Returns:
            The relative file path where the logo was saved.
        """
        # Sanitize theme name for file system
        safe_theme_name = self._sanitize_filename(theme_name)

        # Generate file path : branding/logos/YYYY/MM/account_id/theme_name_original.ext
        from datetime import datetime

        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")

        # Get original extension
        original_name = file.name
        ext = Path(original_name).suffix

        # Build file path
        file_path = f"branding/logos/{year}/{month}/{account_id}/{safe_theme_name}{ext}"

        # Save file using Django storage
        saved_path = default_storage.save(file_path, file)
        return saved_path

    def delete_logo(self, *, file_path: str) -> None:
        """
        Delete a logo file.

        Args:
            file_path: The relative file path of the logo to delete.
        """
        if default_storage.exists(file_path):
            default_storage.delete(file_path)

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename for use in a file system.

        Args:
            filename: The filename to sanitize.

        Returns:
            The sanitized filename.
        """
        import re

        # Keep only alphanumeric, underscores, and dashes
        safe = re.sub(r"[^\w\s-]", "", filename)
        # Replace spaces with underscores
        safe = re.sub(r"[-\s]+", "_", safe)
        # Lower case
        safe = safe.lower()
        # Limit length
        return safe[:50]
