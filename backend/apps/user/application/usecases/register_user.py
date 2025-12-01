# apps/user/application/usecases/register_user.py
"""
Use case: Enregistrer un nouvel utilisateur.
"""
import logging

from apps.user.application.dto.user_inputs import RegisterUserInput
from apps.user.application.dto.user_viewmodels import (
    ProfileViewModel,
    UserViewModel,
)
from apps.user.application.errors import (
    DuplicateEmailError,
    RepositoryError,
)
from apps.user.application.ports.user_repository import UserRepository
from apps.user.domain.policies.user_policy import ProfilePolicy, UserPolicy
from apps.user.domain.services.user_calculator import UserCalculator

logger = logging.getLogger(__name__)


class RegisterUser:
    """
    Use case: Créer un nouvel utilisateur avec son profil.
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, input_dto: RegisterUserInput) -> UserViewModel:
        """
        Exécute le use case.

        Args:
            input_dto: Données d'enregistrement

        Returns:
            UserViewModel

        Raises:
            InvalidEmailError: Email invalide
            InvalidPasswordError: Mot de passe invalide
            DuplicateEmailError: Email déjà utilisé
            UnauthorizedRoleAssignmentError: Rôle non autorisé
            RepositoryError: Erreur technique
        """
        logger.info("RegisterUser: email=%s", input_dto.email)

        # 1) Validation des règles métier
        email_clean = UserPolicy.validate_email(input_dto.email)
        UserPolicy.validate_password(input_dto.password)

        # Valider le rôle (empêcher auto-assignation admin)
        role = input_dto.role or "freelance"
        if role == "admin":
            logger.warning("RegisterUser: tentative d'auto-assignation admin, forcing freelance")
            role = "freelance"

        UserPolicy.validate_role_assignment(role, assigner_is_staff=False)

        # Validation du téléphone si fourni
        if input_dto.phone:
            UserPolicy.validate_phone(input_dto.phone)

        # Validation des noms
        if input_dto.first_name:
            ProfilePolicy.validate_name(input_dto.first_name, "first_name")
        if input_dto.last_name:
            ProfilePolicy.validate_name(input_dto.last_name, "last_name")

        # 2) Vérifier que l'email n'existe pas déjà
        if self.user_repository.exists_by_email(email_clean):
            logger.warning("RegisterUser: email déjà utilisé: %s", email_clean)
            raise DuplicateEmailError(email_clean)

        # 3) Créer l'utilisateur via le repository
        try:
            user_data = {
                "email": email_clean,
                "password": input_dto.password,
                "profile": {
                    "first_name": input_dto.first_name or "",
                    "last_name": input_dto.last_name or "",
                    "phone": input_dto.phone or "",
                    "avatar_url": input_dto.avatar_url or "",
                    "role": role,
                },
            }

            user = self.user_repository.create(user_data)

            logger.info("RegisterUser: utilisateur créé id=%s", user.id)

            return self._to_viewmodel(user)

        except Exception as e:
            logger.exception("Erreur lors de la création de l'utilisateur")
            raise RepositoryError("Impossible de créer l'utilisateur", original_error=e)

    def _to_viewmodel(self, user) -> UserViewModel:
        """Convertit un User en ViewModel."""
        profile = user.profile

        return UserViewModel(
            id=user.id,
            email=user.email,
            profile=ProfileViewModel(
                first_name=profile.first_name,
                last_name=profile.last_name,
                phone=profile.phone,
                avatar_url=profile.avatar_url,
                role=profile.role,
                full_name_display=UserCalculator.format_full_name(profile.first_name or "", profile.last_name or ""),
            ),
            created_at=user.date_joined,
            updated_at=profile.updated_at,
        )
