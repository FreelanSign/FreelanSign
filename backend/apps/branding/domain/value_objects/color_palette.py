# apps/branding/domain/value_objects/color_palette.py
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ColorPalette:
    """
    Value Object representing a color palette for branding.
    All colors are in hexadecimal format (e.g. #000000).
    """

    primary: str
    secondary: str
    background: str
    text_primary: str
    text_secondary: str
    border: str
    highlight: str

    HEX_PATTERN = re.compile(r"^#([0-9a-fA-F]{6})$")

    def __post_init__(self):
        """Validate all colors are valid hex codes."""
        for field_name in self.__dataclass_fields__:
            color = getattr(self, field_name)
            if not self.HEX_PATTERN.match(color):
                raise ValueError(f"Invalid hex color for {field_name}: {color}. Expected format: #RRGGBB")

    @classmethod
    def default(cls) -> ColorPalette:
        """Return the default FreelanSign color palette."""
        return cls(
            primary="#2456c2",
            secondary="#3ccf91",
            background="#f5f7fa",
            text_primary="#222222",
            text_secondary="#666666",
            border="#e5e7eb",
            highlight="#ff8a3d",
        )

    # TODO: Set white for background only and black for text_primary and text_secondary
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "background": self.background,
            "text_primary": self.text_primary,
            "text_secondary": self.text_secondary,
            "border": self.border,
            "highlight": self.highlight,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ColorPalette:
        """Create from dictionary for JSON deserialization."""
        return cls(
            primary=data.get("primary", "#2456c2"),
            secondary=data.get("secondary", "#3ccf91"),
            background=data.get("background", "#f5f7fa"),
            text_primary=data.get("text_primary", "#222222"),
            text_secondary=data.get("text_secondary", "#666666"),
            border=data.get("border", "#e5e7eb"),
            highlight=data.get("highlight", "#ff8a3d"),
        )
