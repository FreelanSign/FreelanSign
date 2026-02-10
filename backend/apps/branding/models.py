# apps/branding/models.py
from __future__ import annotations

import uuid
from tabnanny import verbose

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q


class BrandTheme(models.Model):
    """
    Brand theme for document customization.
    A professional user can have multiple themes but only one active at a time.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # owner
    account = models.ForeignKey(
        "user.Account",
        on_delete=models.CASCADE,
        related_name="brand_themes",
        help_text="Account that owns the theme.",
    )

    # Basic info
    name = models.CharField(max_length=128, help_text="Name of the theme (e.g. 'Default', 'Professional', 'Personal').")
    is_active = models.BooleanField(default=False, help_text="Whether the theme is active.")

    # customization data (stored as JSON)
    colors = models.JSONField(
        default=dict,
        help_text="Color palette: primary, secondary, background, text_primary, text_secondary, border, highlight.",
    )
    typography = models.JSONField(
        default=dict,
        help_text="Typography config: heading_font, body_font, font_sizes, line_heights.",
    )
    spacing = models.JSONField(
        default=dict,
        help_text="Spacing config: page_margin, section_spacing, element_padding.",
    )

    # Logo
    logo = models.FileField(
        upload_to="branding/logos/%Y/%m/",
        null=True,
        blank=True,
        help_text="Logo image file.",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "branding_brand_theme"
        verbose_name = "Brand Theme"
        verbose_name_plural = "Brand Themes"
        constraints = [
            # Ensure theme names are unique per account
            models.UniqueConstraint(
                fields=["account", "name"],
                name="uq_brand_account_name",
            ),
            # Ensure only one theme can be active at a time per account
            models.UniqueConstraint(
                fields=["account"],
                condition=models.Q(is_active=True),
                name="uq_brand_account_active",
            ),
        ]
        indexes = [
            models.Index(fields=["account", "is_active"], name="ix_brand_account_active"),
            models.Index(fields=["account"], name="ix_brand_account"),
        ]
        ordering = ["-is_active", "-updated_at"]

    def __str__(self) -> str:
        status = "Active" if self.is_active else "Inactive"
        return f"{self.name} - {status} ({self.account.display_name})"

    def clean(self):
        """Validate that only one theme can be active at a time per account."""
        if self.is_active:
            # Check if another theme is already active
            active_themes = BrandTheme.objects.filter(
                account=self.account,
                is_active=True,
            ).exclude(pk=self.pk)

            if active_themes.exists():
                raise ValidationError("Only one theme can be active at a time per account.")

    def save(self, *args, **kwargs) -> None:
        """Override save to ensure only one active theme per account."""
        if self.is_active:
            # Deactivate all other themes for this account
            with transaction.atomic():
                BrandTheme.objects.filter(
                    account=self.account,
                    is_active=True,
                ).exclude(
                    pk=self.pk
                ).update(is_active=False)

        super().save(*args, **kwargs)

    @property
    def logo_url(self) -> str | None:
        """Return the URL of the logo if it exists."""
        if self.logo:
            return self.logo.url
        return None
