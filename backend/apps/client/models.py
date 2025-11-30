# apps/client/models.py
import uuid

from django.conf import settings
from django.db import models


class Client(models.Model):
    """
    Simple client model for quotes.
    Keep it compact — extend later with addresses, contacts, VAT, etc.
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
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=64, blank=True)
    address = models.TextField(blank=True)
    vat_number = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "client_client"
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        indexes = [
            models.Index(fields=["account", "name"], name="ix_client_account_name"),
        ]

    def __str__(self):
        return self.name
