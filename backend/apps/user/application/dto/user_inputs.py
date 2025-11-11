# apps/user/application/dto/user_inputs.py
"""
DTOs d'entrée pour les use cases d'utilisateurs.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class RegisterUserInput:
    """Données pour enregistrer un nouvel utilisateur."""

    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    avatar_url: Optional[str] = None
    role: str = "freelance"
    # Legacy support
    full_name: Optional[str] = None


@dataclass(frozen=True)
class UpdateProfileInput:
    """Données pour mettre à jour un profil."""

    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
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
class CreateProfessionalInput:
    """Données pour créer un profil professionnel."""

    user_id: int
    name: Optional[str] = None
    status_juridique: Optional[str] = None
    domaine_id: Optional[int] = None
    tjm_cents: int = 0
    number_pro: Optional[str] = None
    service_type_ids: Optional[list[int]] = None


@dataclass(frozen=True)
class UpdateProfessionalInput:
    """Données pour mettre à jour un profil professionnel."""

    professional_id: int
    user_id: int  # Pour vérifier les droits
    name: Optional[str] = None
    status_juridique: Optional[str] = None
    domaine_id: Optional[int] = None
    tjm_cents: Optional[int] = None
    number_pro: Optional[str] = None
    service_type_ids: Optional[list[int]] = None
    updater_is_staff: bool = False


@dataclass(frozen=True)
class GetProfessionalInput:
    """Paramètres pour récupérer un professionnel."""

    user_id: Optional[int] = None
    professional_id: Optional[int] = None


@dataclass(frozen=True)
class ResetPasswordInput:
    """Paramètres pour mettre à jour un mot de passe."""

    token: str
    new_password: str
