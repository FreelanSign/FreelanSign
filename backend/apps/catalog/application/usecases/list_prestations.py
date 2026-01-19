# apps/catalog/application/usecases/list_prestations.py
"""
Use case: Lister les prestations.
"""

import logging

from apps.catalog.application.dto.prestation_inputs import ListPrestationsInput
from apps.catalog.application.dto.prestation_viewmodels import (
    PrestationListViewModel,
    PrestationViewModel,
)
from apps.catalog.application.errors import RepositoryError
from apps.catalog.application.ports.prestation_repository import PrestationRepository
from apps.catalog.domain.services.prestation_calculator import PrestationCalculator

logger = logging.getLogger(__name__)


class ListPrestations:
    """
    Use case: Récupérer une liste de prestations selon des filtres.
    """

    def __init__(self, prestation_repository: PrestationRepository):
        self.prestation_repository = prestation_repository

    def execute(self, input_dto: ListPrestationsInput) -> PrestationListViewModel:
        """
        Exécute le use case.

        Args:
            input_dto: Filtres de recherche

        Returns:
            PrestationListViewModel

        Raises:
            RepositoryError: En cas d'erreur d'accès aux données
        """
        logger.info("ListPrestations: area_id=%s status=%s search=%s", input_dto.area_id, input_dto.status, input_dto.search)

        try:
            # Récupération via le repository
            prestations_qs = self.prestation_repository.list_prestations(input_dto)

            # Conversion en ViewModels
            prestations_vm = [self._to_viewmodel(prest) for prest in prestations_qs]

            logger.info("ListPrestations: %d prestations trouvées", len(prestations_vm))

            return PrestationListViewModel(prestations=prestations_vm, total_count=len(prestations_vm))

        except Exception as e:
            logger.exception("Erreur lors du listing des prestations")
            raise RepositoryError("Impossible de récupérer les prestations", original_error=e)

    def _to_viewmodel(self, prestation) -> PrestationViewModel:
        """Convertit une Prestation en ViewModel."""
        return PrestationViewModel(
            id=prestation.id,
            area_id=prestation.area_id,
            area_name=prestation.area.name,
            name=prestation.name,
            description=prestation.description,
            weight_days=prestation.weight_days,
            default_rate_cents=prestation.default_rate_cents,
            default_rate_display=PrestationCalculator.format_rate_display(prestation.default_rate_cents),
            status=prestation.status,
            custom=prestation.custom,
            account_id=prestation.account_id,  # Phase 5.4
            created_at=prestation.created_at,
            updated_at=prestation.updated_at,
        )
