# apps/user/application/dto/user_viewmodels.py
"""
ViewModels de sortie pour les use cases.
Structures prêtes pour présentation.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ProfileViewModel:
    """Représentation d'un profil pour présentation."""

    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    avatar_url: Optional[str]
    role: str
    full_name_display: str


@dataclass(frozen=True)
class UserViewModel:
    """Représentation d'un utilisateur pour présentation."""

    id: int
    email: str
    email_verified: bool
    profile: ProfileViewModel
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class UserListViewModel:
    """Liste d'utilisateurs avec métadonnées."""

    users: list[UserViewModel]
    total_count: int


@dataclass(frozen=True)
class AuthTokensViewModel:
    """Tokens d'authentification."""

    access: str
    refresh: str
    user: UserViewModel
