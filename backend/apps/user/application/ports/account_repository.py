# apps/user/application/ports/account_repository.py
"""
Port (interface) pour l'accès aux données Account.
L'implémentation concrète (Django ORM) vivra dans adapters/persistence.
"""

from abc import abstractmethod
from typing import Protocol

from apps.user.domain.entities.account import Account


class AccountRepository(Protocol):
    """Interface pour la persistence des comptes professionnels."""

    @abstractmethod
    def create(self, account: Account) -> Account:
        """Créer et persister un nouveau compte."""
        ...

    @abstractmethod
    def get_by_id(self, account_id: int) -> Account | None:
        """Récupérer un compte par son ID."""
        ...

    @abstractmethod
    def get_by_user(self, user_id: int, include_inactive: bool = False) -> list[Account]:
        """
        Récupérer tous les comptes d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            include_inactive: Si True, inclut les comptes désactivés
        """
        ...

    @abstractmethod
    def update(self, account: Account) -> Account:
        """Mettre à jour un compte existant."""
        ...

    @abstractmethod
    def exists_by_name(self, user_id: int, display_name: str, exclude_id: int | None = None) -> bool:
        """
        Vérifier si un nom de compte existe (case-insensitive).

        Args:
            user_id: ID de l'utilisateur
            display_name: Nom à vérifier
            exclude_id: ID de compte à exclure (pour update)
        """
        ...

    @abstractmethod
    def has_quotes(self, account_id: int) -> bool:
        """Vérifier si le compte possède des devis."""
        ...

    @abstractmethod
    def count_active_clients(self, account_id: int) -> int:
        """Compter le nombre de clients actifs (non supprimés) d'un compte."""
        ...
