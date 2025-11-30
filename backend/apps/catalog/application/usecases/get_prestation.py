# apps/catalog/application/usecases/get_prestation.py
"""
Use case: Récupérer une prestation par ID.
"""
import logging

from apps.catalog.application.dto.prestation_inputs import GetPrestationInput
from apps.catalog.application.dto.prestation_viewmodels import PrestationViewModel
from apps.catalog.application.errors import PrestationNotFoundError, RepositoryError
from apps.catalog.application.ports.prestation_repository import PrestationRepository
from apps.catalog.domain.services.prestation_calculator import PrestationCalculator

logger = logging.getLogger(__name__)


class GetPrestation:
    """
    Use case: Récupérer une prestation spécifique.
    """

    def __init__(self, prestation_repository: PrestationRepository):
        self.prestation_repository = prestation_repository

    def execute(self, input_dto: GetPrestationInput) -> PrestationViewModel:
        """
        Exécute le use case.

        Args:
            input_dto: ID de la prestation

        Returns:
            PrestationViewModel

        Raises:
            PrestationNotFoundError: Si la prestation n'existe pas
            RepositoryError: En cas d'erreur technique
        """
        logger.info("GetPrestation: prestation_id=%s", input_dto.prestation_id)

        try:
            prestation = self.prestation_repository.get_by_id(input_dto.prestation_id)

            if prestation is None:
                logger.warning("Prestation %s introuvable", input_dto.prestation_id)
                raise PrestationNotFoundError(input_dto.prestation_id)

            return self._to_viewmodel(prestation)

        except PrestationNotFoundError:
            raise
        except Exception as e:
            logger.exception("Erreur lors de la récupération de la prestation")
            raise RepositoryError(f"Impossible de récupérer la prestation {input_dto.prestation_id}", original_error=e)

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
            account_id=prestation.account_id,
            created_at=prestation.created_at,
            updated_at=prestation.updated_at,
        )
