# apps/branding/application/errors.py
from __future__ import annotations


class BrandingError(Exception):
    """Base exception for branding errors."""

    pass


class ThemeNotFoundError(BrandingError):
    """Raised when a theme is not found."""

    pass


class ThemeOwnershipError(BrandingError):
    """Raised when a user tries to access a theme they don't own."""

    pass


class ThemeValidationError(BrandingError):
    """Raised when theme validation fails."""

    pass


class ActiveThemeConflictError(BrandingError):
    """Raised when trying to activate multiple themes."""

    pass
