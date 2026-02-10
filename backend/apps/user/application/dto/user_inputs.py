# apps/user/application/dto/user_inputs.py
"""
DTOs d'entrée pour les use cases d'utilisateurs.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RegisterUserInput:
    """Données pour enregistrer un nouvel utilisateur."""

    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str = "freelance"


@dataclass(frozen=True)
class UpdateProfileInput:
    """Données pour mettre à jour un profil."""

    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[str] = None
    # Contexte pour valider les droits
    updater_is_staff: bool = False


@dataclass(frozen=True)
class ChangePasswordInput:
    """Données pour changer le mot de passe."""

    user_id: int
    current_password: str
    new_password: str


@dataclass(frozen=True)
class GetUserInput:
    """Paramètres pour récupérer un utilisateur."""

    user_id: int


@dataclass(frozen=True)
class ResetPasswordInput:
    """Paramètres pour mettre à jour un mot de passe."""

    token: str
    new_password: str
