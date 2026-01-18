# apps/user/adapters/persistence/django_user_repository.py
"""
Implémentation Django des repositories user.
"""

import logging
from typing import Optional

from django.db import IntegrityError, transaction

from apps.user.application.errors import DuplicateEmailError, RepositoryError
from apps.user.application.ports.user_repository import UserRepository
from apps.user.models.models import Profile, User

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
            user.profile.refresh_from_db()  # AIDEV-NOTE: Refresh profile to avoid returning stale cached data

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
