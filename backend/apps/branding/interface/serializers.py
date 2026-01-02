# apps/branding/interface/serializers.py
from __future__ import annotations

from rest_framework import serializers

from apps.branding.domain.value_objects.color_palette import ColorPalette
from apps.branding.domain.value_objects.spacing_config import SpacingConfig
from apps.branding.domain.value_objects.typography_config import TypographyConfig


class ColorPaletteSerializer(serializers.Serializer):
    """Serializer for color palette."""

    primary = serializers.RegexField(regex=r"^#[0-9A-Fa-f]{6}$", required=True)
    secondary = serializers.RegexField(regex=r"^#[0-9A-Fa-f]{6}$", required=True)
    background = serializers.RegexField(regex=r"^#[0-9A-Fa-f]{6}$", required=True)
    text_primary = serializers.RegexField(regex=r"^#[0-9A-Fa-f]{6}$", required=True)
    text_secondary = serializers.RegexField(regex=r"^#[0-9A-Fa-f]{6}$", required=True)
    border = serializers.RegexField(regex=r"^#[0-9A-Fa-f]{6}$", required=True)
    highlight = serializers.RegexField(regex=r"^#[0-9A-Fa-f]{6}$", required=True)


class FontSizesSerializer(serializers.Serializer):
    """Serializer for font sizes."""

    h1 = serializers.IntegerField(min_value=8, max_value=72, required=True)
    h2 = serializers.IntegerField(min_value=8, max_value=72, required=True)
    h3 = serializers.IntegerField(min_value=8, max_value=72, required=True)
    body = serializers.IntegerField(min_value=8, max_value=72, required=True)
    small = serializers.IntegerField(min_value=8, max_value=72, required=True)


class LineHeightsSerializer(serializers.Serializer):
    """Serializer for line heights."""

    heading = serializers.FloatField(min_value=1.0, max_value=2.5, required=True)
    body = serializers.FloatField(min_value=1.0, max_value=2.5, required=True)


class TypographyConfigSerializer(serializers.Serializer):
    """Serializer for typography configuration."""

    heading_font = serializers.CharField(max_length=128, required=True)
    body_font = serializers.CharField(max_length=128, required=True)
    font_sizes = FontSizesSerializer(required=True)
    line_heights = LineHeightsSerializer(required=True)


class SpacingConfigSerializer(serializers.Serializer):
    """Serializer for spacing configuration."""

    page_margin = serializers.IntegerField(min_value=0, max_value=100, required=True)
    section_spacing = serializers.IntegerField(min_value=0, max_value=100, required=True)
    element_padding = serializers.IntegerField(min_value=0, max_value=100, required=True)


class CreateThemeSerializer(serializers.Serializer):
    """Serializer for creating a theme."""

    name = serializers.CharField(max_length=128, required=True)
    is_active = serializers.BooleanField(default=False)
    colors = ColorPaletteSerializer(required=True)
    typography = TypographyConfigSerializer(required=True)
    spacing = SpacingConfigSerializer(required=True)
    logo = serializers.ImageField(required=False, allow_null=True)

    def validate_name(self, value):
        """Validate theme name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Theme name cannot be empty.")
        return value.strip()


class UpdateThemeSerializer(serializers.Serializer):
    """Serializer for updating a theme."""

    name = serializers.CharField(max_length=128, required=False)
    is_active = serializers.BooleanField(required=False)
    colors = ColorPaletteSerializer(required=False)
    typography = TypographyConfigSerializer(required=False)
    spacing = SpacingConfigSerializer(required=False)
    logo = serializers.ImageField(required=False, allow_null=True)

    def validate_name(self, value):
        """Validate theme name is not empty."""
        if value is not None and (not value or not value.strip()):
            raise serializers.ValidationError("Theme name cannot be empty.")
        return value.strip() if value else None


class ThemeSerializer(serializers.Serializer):
    """Serializer for theme response."""

    id = serializers.UUIDField(read_only=True)
    account_id = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    is_active = serializers.BooleanField()
    colors = ColorPaletteSerializer()
    typography = TypographyConfigSerializer()
    spacing = SpacingConfigSerializer()
    logo_url = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ThemeListItemSerializer(serializers.Serializer):
    """Serializer for theme list item response."""

    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    is_active = serializers.BooleanField()
    colors = ColorPaletteSerializer()
    logo_url = serializers.CharField(allow_null=True)
    updated_at = serializers.DateTimeField(read_only=True)


class DeactivateThemeSerializer(serializers.Serializer):
    """Serializer for deactivating a theme."""

    theme_id = serializers.UUIDField(required=True)
    account_id = serializers.UUIDField(required=True)


class ActivateThemeSerializer(serializers.Serializer):
    """Serializer for activating a theme."""

    theme_id = serializers.UUIDField(required=True)
    account_id = serializers.UUIDField(required=True)
