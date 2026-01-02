# apps/branding/application/dto/theme_viewmodels.py
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ThemeViewModel:
    """View model for theme presentation."""

    id: int | str
    account_id: int | str
    name: str
    is_active: bool
    colors: dict
    typography: dict
    spacing: dict
    logo_url: str | None
    created_at: str
    updated_at: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "account_id": self.account_id,
            "name": self.name,
            "is_active": self.is_active,
            "colors": self.colors,
            "typography": self.typography,
            "spacing": self.spacing,
            "logo_url": self.logo_url,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class ThemeListItemViewModel:
    """View model for theme list item presentation."""

    id: int | str
    name: str
    is_active: bool
    colors: dict
    logo_url: str | None
    updated_at: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "is_active": self.is_active,
            "colors": self.colors,
            "logo_url": self.logo_url,
            "updated_at": self.updated_at,
        }
