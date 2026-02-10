# apps/branding/domain/entities/brand_theme.py
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from apps.branding.domain.value_objects.color_palette import ColorPalette
from apps.branding.domain.value_objects.spacing_config import SpacingConfig
from apps.branding.domain.value_objects.typography_config import TypographyConfig


@dataclass(frozen=True)
class BrandTheme:
    """
    Domain Entity representing a brand theme for document customization.
    A professional user can have multiple themes but only one active at a time.
    """

    id: uuid.UUID
    account_id: uuid.UUID
    name: str
    is_active: bool
    colors: ColorPalette
    typography: TypographyConfig
    spacing: SpacingConfig
    logo_url: str | None
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        """Validate entity invariants."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Theme name cannot be empty")
        if len(self.name) > 128:
            raise ValueError("Theme name cannot be longer than 128 characters")

    def activate(self) -> None:
        """Activate the theme."""
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate the theme."""
        self.is_active = False

    def update_colors(self, colors: ColorPalette) -> None:
        """Update the color palette."""
        self.colors = colors

    def update_typography(self, typography: TypographyConfig) -> None:
        """Update the typography configuration."""
        self.typography = typography

    def update_spacing(self, spacing: SpacingConfig) -> None:
        """Update the spacing configuration."""
        self.spacing = spacing

    def update_name(self, name: str) -> None:
        """Update the theme name."""
        self.name = name

    def update_logo(self, logo_url: str) -> None:
        """Update the logo URL."""
        self.logo_url = logo_url

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "account_id": str(self.account_id),
            "name": self.name,
            "is_active": self.is_active,
            "colors": self.colors.to_dict(),
            "typography": self.typography.to_dict(),
            "spacing": self.spacing.to_dict(),
            "logo_url": self.logo_url,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
