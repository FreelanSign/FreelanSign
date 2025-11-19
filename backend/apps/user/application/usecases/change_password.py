# apps/user/application/usecases/change_password.py
"""
Use case: Changer le mot de passe d'un utilisateur.
"""
import logging

from apps.user.application.dto.user_inputs import ChangePasswordInput
from apps.user.application.errors import (
    IncorrectPasswordError,
    RepositoryError,
    UserNotFoundError,
)
from apps.user.application.ports.user_repository import UserRepository
from apps.user.domain.policies.user_policy import UserPolicy

logger = logging.getLogger(__name__)


class ChangePassword:
    """
    Use case: Changer le mot de passe d'un utilisateur.
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, input_dto: ChangePasswordInput) -> None:
        """
        Exécute le use case.

        Args:
            input_dto: Données de changement de mot de passe

        Raises:
            UserNotFoundError: Utilisateur introuvable
            IncorrectPasswordError: Mot de passe actuel incorrect
            InvalidPasswordError: Nouveau mot de passe invalide
            RepositoryError: Erreur technique
        """
        logger.info("ChangePassword: user_id=%s", input_dto.user_id)

        # 1) Vérifier que l'utilisateur existe
        user = self.user_repository.get_by_id(input_dto.user_id)
        if not user:
            raise UserNotFoundError(user_id=input_dto.user_id)

        # 2) Vérifier le mot de passe actuel
        if not self.user_repository.verify_password(input_dto.user_id, input_dto.current_password):
            logger.warning("ChangePassword: mot de passe incorrect pour user_id=%s", input_dto.user_id)
            raise IncorrectPasswordError()

        # 3) Valider le nouveau mot de passe
        UserPolicy.validate_password(input_dto.new_password)

        # 4) Mettre à jour le mot de passe
        try:
            self.user_repository.update_password(input_dto.user_id, input_dto.new_password)

            logger.info("ChangePassword: mot de passe changé pour user_id=%s", input_dto.user_id)

        except Exception as e:
            logger.exception("Erreur lors du changement de mot de passe")
            raise RepositoryError("Impossible de changer le mot de passe", original_error=e)
