# apps/client/models.py
import uuid

from django.conf import settings
from django.db import models

from apps.core.fields import EncryptedCharField, EncryptedEmailField
from apps.core.models import SoftDeleteModel, TimestampedModel


class Client(TimestampedModel, SoftDeleteModel):
    """
    Simple client model for quotes.
    Keep it compact — extend later with addresses, contacts, VAT, etc.

    Soft delete enabled for RGPD compliance.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="clients", help_text="Owner who created this client."
    )
    account = models.ForeignKey(
        "user.Account",
        on_delete=models.PROTECT,
        related_name="clients",
        help_text="Account owning this client.",
    )
    name = models.CharField(max_length=255)
    # RGPD: Encrypted fields for sensitive personal data (SPECIFICATIONS_RGPD.md Section 3.1.1)
    email = EncryptedEmailField(blank=True)
    phone = EncryptedCharField(max_length=64, blank=True)
    address = models.TextField(blank=True)
    vat_number = EncryptedCharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "client_client"
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        indexes = [
            models.Index(fields=["account", "name"], name="ix_client_account_name"),
        ]

    def __str__(self):
        return self.name
