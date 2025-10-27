# apps/user/application/usecases/create_professional.py
"""
Use case: Créer un profil professionnel.
"""
import logging

from apps.user.application.dto.user_inputs import CreateProfessionalInput
from apps.user.application.dto.user_viewmodels import ProfessionalViewModel
from apps.user.application.errors import RepositoryError, UserNotFoundError
from apps.user.application.ports.user_repository import (
    ProfessionalRepository,
    UserRepository,
)
from apps.user.domain.errors import DuplicateProfessionalError
from apps.user.domain.policies.user_policy import ProfessionalPolicy
from apps.user.domain.services.user_calculator import UserCalculator

logger = logging.getLogger(__name__)


class CreateProfessional:
    """
    Use case: Créer un profil professionnel pour un utilisateur.
    """

    def __init__(self, user_repository: UserRepository, professional_repository: ProfessionalRepository):
        self.user_repository = user_repository
        self.professional_repository = professional_repository

    def execute(self, input_dto: CreateProfessionalInput) -> ProfessionalViewModel:
        """
        Exécute le use case.

        Args:
            input_dto: Données de création

        Returns:
            ProfessionalViewModel

        Raises:
            UserNotFoundError: Utilisateur introuvable
            DuplicateProfessionalError: Profil professionnel déjà existant
            InvalidTJMError: TJM invalide
            InvalidStatusJuridiqueError: Statut juridique invalide
            RepositoryError: Erreur technique
        """
        logger.info("CreateProfessional: user_id=%s", input_dto.user_id)

        # 1) Vérifier que l'utilisateur existe
        user = self.user_repository.get_by_id(input_dto.user_id)
        if not user:
            raise UserNotFoundError(user_id=input_dto.user_id)

        # 2) Vérifier qu'un profil pro n'existe pas déjà
        if self.professional_repository.exists_for_user(input_dto.user_id):
            logger.warning("CreateProfessional: profil pro déjà existant pour user_id=%s", input_dto.user_id)
            raise DuplicateProfessionalError(input_dto.user_id)

        # 3) Validation des règles métier
        ProfessionalPolicy.validate_tjm_cents(input_dto.tjm_cents)

        if input_dto.status_juridique:
            ProfessionalPolicy.validate_status_juridique(input_dto.status_juridique)

        # 4) Créer le profil professionnel
        try:
            professional_data = {
                "user_id": input_dto.user_id,
                "name": input_dto.name or "",
                "status_juridique": input_dto.status_juridique,
                "domaine_id": input_dto.domaine_id,
                "tjm_cents": input_dto.tjm_cents,
                "number_pro": input_dto.number_pro,
                "service_type_ids": input_dto.service_type_ids or [],
            }

            professional = self.professional_repository.create(professional_data)

            logger.info("CreateProfessional: profil créé id=%s pour user_id=%s", professional.id, input_dto.user_id)

            return self._to_viewmodel(professional)

        except Exception as e:
            logger.exception("Erreur lors de la création du profil professionnel")
            raise RepositoryError("Impossible de créer le profil professionnel", original_error=e)

    def _to_viewmodel(self, professional) -> ProfessionalViewModel:
        """Convertit un ProfessionalUser en ViewModel."""
        domaine_name = None
        if hasattr(professional, "domaine") and professional.domaine:
            domaine_name = professional.domaine.name

        service_type_ids = []
        if hasattr(professional, "service_types"):
            service_type_ids = list(professional.service_types.values_list("id", flat=True))

        return ProfessionalViewModel(
            id=professional.id,
            user_id=professional.user_id,
            name=professional.name,
            status_juridique=professional.status_juridique,
            domaine_id=professional.domaine_id,
            domaine_name=domaine_name,
            tjm_cents=professional.tjm_cents,
            tjm_display=UserCalculator.format_tjm_display(professional.tjm_cents),
            number_pro=professional.number_pro,
            service_type_ids=service_type_ids,
            created_at=professional.created_at,
            updated_at=professional.updated_at,
        )
