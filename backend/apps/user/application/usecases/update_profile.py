# apps/user/application/usecases/update_profile.py
"""
Use case: Mettre à jour le profil d'un utilisateur.
"""
import logging

from apps.user.application.dto.user_inputs import UpdateProfileInput
from apps.user.application.dto.user_viewmodels import (
    ProfileViewModel,
    UserViewModel,
)
from apps.user.application.errors import (
    ProfileNotFoundError,
    RepositoryError,
    UserNotFoundError,
)
from apps.user.application.ports.user_repository import UserRepository
from apps.user.domain.policies.user_policy import ProfilePolicy, UserPolicy
from apps.user.domain.services.user_calculator import UserCalculator

logger = logging.getLogger(__name__)


class UpdateProfile:
    """
    Use case: Mettre à jour le profil d'un utilisateur.
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, input_dto: UpdateProfileInput) -> UserViewModel:
        """
        Exécute le use case.

        Args:
            input_dto: Données de mise à jour

        Returns:
            UserViewModel

        Raises:
            UserNotFoundError: Utilisateur introuvable
            InvalidPhoneError: Téléphone invalide
            InvalidNameError: Nom invalide
            UnauthorizedRoleAssignmentError: Attribution de rôle non autorisée
            RepositoryError: Erreur technique
        """
        logger.info("UpdateProfile: user_id=%s", input_dto.user_id)

        # 1) Vérifier que l'utilisateur existe
        user = self.user_repository.get_by_id(input_dto.user_id)
        if not user:
            raise UserNotFoundError(user_id=input_dto.user_id)

        if not hasattr(user, "profile") or not user.profile:
            raise ProfileNotFoundError(user_id=input_dto.user_id)

        # 2) Construire les données à mettre à jour (seulement les champs fournis)
        profile_data = {}

        if input_dto.first_name is not None:
            ProfilePolicy.validate_name(input_dto.first_name, "first_name")
            profile_data["first_name"] = input_dto.first_name

        if input_dto.last_name is not None:
            ProfilePolicy.validate_name(input_dto.last_name, "last_name")
            profile_data["last_name"] = input_dto.last_name

        if input_dto.phone is not None:
            UserPolicy.validate_phone(input_dto.phone)
            profile_data["phone"] = input_dto.phone

        if input_dto.birthday is not None:
            profile_data["birthday"] = input_dto.birthday

        if input_dto.avatar_url is not None:
            profile_data["avatar_url"] = input_dto.avatar_url

        # Validation spéciale pour le rôle (droits requis)
        if input_dto.role is not None:
            UserPolicy.validate_role_assignment(input_dto.role, assigner_is_staff=input_dto.updater_is_staff)
            profile_data["role"] = input_dto.role

        # 3) Mettre à jour via le repository
        if not profile_data:
            logger.info("UpdateProfile: aucune donnée à mettre à jour")
            return self._to_viewmodel(user)

        try:
            user = self.user_repository.update_profile(input_dto.user_id, profile_data)

            logger.info("UpdateProfile: profil mis à jour pour user_id=%s", input_dto.user_id)

            return self._to_viewmodel(user)

        except Exception as e:
            logger.exception("Erreur lors de la mise à jour du profil")
            raise RepositoryError("Impossible de mettre à jour le profil", original_error=e)

    def _to_viewmodel(self, user) -> UserViewModel:
        """Convertit un User en ViewModel."""
        profile = user.profile

        return UserViewModel(
            id=user.id,
            email=user.email,
            profile=ProfileViewModel(
                first_name=profile.first_name,
                last_name=profile.last_name,
                birthday=profile.birthday,
                phone=profile.phone,
                avatar_url=profile.avatar_url,
                role=profile.role,
                full_name_display=UserCalculator.format_full_name(profile.first_name or "", profile.last_name or ""),
            ),
            created_at=user.date_joined,
            updated_at=profile.updated_at,
        )
