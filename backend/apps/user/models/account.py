# apps/user/models/account.py
"""Django model for Account entity."""
from django.conf import settings
from django.db import models


class LegalForm(models.TextChoices):
    """Legal forms for freelance accounts."""
    MICRO = "micro", "Micro-entrepreneur"
    EIRL = "eirl", "EIRL"
    EURL = "eurl", "EURL"
    SASU = "sasu", "SASU"
    OTHER = "other", "Autre"


class Account(models.Model):
    """
    Account model - replaces ProfessionalUser.
    Represents a freelance entity (1:N relationship with User in future).

    @author: @Bertrand2808
    @since: 2025-11-25
    @version: 1.0
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accounts",
    )
    display_name = models.CharField(max_length=255)
    legal_form = models.CharField(
        max_length=10,
        choices=LegalForm.choices,
        blank=True,
        null=True,
    )
    legal_id = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        help_text="SIRET (14 digits)",
    )
    domain = models.ForeignKey(
        "catalog.Area",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accounts",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "display_name")]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["domain"]),
        ]
        verbose_name = "Account"
        verbose_name_plural = "Accounts"

    def __str__(self):
        return self.display_name or f"Account<{self.id}>"
