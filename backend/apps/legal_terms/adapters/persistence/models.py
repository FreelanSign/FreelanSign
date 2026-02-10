"""
Django models for legal_terms persistence.
"""

import uuid

from django.db import models


class LegalTemplateModel(models.Model):
    """Legal template model (global, FreelanSign-owned)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    jurisdiction = models.CharField(max_length=10, default="FR")
    version = models.CharField(max_length=50)
    clauses = models.JSONField(help_text="List of clause objects with default content")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "legal_template"
        constraints = [
            models.UniqueConstraint(
                fields=["jurisdiction", "version"],
                name="unique_jurisdiction_version",
            )
        ]
        indexes = [
            models.Index(fields=["jurisdiction", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} v{self.version} ({self.jurisdiction})"


class LegalProfileModel(models.Model):
    """Legal profile model (per-account overrides)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.OneToOneField(
        "user.Account",
        on_delete=models.CASCADE,
        related_name="legal_profile",
    )
    template = models.ForeignKey(
        LegalTemplateModel,
        on_delete=models.PROTECT,
        related_name="profiles",
    )
    clause_overrides = models.JSONField(
        default=dict,
        help_text="Overrides by clause identifier",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "legal_profile"
        indexes = [
            models.Index(fields=["account"]),
        ]

    def __str__(self):
        return f"Profile for Account {self.account_id}"


class AttachedTermsModel(models.Model):
    """Attached terms model (immutable snapshot per quote)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quote = models.OneToOneField(
        "quote.Quote",
        on_delete=models.PROTECT,
        related_name="legal_terms",
    )
    template_version = models.CharField(max_length=50)
    rendered_html = models.TextField()
    rendered_text = models.TextField()
    snapshot_data = models.JSONField(help_text="Complete snapshot of terms at creation")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "attached_terms"
        indexes = [
            models.Index(fields=["quote"]),
        ]

    def __str__(self):
        return f"Terms for Quote {self.quote_id} (v{self.template_version})"
