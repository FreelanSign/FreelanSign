# apps/user/application/usecases/update_professional.py
"""
Use case: Mettre à jour un profil professionnel.
"""
import logging

from apps.user.application.dto.user_inputs import UpdateProfessionalInput
from apps.user.application.dto.user_viewmodels import ProfessionalViewModel
from apps.user.application.errors import RepositoryError, UserNotFoundError
from apps.user.application.ports.user_repository import ProfessionalRepository, UserRepository
from apps.user.domain.policies.user_policy import ProfessionalPolicy
from apps.user.domain.services.user_calculator import UserCalculator

logger = logging.getLogger(__name__)


class UpdateProfessional:
    """
    Use case: Mettre à jour un profil professionnel.
    """

    def __init__(self, user_repository: UserRepository, professional_repository: ProfessionalRepository):
        self.user_repository = user_repository
        self.professional_repository = professional_repository

    def execute(self, input_dto: UpdateProfessionalInput) -> ProfessionalViewModel:
        """
        Exécute le use case.

        Args:
            input_dto: UpdateProfessionalInput

        Returns:
            ProfessionalViewModel

        Raises:
            UserNotFoundError: En cas d'utilisateur non trouvé
            RepositoryError: En cas d'erreur d'acces aux données
        """
        logger.info(
            "UpdateProfessional: professional_id=%s user_id=%s service_type_ids=%s",
            input_dto.professional_id,
            input_dto.user_id,
            input_dto.service_type_ids,
        )

        user = self.user_repository.get_by_id(input_dto.user_id)
        if not user:
            raise UserNotFoundError(user_id=input_dto.user_id)

        if input_dto.tjm_cents is not None:
            ProfessionalPolicy.validate_tjm_cents(input_dto.tjm_cents)
        if input_dto.status_juridique:
            ProfessionalPolicy.validate_status_juridique(input_dto.status_juridique)

        try:
            # ✅ Construction conditionnelle du dictionnaire
            # Ne passer que les champs qui ont été explicitement fournis (non None)
            data = {}

            if input_dto.name is not None:
                data["name"] = input_dto.name

            if input_dto.status_juridique is not None:
                data["status_juridique"] = input_dto.status_juridique

            if input_dto.domaine_id is not None:
                data["domaine_id"] = input_dto.domaine_id

            if input_dto.tjm_cents is not None:
                data["tjm_cents"] = input_dto.tjm_cents

            if input_dto.number_pro is not None:
                data["number_pro"] = input_dto.number_pro

            # ✅ CRITIQUE: service_type_ids doit être passé même s'il est une liste vide
            # On vérifie explicitement qu'il n'est pas None (pas juste "if truthy")
            if input_dto.service_type_ids is not None:
                data["service_type_ids"] = input_dto.service_type_ids
                logger.info(
                    "UpdateProfessional: setting service_type_ids=%s",
                    input_dto.service_type_ids,
                )

            logger.debug("UpdateProfessional: data to update=%s", data)

            pro = self.professional_repository.update(input_dto.professional_id, data)

            # Vérifier que les service_types ont bien été mis à jour
            actual_service_ids = list(pro.service_types.values_list("id", flat=True)) if hasattr(pro, "service_types") else []
            logger.info(
                "UpdateProfessional: after update, service_type_ids in DB=%s",
                actual_service_ids,
            )

            return ProfessionalViewModel(
                id=pro.id,
                user_id=pro.user_id,
                name=pro.name,
                status_juridique=pro.status_juridique,
                domaine_id=pro.domaine_id,
                domaine_name=(pro.domaine.name if getattr(pro, "domaine", None) else None),
                tjm_cents=pro.tjm_cents,
                tjm_display=UserCalculator.format_tjm_display(pro.tjm_cents),
                number_pro=pro.number_pro,
                service_type_ids=actual_service_ids,
                created_at=pro.created_at,
                updated_at=pro.updated_at,
            )
        except Exception as e:
            logger.exception("Erreur UpdateProfessional")
            raise RepositoryError("Impossible de mettre à jour le profil professionnel", original_error=e)
