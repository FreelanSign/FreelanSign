# apps/user/models/account.py
"""Django model for Account entity."""
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from apps.core.fields import EncryptedCharField
from apps.core.models import SoftDeleteModel, TimestampedModel


class LegalForm(models.TextChoices):
    """Legal forms for freelance accounts."""

    MICRO = "micro", "Micro-entrepreneur"
    EIRL = "eirl", "EIRL"
    EURL = "eurl", "EURL"
    SASU = "sasu", "SASU"
    OTHER = "other", "Autre"


class Account(TimestampedModel, SoftDeleteModel):
    """
    Account model - replaces ProfessionalUser.
    Represents a freelance entity (1:N relationship with User in future).

    Two-level soft delete for RGPD compliance:
    - is_active=False: Reversible suspension
    - is_deleted=True: RGPD soft delete with cascade to Clients

    @author: @Bertrand2808
    @since: 2025-11-25
    @version: 1.1
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
    # RGPD: Encrypted field for sensitive identification data (SPECIFICATIONS_RGPD.md Section 3.1.1)
    legal_id = EncryptedCharField(
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
    default_rate_cents = models.BigIntegerField(
        blank=True,
        null=True,
        help_text="Default daily rate in cents (TJM)",
    )
    professional_headline = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Professional title displayed on quotes (e.g., 'Développeur Fullstack')",
    )
    service_types = models.ManyToManyField(
        "catalog.Prestation",
        blank=True,
        related_name="accounts_favorites",
        help_text="Favorite service types for this account",
    )
    is_active = models.BooleanField(default=True)

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

    def delete(self, hard: bool = False, using=None, keep_parents=False):
        """
        Soft-delete Account with cascade to Clients (RGPD compliance).

        Blocks deletion if active Quotes exist (DRAFT, SENT, ACCEPTED).
        Cascades soft delete to all non-deleted Clients.
        Uses transaction.atomic to ensure atomicity.

        Args:
            hard: If True, performs hard delete (bypass soft delete)
            using: Database alias
            keep_parents: Standard Django delete parameter

        Raises:
            ValueError: If active Quotes exist (DRAFT, SENT, ACCEPTED)
        """
        if hard:
            # Pass hard=True to SoftDeleteModel.delete() to bypass soft delete
            return super().delete(hard=True, using=using, keep_parents=keep_parents)

        # AIDEV-NOTE: Vérifier les quotes actives uniquement (pas PAID)
        # PAID = transaction terminée, conservation légale avec anonymisation
        from apps.quote.models import Quote

        active_statuses = ["DRAFT", "SENT", "ACCEPTED"]
        if self.quotes.filter(status__in=active_statuses).exists():
            raise ValueError(
                "Impossible de supprimer le compte : des devis actifs existent. "
                "Veuillez d'abord finaliser ou annuler les devis en cours."
            )

        # AIDEV-NOTE: Assure que la cascade et la suppression de l'Account sont atomiques
        with transaction.atomic():
            # Cascade : soft-delete clients non déjà supprimés
            now = timezone.now()
            self.clients.filter(is_deleted=False).update(is_deleted=True, deleted_at=now)

            # Soft-delete Account via le mécanisme du SoftDeleteModel
            if not self.is_deleted:
                self.is_deleted = True
                self.is_active = False  # Deactivate when deleted
                self.deleted_at = now
                self.save(update_fields=["is_deleted", "deleted_at", "is_active"])
