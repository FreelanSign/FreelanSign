# apps/user/adapters/persistence/django_user_repository.py
"""
Implémentation Django des repositories user.
"""
import logging
from typing import Optional

from django.db import IntegrityError, transaction

from apps.user.application.errors import DuplicateEmailError, RepositoryError
from apps.user.application.ports.user_repository import (
    ProfessionalRepository,
    UserRepository,
)
from apps.user.models.models import ProfessionalUser, Profile, User

logger = logging.getLogger(__name__)


class DjangoUserRepository(UserRepository):
    """
    Implémentation concrète du repository User avec Django ORM.
    """

    def get_by_id(self, user_id: int):
        """Récupère un utilisateur par ID."""
        try:
            return User.objects.select_related("profile").get(id=user_id)
        except User.DoesNotExist:
            return None
        except Exception as e:
            logger.exception("Erreur lors de get_by_id(%s)", user_id)
            raise RepositoryError(f"Erreur technique lors de la récupération de l'utilisateur {user_id}", original_error=e)

    def get_by_email(self, email: str):
        """Récupère un utilisateur par email."""
        try:
            email_clean = email.strip().lower()
            return User.objects.select_related("profile").get(email=email_clean)
        except User.DoesNotExist:
            return None
        except Exception as e:
            logger.exception("Erreur lors de get_by_email(%s)", email)
            raise RepositoryError(f"Erreur technique lors de la récupération de l'utilisateur", original_error=e)

    def list_all(self):
        """Liste tous les utilisateurs."""
        try:
            return User.objects.select_related("profile").all()
        except Exception as e:
            logger.exception("Erreur lors du listing des utilisateurs")
            raise RepositoryError("Erreur technique lors du listing des utilisateurs", original_error=e)

    def exists_by_email(self, email: str) -> bool:
        """Vérifie si un utilisateur existe avec cet email."""
        try:
            email_clean = email.strip().lower()
            return User.objects.filter(email=email_clean).exists()
        except Exception as e:
            logger.exception("Erreur lors de exists_by_email")
            raise RepositoryError("Erreur technique lors de la vérification d'existence", original_error=e)

    @transaction.atomic
    def create(self, user_data: dict):
        """Crée un nouvel utilisateur avec profil."""
        try:
            profile_data = user_data.pop("profile", {})
            password = user_data.pop("password")
            email = user_data.pop("email")

            # Créer l'utilisateur
            user = User.objects.create_user(email=email, password=password, **user_data)

            # Créer le profil
            Profile.objects.create(user=user, **profile_data)

            return user

        except IntegrityError as e:
            logger.warning("IntegrityError lors de la création: %s", str(e))
            # Vérifier si c'est un email dupliqué
            if "email" in str(e).lower() or "uniq_user_email" in str(e).lower():
                raise DuplicateEmailError(email)
            raise RepositoryError("Erreur d'intégrité lors de la création", original_error=e)

        except Exception as e:
            logger.exception("Erreur lors de la création de l'utilisateur")
            raise RepositoryError("Erreur technique lors de la création de l'utilisateur", original_error=e)

    def update_profile(self, user_id: int, profile_data: dict):
        """Met à jour le profil d'un utilisateur."""
        try:
            user = self.get_by_id(user_id)
            if not user:
                raise RepositoryError(f"Utilisateur {user_id} introuvable")

            if not hasattr(user, "profile") or not user.profile:
                raise RepositoryError(f"Profil introuvable pour utilisateur {user_id}")

            # Mettre à jour les champs du profil
            for key, value in profile_data.items():
                setattr(user.profile, key, value)

            user.profile.save()
            user.refresh_from_db()

            return user

        except RepositoryError:
            raise
        except Exception as e:
            logger.exception("Erreur lors de la mise à jour du profil")
            raise RepositoryError(f"Erreur technique lors de la mise à jour du profil {user_id}", original_error=e)

    def update_password(self, user_id: int, new_password: str):
        """Met à jour le mot de passe d'un utilisateur."""
        try:
            user = self.get_by_id(user_id)
            if not user:
                raise RepositoryError(f"Utilisateur {user_id} introuvable")

            user.set_password(new_password)
            user.save()

        except RepositoryError:
            raise
        except Exception as e:
            logger.exception("Erreur lors de la mise à jour du mot de passe")
            raise RepositoryError(f"Erreur technique lors de la mise à jour du mot de passe", original_error=e)

    def verify_password(self, user_id: int, password: str) -> bool:
        """Vérifie si un mot de passe est correct."""
        try:
            user = self.get_by_id(user_id)
            if not user:
                return False

            return user.check_password(password)

        except Exception as e:
            logger.exception("Erreur lors de la vérification du mot de passe")
            return False

    def delete(self, user_id: int):
        """Supprime un utilisateur."""
        try:
            return User.objects.filter(id=user_id).delete()
        except Exception as e:
            logger.exception("Erreur lors de la suppression de l'utilisateur")
            raise RepositoryError(f"Erreur technique lors de la suppression de l'utilisateur {user_id}", original_error=e)


class DjangoProfessionalRepository(ProfessionalRepository):
    """
    Implémentation concrète du repository Professional avec Django ORM.
    """

    def get_by_id(self, professional_id: int):
        """Récupère un professionnel par ID."""
        try:
            return (
                ProfessionalUser.objects.select_related("user", "domaine")
                .prefetch_related("service_types")
                .get(id=professional_id)
            )
        except ProfessionalUser.DoesNotExist:
            return None
        except Exception as e:
            logger.exception("Erreur lors de get_by_id professional(%s)", professional_id)
            raise RepositoryError(
                f"Erreur technique lors de la récupération du professionnel {professional_id}", original_error=e
            )

    def get_by_user_id(self, user_id: int):
        """Récupère un professionnel par l'ID de l'utilisateur."""
        try:
            return (
                ProfessionalUser.objects.select_related("user", "domaine")
                .prefetch_related("service_types")
                .get(user_id=user_id)
            )
        except ProfessionalUser.DoesNotExist:
            return None
        except Exception as e:
            logger.exception("Erreur lors de get_by_user_id(%s)", user_id)
            raise RepositoryError(f"Erreur technique lors de la récupération du professionnel", original_error=e)

    def list_all(self, user_id: Optional[int] = None):
        """Liste tous les professionnels."""
        try:
            qs = ProfessionalUser.objects.select_related("user", "domaine").prefetch_related("service_types").all()

            if user_id is not None:
                qs = qs.filter(user_id=user_id)

            return qs
        except Exception as e:
            logger.exception("Erreur lors du listing des professionnels")
            raise RepositoryError("Erreur technique lors du listing des professionnels", original_error=e)

    def exists_for_user(self, user_id: int) -> bool:
        """Vérifie si un profil professionnel existe pour cet utilisateur."""
        try:
            return ProfessionalUser.objects.filter(user_id=user_id).exists()
        except Exception as e:
            logger.exception("Erreur lors de exists_for_user")
            raise RepositoryError("Erreur technique lors de la vérification d'existence", original_error=e)

    def create(self, professional_data: dict):
        """Crée un nouveau profil professionnel."""
        try:
            service_type_ids = professional_data.pop("service_type_ids", [])

            professional = ProfessionalUser.objects.create(**professional_data)

            if service_type_ids:
                professional.service_types.set(service_type_ids)

            return professional

        except Exception as e:
            logger.exception("Erreur lors de la création du professionnel")
            raise RepositoryError("Erreur technique lors de la création du professionnel", original_error=e)

    def update(self, professional_id: int, professional_data: dict):
        """Met à jour un profil professionnel."""
        try:
            professional = self.get_by_id(professional_id)
            if not professional:
                raise RepositoryError(f"Professionnel {professional_id} introuvable")

            service_type_ids = professional_data.pop("service_type_ids", None)

            # 🔍 DEBUG
            logger.info(
                "Repository update: professional_id=%s, service_type_ids=%s",
                professional_id,
                service_type_ids,
            )

            # Mettre à jour les champs
            for key, value in professional_data.items():
                if value is not None:
                    setattr(professional, key, value)

            professional.save()

            # Mettre à jour les service_types si fournis
            if service_type_ids is not None:
                logger.info("Repository: calling service_types.set(%s)", service_type_ids)
                professional.service_types.set(service_type_ids)
                # 🔍 Vérifier immédiatement après
                actual = list(professional.service_types.values_list("id", flat=True))
                logger.info("Repository: after set(), actual service_types=%s", actual)

            professional.refresh_from_db()

            return professional
        except Exception as e:
            logger.exception("Erreur lors de la mise à jour du professionnel")
            raise RepositoryError("Erreur technique lors de la mise à jour du professionnel", original_error=e)

    def delete(self, professional_id: int):
        """Supprime un profil professionnel."""
        try:
            return ProfessionalUser.objects.filter(id=professional_id).delete()
        except Exception as e:
            logger.exception("Erreur lors de la suppression du professionnel")
            raise RepositoryError(
                f"Erreur technique lors de la suppression du professionnel {professional_id}", original_error=e
            )
