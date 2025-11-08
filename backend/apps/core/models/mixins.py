from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.managers import SoftDeleteManager, SoftDeleteManagerWithDeleted


class TimestampedModel(models.Model):
    """Ajoute created_at & updated_at à toutes les entités."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Soft-delete générique : on masque la ligne au lieu de la supprimer.
    .objects    -> ne renvoie que les éléments non supprimés
    .all_objects -> renvoie tous les éléments
    """

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Managers
    objects = SoftDeleteManager()
    all_objects = SoftDeleteManagerWithDeleted()

    class Meta:
        abstract = True

    def delete(self, hard: bool = False, using=None, keep_parents=False):
        if hard:
            return super().delete(using=using, keep_parents=keep_parents)
        if not self.is_deleted:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(update_fields=["is_deleted", "deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    def undelete(self):
        if self.is_deleted:
            self.is_deleted = False
            self.deleted_at = None
            self.save(update_fields=["is_deleted", "deleted_at"])


class OwnedByUserMixin(models.Model):
    """
    Rattache l'entité à un utilisateur.
    Compatible avec SoftDeleteModel (héritage multiple).
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_owned",
        db_index=True,
    )

    class Meta:
        abstract = True

    @classmethod
    def for_user(cls, user):
        """Filtre utilitaire simple, compatible avec n'importe quel manager."""
        if user is None or getattr(user, "is_anonymous", False):
            return cls.objects.none()
        return cls.objects.filter(owner=user)


class DocumentCounter(models.Model):
    """
    Compteur séquentiel par propriétaire, type de document et période.
    Ex: (owner=42, doc_type='QUOTE', period='2025-11) --> last_value: 7
    """

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    doc_type = models.CharField(max_length=16)  # 'QUOTE'
    period = models.CharField(max_length=8)
    last_value = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "core_document_counter"
        constraints = [models.UniqueConstraint(fields=["owner", "doc_type", "period"], name="uq_counter_owner_type_period")]

    def __str__(self) -> str:
        return f"{self.doc_type} {self.owner} {self.period} -> {self.last_value}"
