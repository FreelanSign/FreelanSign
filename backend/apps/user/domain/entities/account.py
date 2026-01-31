# apps/user/domain/entities/account.py
"""
Entité Account du domaine user.

@version: 1.0
@author: @Bertrand2808
@since: 2025-11-25
"""

from dataclasses import dataclass, field
from datetime import datetime

from apps.user.domain.policies.account_policy import AccountPolicy
from apps.user.domain.value_objects import LegalForm


@dataclass
class Account:
    """
    Domain Entity pour un compte professionnel (entité freelance).
    Un utilisateur peut avoir plusieurs Accounts (multi-entity future).

    @author: @Bertrand2808
    @since: 2025-11-25
    @version: 1.0
    """

    id: int
    user_id: int
    display_name: str  # Nom affiché (maps from ProfessionalUser.name)
    legal_form: LegalForm  # Forme juridique (enum)
    legal_id: str | None  # SIRET (14 chiffres)
    domain_id: int | None  # FK vers catalog.Area
    is_active: bool
    created_at: datetime
    updated_at: datetime
    default_rate_cents: int | None = None
    professional_headline: str | None = None
    service_type_ids: list[int] = field(default_factory=list)
    # Address fields (feat/account-address)
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    postal_code: str | None = None
    country: str | None = None
    # Subscription plan and quota fields (v0.4.0+)
    plan: str = "beta"
    max_quotes_monthly: int | None = None
    max_clients: int | None = None

    def __post_init__(self):
        """Validation à la création."""
        # Valide display_name uniquement (les autres validations sont optionnelles
        # ou seront faites dans les use cases)
        AccountPolicy.validate_display_name(self.display_name)
