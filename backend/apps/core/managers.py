from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        # soft-delete en masse
        return super().update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        # hard-delete en masse
        return super().delete()

    def alive(self):
        return self.filter(is_deleted=False)

    def dead(self):
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

    def hard_delet(self):
        return self.get_queryset().hard_delete()

    def dead(self):
        return self.get_queryset().dead()


class SoftDeleteManagerWithDeleted(models.Manager):
    """Manager qui ne filtre pas par défaut (inclut supprimés)"""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)


class OwnedByUserQuerySet(models.QuerySet):
    def for_user(self, user):
        if user is None:
            return self.none()
        return self.filter(owner=user)
