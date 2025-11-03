# apps/branding/domain/value_objects/spacing_config.py
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SpacingConfig:
    """
    Value Object representing spacing configuration.
    All values are in picels (px).
    """

    page_margin: int  # Marge de la page (ex: 20)
    section_spacing: int  # Espacement entre les sections (ex: 20)
    element_padding: int  # Padding des éléments (ex: 20)

    def __post_init__(self):
        """Validate specific spacing configuration."""
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            if not isinstance(value, int) or not (0 <= value <= 100):
                raise ValueError(f"Invalid spacing value for {field_name}: {value}. Expected int between 0 and 100.")

    @classmethod
    def default(cls) -> SpacingConfig:
        """Return the default FreelanSign spacing configuration."""
        return cls(
            page_margin=40,
            section_spacing=12,
            element_padding=8,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "page_margin": self.page_margin,
            "section_spacing": self.section_spacing,
            "element_padding": self.element_padding,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SpacingConfig:
        """Create from dictionary for JSON deserialization."""
        return cls(
            page_margin=data["page_margin"],
            section_spacing=data["section_spacing"],
            element_padding=data["element_padding"],
        )
