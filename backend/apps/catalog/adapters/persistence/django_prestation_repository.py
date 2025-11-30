# apps/catalog/adapters/persistence/django_prestation_repository.py
"""
Implémentation Django du PrestationRepository.
"""
import logging
from typing import Optional

from django.db.models import Q

from apps.catalog.application.dto.prestation_inputs import ListPrestationsInput
from apps.catalog.application.errors import RepositoryError
from apps.catalog.application.ports.prestation_repository import (
    AreaRepository,
    PrestationRepository,
)
from apps.catalog.models import Area, Prestation

logger = logging.getLogger(__name__)


class DjangoPrestationRepository(PrestationRepository):
    """
    Implémentation concrète du repository avec Django ORM.
    """

    def get_by_id(self, prestation_id: int):
        """Récupère une prestation par ID."""
        try:
            return Prestation.objects.select_related("area").get(id=prestation_id)
        except Prestation.DoesNotExist:
            return None
        except Exception as e:
            logger.exception("Erreur lors de get_by_id(%s)", prestation_id)
            raise RepositoryError(
                f"Erreur technique lors de la récupération de la prestation {prestation_id}", original_error=e
            )

    def list_prestations(self, filters: ListPrestationsInput):
        """Liste les prestations selon des filtres."""
        try:
            qs = Prestation.objects.select_related("area").all()

            # Filtre par IDs spécifiques
            if filters.prestation_ids:
                qs = qs.filter(id__in=filters.prestation_ids)

            # Filtre par area
            if filters.area_id is not None:
                qs = qs.filter(area_id=filters.area_id)

            # Filtre par statut
            if filters.status:
                qs = qs.filter(status__iexact=filters.status)

            # Filtre par account (Phase 5.4)
            if filters.account_id is not None:
                qs = qs.filter(Q(account__isnull=True) | Q(account_id=filters.account_id))

            # Recherche textuelle
            if filters.search:
                qs = qs.filter(Q(name__icontains=filters.search) | Q(description__icontains=filters.search))

            # Tri
            if filters.ordering:
                if isinstance(filters.ordering, list):
                    order_fields = filters.ordering
                else:
                    order_fields = filters.ordering.split(",")
                qs = qs.order_by(*order_fields)
            else:
                qs = qs.order_by("area__name", "name")

            return qs

        except Exception as e:
            logger.exception("Erreur lors du listing des prestations")
            raise RepositoryError("Erreur technique lors du listing des prestations", original_error=e)

    def exists_by_name_and_area(self, name: str, area_id: int, account_id: Optional[int] = None) -> bool:
        """Vérifie si une prestation existe déjà. Phase 5.4: account_id instead of professional_user_id."""
        try:
            if account_id is None:
                # Prestation globale
                return Prestation.objects.filter(name__iexact=name, area_id=area_id, account__isnull=True).exists()
            else:
                # Prestation custom d'un account
                return Prestation.objects.filter(name__iexact=name, account_id=account_id).exists()
        except Exception as e:
            logger.exception("Erreur lors de exists_by_name_and_area")
            raise RepositoryError("Erreur technique lors de la vérification d'existence", original_error=e)

    def create(self, prestation_data: dict):
        """Crée une nouvelle prestation."""
        try:
            return Prestation.objects.create(**prestation_data)
        except Exception as e:
            logger.exception("Erreur lors de la création de prestation")
            raise RepositoryError("Erreur technique lors de la création de la prestation", original_error=e)

    def update(self, prestation_id: int, update_data: dict):
        """Met à jour une prestation."""
        try:
            prestation = self.get_by_id(prestation_id)
            if prestation is None:
                raise RepositoryError(f"Prestation {prestation_id} introuvable")

            for key, value in update_data.items():
                setattr(prestation, key, value)

            prestation.save()
            return prestation
        except Exception as e:
            logger.exception("Erreur lors de la mise à jour de prestation")
            raise RepositoryError(
                f"Erreur technique lors de la mise à jour de la prestation {prestation_id}", original_error=e
            )


class DjangoAreaRepository(AreaRepository):
    """Implémentation concrète du repository Area avec Django ORM."""

    def get_by_id(self, area_id: int):
        """Récupère une area par ID."""
        try:
            return Area.objects.get(id=area_id)
        except Area.DoesNotExist:
            return None
        except Exception as e:
            logger.exception("Erreur lors de get_by_id area(%s)", area_id)
            raise RepositoryError(f"Erreur technique lors de la récupération de l'area {area_id}", original_error=e)

    def list_areas(self, search: Optional[str] = None):
        """Liste les areas."""
        try:
            qs = Area.objects.all().order_by("name")

            if search:
                qs = qs.filter(name__icontains=search)

            return qs
        except Exception as e:
            logger.exception("Erreur lors du listing des areas")
            raise RepositoryError("Erreur technique lors du listing des areas", original_error=e)

    def exists(self, area_id: int) -> bool:
        """Vérifie si une area existe."""
        try:
            return Area.objects.filter(id=area_id).exists()
        except Exception as e:
            logger.exception("Erreur lors de la vérification d'existence area")
            raise RepositoryError("Erreur technique lors de la vérification d'existence de l'area", original_error=e)
