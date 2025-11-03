# apps/branding/domain/value_objects/typography_config.py
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TypographyConfig:
    """
    Value Object representing typography configuration.
    Font sizes are in picels (px).
    """

    heading_font: str  # Police des titres (Google Fonts)
    body_font: str  # Police du corps
    font_sizes: dict[str, int]  # Taille des polices (ex: {"h1": 24, "h2": 20, "h3": 18, "body": 16})
    line_heights: dict[str, float]  # Hauteur des lignes (ex: {"h1": 1.2, "h2": 1.3, "h3": 1.4, "body": 1.5})

    # TODO: Implement Google Fonts Whitelist validation in future version
    ALLOWED_FONTS = None  # None = all fonts allowed for now

    def __post_init__(self):
        """Validate typography configuration."""
        # Validate font sizes
        required_sizes = {"h1", "h2", "h3", "body", "small"}
        if not required_sizes.issubset(self.font_sizes.keys()):
            raise ValueError(f"Missing required font sizes: {required_sizes - self.font_sizes.keys()}")

        for size_name, size_value in self.font_sizes.items():
            if not isinstance(size_value, int) or not (8 <= size_value <= 72):
                raise ValueError(f"Invalid font size for {size_name}: {size_value}. Expected int between 8 and 72.")

        # Validate line heights
        required_line_heights = {"heading", "body"}
        if not required_line_heights.issubset(self.line_heights.keys()):
            raise ValueError(f"Missing required line heights: {required_line_heights - self.line_heights.keys()}")

        for line_height_name, line_height_value in self.line_heights.items():
            if not isinstance(line_height_value, float) or not (1.0 <= line_height_value <= 2.5):
                raise ValueError(
                    f"Invalid line height for {line_height_name}: {line_height_value}. Expected float between 1.0 and 2.5."
                )

    @classmethod
    def default(cls) -> TypographyConfig:
        """Return the default FreelanSign typography configuration."""
        return cls(
            heading_font="Inter",
            body_font="Inter",
            font_sizes={"h1": 20, "h2": 16, "h3": 13, "body": 12, "small": 10},
            line_heights={"heading": 1.2, "body": 1.5},
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "heading_font": self.heading_font,
            "body_font": self.body_font,
            "font_sizes": self.font_sizes,
            "line_heights": self.line_heights,
        }

    @classmethod
    def from_dict(cls, data: dict) -> TypographyConfig:
        """Create from dictionary for JSON deserialization."""
        return cls(
            heading_font=data["heading_font"],
            body_font=data["body_font"],
            font_sizes=data["font_sizes"],
            line_heights=data["line_heights"],
        )
