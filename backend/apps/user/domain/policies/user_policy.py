# apps/user/domain/policies/user_policy.py
"""
Politiques métier pour les utilisateurs.
Règles pures, sans dépendance Django.
"""

import re
from typing import Optional

from apps.user.domain.errors import (
    InvalidEmailError,
    InvalidNameError,
    InvalidPasswordError,
    InvalidPhoneError,
    InvalidRoleError,
    InvalidTJMError,
    UnauthorizedRoleAssignmentError,
)


class UserRole:
    """Rôles possibles pour un utilisateur."""

    FREELANCE = "freelance"
    ADMIN = "admin"

    ALL_ROLES = [FREELANCE, ADMIN]


class UserPolicy:
    """
    Politique de validation des utilisateurs.
    Contient les règles métier pures.
    """

    MIN_PASSWORD_LENGTH = 8
    MIN_NAME_LENGTH = 1
    MAX_NAME_LENGTH = 255
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    PHONE_REGEX = re.compile(r"^\+?[0-9\s\-\(\)]{8,20}$")

    @classmethod
    def validate_email(cls, email: str) -> str:
        """
        Valide et normalise un email.

        Returns:
            Email normalisé (lowercase, stripped)

        Raises:
            InvalidEmailError si invalide
        """
        if not email or not email.strip():
            raise InvalidEmailError(email)

        email_clean = email.strip().lower()

        if not cls.EMAIL_REGEX.match(email_clean):
            raise InvalidEmailError(email)

        return email_clean

    @classmethod
    def validate_password(cls, password: str) -> None:
        """Valide un mot de passe."""
        if not password:
            raise InvalidPasswordError("Le mot de passe ne peut pas être vide")

        if len(password) < cls.MIN_PASSWORD_LENGTH:
            raise InvalidPasswordError(f"Minimum {cls.MIN_PASSWORD_LENGTH} caractères requis")

        # Règles de complexité (optionnel, à adapter selon besoins)
        has_digit = any(c.isdigit() for c in password)
        has_letter = any(c.isalpha() for c in password)

        if not (has_digit and has_letter):
            raise InvalidPasswordError("Le mot de passe doit contenir au moins une lettre et un chiffre")

    @classmethod
    def validate_phone(cls, phone: str) -> None:
        """Valide un numéro de téléphone."""
        if not phone:
            return  # Optionnel

        phone_clean = phone.strip()

        if not cls.PHONE_REGEX.match(phone_clean):
            raise InvalidPhoneError(phone)

    @classmethod
    def validate_role(cls, role: str) -> None:
        """Valide qu'un rôle est autorisé."""
        if role not in UserRole.ALL_ROLES:
            raise InvalidRoleError(role)

    @classmethod
    def can_assign_role(cls, role: str, assigner_is_staff: bool = False) -> bool:
        """
        Vérifie si un rôle peut être assigné.

        Args:
            role: Rôle à assigner
            assigner_is_staff: Si l'assigneur est staff

        Returns:
            True si l'attribution est autorisée
        """
        if role == UserRole.ADMIN:
            return assigner_is_staff

        return True  # FREELANCE peut être assigné par tous

    @classmethod
    def validate_role_assignment(cls, role: str, assigner_is_staff: bool = False) -> None:
        """
        Valide une attribution de rôle.

        Raises:
            UnauthorizedRoleAssignmentError si non autorisé
        """
        cls.validate_role(role)

        if not cls.can_assign_role(role, assigner_is_staff):
            raise UnauthorizedRoleAssignmentError(role, "Seul un staff peut assigner le rôle admin")


class ProfilePolicy:
    """Politique de validation des profils."""

    MIN_NAME_LENGTH = 1
    MAX_NAME_LENGTH = 255

    @classmethod
    def validate_name(cls, name: str, field: str = "name") -> None:
        """Valide un nom (first_name, last_name, etc.)."""
        if not name:
            return  # Optionnel

        name_clean = name.strip()

        if len(name_clean) < cls.MIN_NAME_LENGTH:
            raise InvalidNameError(name, field)

        if len(name) > cls.MAX_NAME_LENGTH:
            raise InvalidNameError(f"{name[:50]}... (trop long)", field)

    @classmethod
    def split_full_name(cls, full_name: str) -> tuple[str, str]:
        """
        Divise un nom complet en prénom et nom.

        Returns:
            (first_name, last_name)
        """
        parts = (full_name or "").strip().split()
        if not parts:
            return "", ""
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], " ".join(parts[1:])


class ProfessionalPolicy:
    """Politique de validation des professionnels."""

    MIN_TJM_CENTS = 0
    VALID_STATUS_JURIDIQUE = ["micro", "eirl", "eurl", "sasu", "other"]

    @classmethod
    def validate_tjm_cents(cls, tjm_cents: int) -> None:
        """Valide le TJM en centimes."""
        if tjm_cents < cls.MIN_TJM_CENTS:
            raise InvalidTJMError(tjm_cents)

    @classmethod
    def validate_status_juridique(cls, status: str) -> None:
        """Valide le statut juridique."""
        if not status:
            return  # Optionnel

        if status not in cls.VALID_STATUS_JURIDIQUE:
            from apps.user.domain.errors import InvalidStatusJuridiqueError

            raise InvalidStatusJuridiqueError(status)
