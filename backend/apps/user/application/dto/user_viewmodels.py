# apps/user/application/dto/user_viewmodels.py
"""
ViewModels de sortie pour les use cases.
Structures prêtes pour présentation.
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass(frozen=True)
class ProfileViewModel:
    """Représentation d'un profil pour présentation."""

    first_name: Optional[str]
    last_name: Optional[str]
    birthday: Optional[date]
    phone: Optional[str]
    avatar_url: Optional[str]
    role: str
    full_name_display: str  # Nom complet formaté


@dataclass(frozen=True)
class UserViewModel:
    """Représentation d'un utilisateur pour présentation."""

    id: int
    email: str
    profile: ProfileViewModel
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class UserListViewModel:
    """Liste d'utilisateurs avec métadonnées."""

    users: list[UserViewModel]
    total_count: int


@dataclass(frozen=True)
class ProfessionalViewModel:
    """Représentation d'un professionnel pour présentation."""

    id: int
    user_id: int
    name: Optional[str]
    status_juridique: Optional[str]
    domaine_id: Optional[int]
    domaine_name: Optional[str]
    tjm_cents: int
    tjm_display: str  # Format "500.00"
    number_pro: Optional[str]
    service_type_ids: list[int]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class AuthTokensViewModel:
    """Tokens d'authentification."""

    access: str
    refresh: str
    user: UserViewModel
