# apps/user/application/dto/account_inputs.py
"""
Input DTOs pour les use cases Account.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class CreateAccountInput:
    """Input pour créer un nouveau compte professionnel."""

    user_id: int
    display_name: str
    legal_form: str  # Sera converti en LegalForm enum
    legal_id: str | None = None
    domain_id: int | None = None


@dataclass(frozen=True)
class UpdateAccountInput:
    """Input pour mettre à jour un compte existant."""

    account_id: int
    display_name: str
    legal_form: str
    legal_id: str | None = None
    domain_id: int | None = None
