# apps/branding/domain/services/theme_normalizer.py
from apps.branding.domain.services.theme_validator import ThemeValidator
from apps.branding.domain.value_objects.color_palette import ColorPalette
from apps.branding.domain.value_objects.spacing_config import SpacingConfig
from apps.branding.domain.value_objects.typography_config import TypographyConfig


def normalize_theme_dict(raw_theme_dict: dict) -> dict:
    """
    Take a dictionary of theme values and return a normalized dictionary of theme values.
    """
    if not raw_theme_dict:
        # full default theme
        colors = ColorPalette.default()
        typography = TypographyConfig.default()
        spacing = SpacingConfig.default()
        return {
            "name": "FreelanSign Default Theme",
            "logo_url": None,
            "colors": colors.to_dict(),
            "typography": typography.to_dict(),
            "spacing": spacing.to_dict(),
        }

    # colors
    raw_colors = raw_theme_dict.get("colors", {})
    colors = ColorPalette.from_dict(raw_colors)

    # typography
    raw_typo = raw_theme_dict.get("typography", {})
    default_typography = TypographyConfig.default().to_dict()
    merged_typo = {
        "heading_font": raw_typo.get("heading_font", default_typography["heading_font"]),
        "body_font": raw_typo.get("body_font", default_typography["body_font"]),
        "font_sizes": raw_typo.get("font_sizes", default_typography["font_sizes"]),
        "line_heights": raw_typo.get("line_heights", default_typography["line_heights"]),
    }
    typo = TypographyConfig.from_dict(merged_typo)

    # spacing
    raw_spacing = raw_theme_dict.get("spacing", {})
    default_spacing = SpacingConfig.default().to_dict()
    merged_spacing = {
        "page_margin": raw_spacing.get("page_margin", default_spacing["page_margin"]),
        "section_spacing": raw_spacing.get("section_spacing", default_spacing["section_spacing"]),
        "element_padding": raw_spacing.get("element_padding", default_spacing["element_padding"]),
    }
    spacing = SpacingConfig.from_dict(merged_spacing)

    return {
        "id": raw_theme_dict.get("id"),
        "name": raw_theme_dict.get("name") or "FreelanSign Default Theme",
        "logo_url": raw_theme_dict.get("logo_url"),
        "colors": colors.to_dict(),
        "typography": typo.to_dict(),
        "spacing": spacing.to_dict(),
    }
