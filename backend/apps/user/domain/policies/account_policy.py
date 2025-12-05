# apps/user/domain/policies/account_policy.py
"""
Politiques métier pour les comptes professionnels (Account).
Règles pures, sans dépendance Django.
"""
import re
from typing import Optional

from apps.user.domain.errors import (
    DuplicateAccountNameError,
    InvalidDisplayNameError,
    InvalidDomainIdError,
    InvalidLegalFormError,
    InvalidLegalIdError,
)
from apps.user.domain.value_objects import LegalForm


class AccountPolicy:
    """
    Politique de validation des comptes professionnels.
    Contient les règles métier pures.
    """

    MIN_DISPLAY_NAME_LENGTH = 2
    MAX_DISPLAY_NAME_LENGTH = 255
    SIRET_LENGTH = 14
    VALID_LEGAL_FORMS = [form.value for form in LegalForm]

    @classmethod
    def validate_display_name(cls, name: str) -> None:
        """Valide le nom d'affichage."""
        if not name or not name.strip():
            raise InvalidDisplayNameError(name, "ne peut pas être vide")

        if len(name.strip()) < cls.MIN_DISPLAY_NAME_LENGTH:
            raise InvalidDisplayNameError(name, f"minimum {cls.MIN_DISPLAY_NAME_LENGTH} caractères")

        if len(name) > cls.MAX_DISPLAY_NAME_LENGTH:
            raise InvalidDisplayNameError(name, f"maximum {cls.MAX_DISPLAY_NAME_LENGTH} caractères")

    @classmethod
    def validate_legal_form(cls, legal_form: str | LegalForm) -> None:
        """Valide la forme juridique."""
        # Convert enum to string if needed
        form_value = legal_form.value if isinstance(legal_form, LegalForm) else legal_form

        if form_value not in cls.VALID_LEGAL_FORMS:
            raise InvalidLegalFormError(str(form_value))

    @classmethod
    def validate_legal_id(cls, legal_id: str | None) -> None:
        """
        Valide l'identifiant légal (SIRET).
        Format: exactement 14 chiffres.
        """
        # None or empty string is allowed (optional field)
        if not legal_id:
            return

        # Check exact length and numeric-only
        if not re.match(r"^[0-9]{14}$", legal_id):
            if len(legal_id) != cls.SIRET_LENGTH:
                raise InvalidLegalIdError(legal_id, f"doit contenir exactement {cls.SIRET_LENGTH} chiffres")
            else:
                raise InvalidLegalIdError(legal_id, "doit contenir uniquement des chiffres")

    @classmethod
    def validate_domain_id(cls, domain_id: int | None) -> None:
        """Valide l'ID du domaine d'activité."""
        if domain_id is None:
            return

        if domain_id <= 0:
            raise InvalidDomainIdError(domain_id)

    @classmethod
    def validate_account_data(
        cls,
        display_name: str,
        legal_form: str | LegalForm | None,
        legal_id: str | None = None,
        domain_id: int | None = None,
    ) -> None:
        """
        Valide toutes les données d'un compte.
        Lève une exception en cas d'erreur.
        """
        cls.validate_display_name(display_name)
        # legal_form is optional, will default to "micro" in use case
        if legal_form is not None:
            cls.validate_legal_form(legal_form)
        cls.validate_legal_id(legal_id)
        cls.validate_domain_id(domain_id)

    @classmethod
    def validate_unique_display_name(
        cls,
        user_id: int,
        display_name: str,
        existing_names: list[str],
        exclude_account_id: int | None = None,
    ) -> None:
        """
        Valide l'unicité du nom d'affichage (case-insensitive).

        Note: L'implémentation actuelle ne gère pas encore l'exclusion par ID
        car existing_names est une simple liste de strings sans les IDs.
        Dans la couche application/repository, on filtrera les noms existants
        en excluant le compte avec exclude_account_id AVANT d'appeler cette méthode.

        Args:
            user_id: ID de l'utilisateur
            display_name: Nom à valider
            existing_names: Liste des noms existants pour cet utilisateur
                           (déjà filtrée pour exclure exclude_account_id si fourni)
            exclude_account_id: ID du compte à exclure (pour update)
                               NOTE: Le filtrage doit être fait en amont
        """
        normalized_name = display_name.lower().strip()

        for existing in existing_names:
            if existing.lower().strip() == normalized_name:
                raise DuplicateAccountNameError(user_id, display_name)
