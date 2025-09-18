from django.contrib.auth import get_user_model
from django.db import connection, models
from django.test import TestCase
from django.test.utils import isolate_apps

from apps.core.models import OwnedByUserMixin, SoftDeleteModel, TimestampedModel

User = get_user_model()


class TestMixins(TestCase):
    @isolate_apps("apps.core.apps.CoreConfig")  # <— chemin EXACT comme dans INSTALLED_APPS
    def test_timestamped_model(self):
        class Item(TimestampedModel, models.Model):
            name = models.CharField(max_length=64)

            class Meta:
                app_label = "core"

        with connection.schema_editor() as se:
            se.create_model(Item)
        try:
            obj = Item.objects.create(name="a")
            self.assertIsNotNone(obj.created_at)
            self.assertIsNotNone(obj.updated_at)
            before = obj.updated_at
            obj.name = "b"
            obj.save()
            self.assertGreater(obj.updated_at, before)
        finally:
            with connection.schema_editor() as se:
                se.delete_model(Item)

    @isolate_apps("apps.core.apps.CoreConfig")  # <— idem
    def test_soft_delete_model(self):
        class Thing(SoftDeleteModel, models.Model):
            name = models.CharField(max_length=64)

            class Meta:
                app_label = "core"

        with connection.schema_editor() as se:
            se.create_model(Thing)
        try:
            a = Thing.all_objects.create(name="A")
            Thing.all_objects.create(name="B")
            self.assertEqual(Thing.objects.count(), 2)

            a.delete()
            self.assertTrue(Thing.all_objects.get(pk=a.pk).is_deleted)
            self.assertEqual(Thing.objects.count(), 1)

            a.undelete()
            self.assertEqual(Thing.objects.count(), 2)

            Thing.objects.filter(name="B").delete()
            self.assertEqual(Thing.objects.count(), 1)

            a.delete(hard=True)
            self.assertEqual(Thing.all_objects.count(), 1)
        finally:
            with connection.schema_editor() as se:
                se.delete_model(Thing)

    def test_owned_by_user_mixin(self):
        class Owned(OwnedByUserMixin, models.Model):
            title = models.CharField(max_length=64)

            class Meta:
                app_label = "core"

        # Créer la table dans la transaction du TestCase
        with connection.schema_editor() as se:
            se.create_model(Owned)

        # Pas de finally / pas de delete_model ici : on laisse le rollback la supprimer

        u1 = User.objects.create_user(email="u1@example.com", password="x")
        u2 = User.objects.create_user(email="u2@example.com", password="x")

        Owned.objects.create(owner=u1, title="A")
        Owned.objects.create(owner=u2, title="B")

        self.assertEqual(Owned.for_user(u1).count(), 1)
        self.assertEqual(Owned.for_user(u1).first().title, "A")
        self.assertEqual(Owned.for_user(u2).count(), 1)
