# apps/quote/adapters/persistence/django_prestation_repository.py
from __future__ import annotations
from apps.quote.application.ports.prestation_repository import PrestationRepository, PrestationDTO
from apps.catalog.models import Prestation


class DjangoPrestationRepository(PrestationRepository):
    """ Prestation repository using Django ORM. """
    def get(self, prestation_id: str) -> PrestationDTO:
        """ Get a prestation by id. """
        prestation = Prestation.objects.select_related("area").get(pk=prestation_id)
        return PrestationDTO(
            id=str(prestation.pk),
            name=prestation.name,
            area_name=getattr(prestation.area, "name", None),
            default_rate_cents=int(prestation.default_rate_cents),
            weight_days=int(prestation.weight_days or 1),
            status=getattr(prestation, "status", None),
        )
