# backend/apps/catalog/tests/test_models.py
from django.db import IntegrityError
from django.test import TestCase

from apps.catalog.models import Area, Prestation, PrestationStatus


class CatalogModelTests(TestCase):
    def test_area_unique_name(self):
        Area.objects.create(name="Développement Web")
        with self.assertRaises(IntegrityError):
            Area.objects.create(name="Développement Web")

    def test_prestation_unique_per_area(self):
        a = Area.objects.create(name="DevOps & Cloud")
        Prestation.objects.create(area=a, name="CI/CD", weight_days=2, default_rate_cents=100000)
        with self.assertRaises(IntegrityError):
            Prestation.objects.create(area=a, name="CI/CD", weight_days=3, default_rate_cents=150000)

    def test_status_filtering(self):
        a = Area.objects.create(name="UI/UX")
        Prestation.objects.create(area=a, name="Maquettes", status=PrestationStatus.ACTIVE)
        Prestation.objects.create(area=a, name="Audit UX", status=PrestationStatus.DRAFT)
        self.assertEqual(Prestation.objects.filter(status=PrestationStatus.ACTIVE).count(), 1)
