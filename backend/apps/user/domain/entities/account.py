# apps/user/domain/entities/account.py
"""
Entité Account du domaine user.
"""
from dataclasses import dataclass
from datetime import datetime

from apps.user.domain.policies.account_policy import AccountPolicy
from apps.user.domain.value_objects import LegalForm


@dataclass
class Account:
    """
    Domain Entity pour un compte professionnel (entité freelance).
    Un utilisateur peut avoir plusieurs Accounts (multi-entity future).
    """

    id: int
    user_id: int
    display_name: str  # Nom affiché (maps from ProfessionalUser.name)
    legal_form: LegalForm  # Forme juridique (enum)
    legal_id: str | None  # SIRET (14 chiffres)
    domain_id: int | None  # FK vers catalog.Area
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        """Validation à la création."""
        # Valide display_name uniquement (les autres validations sont optionnelles
        # ou seront faites dans les use cases)
        AccountPolicy.validate_display_name(self.display_name)
