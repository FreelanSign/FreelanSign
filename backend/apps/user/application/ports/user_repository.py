# apps/user/application/ports/user_repository.py
"""
Ports des repositories pour le domaine user.
Interfaces abstraites utilisées par les use cases.
"""

from abc import ABC, abstractmethod
from typing import Optional


class UserRepository(ABC):
    """
    Port pour l'accès aux utilisateurs.
    Les use cases dépendent de cette interface, pas de l'implémentation Django.
    """

    @abstractmethod
    def get_by_id(self, user_id: int):
        """
        Récupère un utilisateur par son ID.

        Returns:
            Modèle User ou None
        """
        pass

    @abstractmethod
    def get_by_email(self, email: str):
        """
        Récupère un utilisateur par son email.

        Returns:
            Modèle User ou None
        """
        pass

    @abstractmethod
    def list_all(self):
        """
        Liste tous les utilisateurs.

        Returns:
            QuerySet de User
        """
        pass

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """
        Vérifie si un utilisateur existe avec cet email.

        Args:
            email: Email à vérifier

        Returns:
            True si existe
        """
        pass

    @abstractmethod
    def create(self, user_data: dict):
        """
        Crée un nouvel utilisateur avec profil.

        Args:
            user_data: Données de l'utilisateur et du profil

        Returns:
            Instance User créée

        Raises:
            RepositoryError en cas d'erreur
        """
        pass

    @abstractmethod
    def update_profile(self, user_id: int, profile_data: dict):
        """
        Met à jour le profil d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            profile_data: Données du profil à mettre à jour

        Returns:
            Instance User mise à jour
        """
        pass

    @abstractmethod
    def update_password(self, user_id: int, new_password: str):
        """
        Met à jour le mot de passe d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            new_password: Nouveau mot de passe (clair)
        """
        pass

    @abstractmethod
    def verify_password(self, user_id: int, password: str) -> bool:
        """
        Vérifie si un mot de passe est correct.

        Args:
            user_id: ID de l'utilisateur
            password: Mot de passe à vérifier

        Returns:
            True si correct
        """
        pass

    @abstractmethod
    def delete(self, user_id: int):
        """Supprime un utilisateur."""
        pass
