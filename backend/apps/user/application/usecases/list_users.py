# apps/user/application/usecases/list_users.py
"""
Use case: Lister les utilisateurs.
"""

import logging

from apps.user.application.dto.user_viewmodels import ProfileViewModel, UserListViewModel, UserViewModel
from apps.user.application.ports.user_repository import UserRepository
from apps.user.domain.services.user_calculator import UserCalculator

logger = logging.getLogger(__name__)


class ListUsers:
    """
    Use case: Lister les utilisateurs.
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self) -> UserListViewModel:
        """
        Exécute le use case.

        Returns:
            UserListViewModel

        Raises:
            RepositoryError: En cas d'erreur d'acces aux données
        """
        logger.info("ListUsers")
        qs = self.user_repository.list_all()
        users = []
        for u in qs:
            p = u.profile
            users.append(
                UserViewModel(
                    id=u.id,
                    email=u.email,
                    profile=ProfileViewModel(
                        first_name=p.first_name,
                        last_name=p.last_name,
                        phone=p.phone,
                        avatar_url=p.avatar_url,
                        role=p.role,
                        full_name_display=UserCalculator.format_full_name(p.first_name or "", p.last_name or ""),
                    ),
                    created_at=u.date_joined,
                    updated_at=p.updated_at,
                )
            )
        return UserListViewModel(users=users, total_count=len(users))
