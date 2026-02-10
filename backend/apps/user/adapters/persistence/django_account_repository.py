# apps/user/adapters/persistence/django_account_repository.py
"""
Django ORM implementation of AccountRepository port.

@author: @Bertrand2808
@since: 2025-11-25
@version: 1.0
"""

from django.db.models import Q
from django.db.models.functions import Lower

from apps.user.application.ports.account_repository import AccountRepository
from apps.user.domain.entities.account import Account as AccountEntity
from apps.user.domain.value_objects import LegalForm
from apps.user.models.account import Account as AccountModel


class DjangoAccountRepository:
    # DESIGN: Important d'implémenter le port pour :
    # - garantir la signature (linter / IDE)
    # - déplacer la logique d'évolution au niveau du port, pas du repo
    """Implementation of AccountRepository using Django ORM."""

    def create(self, account: AccountEntity) -> AccountEntity:
        """Create and persist a new account."""
        model = AccountModel.objects.create(
            user_id=account.user_id,
            display_name=account.display_name,
            legal_form=account.legal_form.value,
            legal_id=account.legal_id,
            domain_id=account.domain_id,
            default_rate_cents=account.default_rate_cents,
            professional_headline=account.professional_headline,
            is_active=account.is_active,
            created_at=account.created_at,
            updated_at=account.updated_at,
            # Address fields
            address_line1=account.address_line1 or "",
            address_line2=account.address_line2 or "",
            city=account.city or "",
            postal_code=account.postal_code or "",
            country=account.country or "",
            # Subscription plan
            plan=account.plan,
            max_quotes_monthly=account.max_quotes_monthly,
            max_clients=account.max_clients,
        )
        # Set M2M relationship for service_types
        if account.service_type_ids:
            model.service_types.set(account.service_type_ids)
        return self._to_entity(model)

    def get_by_id(self, account_id: int) -> AccountEntity | None:
        """Retrieve account by ID."""
        try:
            model = AccountModel.objects.get(id=account_id)
            return self._to_entity(model)
        except AccountModel.DoesNotExist:
            return None

    def get_by_user(self, user_id: int, include_inactive: bool = False) -> list[AccountEntity]:
        """Retrieve all accounts for a user."""
        queryset = AccountModel.objects.filter(user_id=user_id)

        if not include_inactive:
            queryset = queryset.filter(is_active=True)

        return [self._to_entity(model) for model in queryset]

    def update(self, account: AccountEntity) -> AccountEntity:
        """Update an existing account."""
        model = AccountModel.objects.get(id=account.id)
        model.display_name = account.display_name
        model.legal_form = account.legal_form.value
        model.legal_id = account.legal_id
        model.domain_id = account.domain_id
        model.default_rate_cents = account.default_rate_cents
        model.professional_headline = account.professional_headline
        model.is_active = account.is_active
        model.updated_at = account.updated_at
        # Address fields
        model.address_line1 = account.address_line1 or ""
        model.address_line2 = account.address_line2 or ""
        model.city = account.city or ""
        model.postal_code = account.postal_code or ""
        model.country = account.country or ""
        # Subscription plan
        model.plan = account.plan
        model.max_quotes_monthly = account.max_quotes_monthly
        model.max_clients = account.max_clients
        model.save()
        # Update M2M relationship for service_types
        model.service_types.set(account.service_type_ids)
        return self._to_entity(model)

    def exists_by_name(self, user_id: int, display_name: str, exclude_id: int | None = None) -> bool:
        """Check if account name exists (case-insensitive)."""
        queryset = (
            AccountModel.objects.filter(user_id=user_id)
            .annotate(lower_name=Lower("display_name"))
            .filter(lower_name=display_name.lower())
        )

        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)

        return queryset.exists()

    def has_quotes(self, account_id: int) -> bool:
        """Check if account has associated quotes."""
        # Import locally to avoid circular dependency
        from apps.quote.models import Quote

        # DESIGN-SMELL (Phase 3 - Temporary):
        # - Cross-module coupling: AccountRepository → Quote.models
        # - Uses owner_id instead of account_id (workaround)
        #
        # DECISION (Phase 4 refactoring):
        # ✅ Remove has_quotes from AccountRepository port
        # ✅ Add exists_for_account(account_id) to QuoteRepository
        # ✅ Inject QuoteRepository into DeactivateAccount use case
        # ✅ Keep repositories within their bounded contexts
        #
        # Rationale:
        # - SRP: AccountRepository should only manage accounts
        # - Cross-context constraints belong in Application layer (use case)
        # - Better testability (mock QuoteRepository)
        # - Cleaner separation of bounded contexts
        # For now check by owner (ProfessionalUser pattern)
        # In Phase 5, this will check Quote.account_id
        account = AccountModel.objects.get(id=account_id)
        return Quote.objects.filter(owner_id=account.user_id).exists()

    def count_active_clients(self, account_id: int) -> int:
        """Count active (non-deleted) clients for account."""
        from apps.client.models import Client

        return Client.objects.filter(owner_id=account_id, is_deleted=False).count()

    def _to_entity(self, model: AccountModel) -> AccountEntity:
        """Convert Django model to domain entity."""
        return AccountEntity(
            id=model.id,
            user_id=model.user_id,
            display_name=model.display_name,
            legal_form=LegalForm(model.legal_form) if model.legal_form else LegalForm.MICRO,
            legal_id=model.legal_id,
            domain_id=model.domain_id,
            default_rate_cents=model.default_rate_cents,
            professional_headline=model.professional_headline,
            service_type_ids=list(model.service_types.values_list("id", flat=True)),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            # Address fields
            address_line1=model.address_line1 or None,
            address_line2=model.address_line2 or None,
            city=model.city or None,
            postal_code=model.postal_code or None,
            country=model.country or None,
            # Subscription plan
            plan=model.plan,
            max_quotes_monthly=model.max_quotes_monthly,
            max_clients=model.max_clients,
        )
