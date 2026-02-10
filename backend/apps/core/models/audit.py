# apps/core/models/audit.py
import uuid

from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """
    Log des actions sensibles pour conformité RGPD.

    Attention : c'est un log technique / légal cross-bounded-context,
    pas quelque chose à sur-modéliser.
    """

    class Action(models.TextChoices):
        ACCOUNT_CREATED = "account_created", "Compte créé"
        ACCOUNT_DELETED = "account_deleted", "Compte supprimé"
        ACCOUNT_ANONYMIZED = "account_anonymized", "Compte anonymisé"
        CLIENT_CREATED = "client_created", "Client créé"
        CLIENT_DELETED = "client_deleted", "Client supprimé"
        CLIENT_ANONYMIZED = "client_anonymized", "Client anonymisé"

        # AIDEV_NOTE: on garde la porte ouverte pour plus tard (quote, paiements, etc)
        QUOTE_SENT = "quote_sent", "Devis envoyé"
        QUOTE_SIGNED = "quote_signed", "Devis signé"
        PAYMENT_RECEIVED = "payment_received", "Paiement reçu"
        DATA_EXPORT_REQUESTED = "data_export_requested", "Export de données demandé"
        DATA_DELETION_REQUESTED = "data_deletion_requested", "Suppression de données demandée"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action = models.CharField(max_length=50, choices=Action.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
        help_text="Utilisateur à l'origine de l'action (peut être null si script / tâche async).",
    )

    # AIDEV_NOTE: on ne fait pas de GenericForeignKey car on ne veut pas de dépendances fortes.
    target_model = models.CharField(
        max_length=64,
        help_text="Nom logique de la ressource ciblée (ex: Account, Client, etc).",
    )
    target_id = models.CharField(
        max_length=64,
        help_text="Identifiant de la ressource ciblée (UUID, int, etc. sérialisé en string).",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Données contextuelles minimales (attention à ne pas mettre de données sensibles inutiles).",
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP de l'acteur si action initiée via HTTP.",
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_audit_log"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["actor", "timestamp"]),
            models.Index(fields=["target_model", "target_id"]),
            models.Index(fields=["action", "timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} by {self.actor} at {self.timestamp}"
