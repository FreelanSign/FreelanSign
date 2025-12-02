# apps/user/application/usecases/create_account.py
"""
Use case: Créer un nouveau compte professionnel.
"""
from apps.user.application.dto.account_inputs import CreateAccountInput
from apps.user.application.dto.account_viewmodels import AccountViewModel
from apps.user.application.ports.account_repository import AccountRepository
from apps.user.application.ports.clock import Clock
from apps.user.domain.entities.account import Account
from apps.user.domain.errors import DuplicateAccountNameError
from apps.user.domain.policies.account_policy import AccountPolicy
from apps.user.domain.value_objects import LegalForm


class CreateAccount:
    """
    Use case pour créer un compte professionnel.

    @author: @Bertrand2808
    @since: 2025-11-25
    @version: 1.0
    """

    def __init__(self, repository: AccountRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def execute(self, input_dto: CreateAccountInput) -> AccountViewModel:
        """
        Créer un nouveau compte professionnel.

        Args:
            input_dto: Données du compte à créer

        Returns:
            AccountViewModel du compte créé

        Raises:
            InvalidDisplayNameError: Nom invalide
            InvalidLegalFormError: Forme juridique invalide
            InvalidLegalIdError: SIRET invalide
            InvalidDomainIdError: Domain ID invalide
            DuplicateAccountNameError: Nom déjà utilisé
        """
        # 1. Validate input data
        AccountPolicy.validate_account_data(
            display_name=input_dto.display_name,
            legal_form=input_dto.legal_form,
            legal_id=input_dto.legal_id,
            domain_id=input_dto.domain_id,
        )

        # 2. Check uniqueness (case-insensitive)
        if self.repository.exists_by_name(input_dto.user_id, input_dto.display_name, None):
            raise DuplicateAccountNameError(input_dto.user_id, input_dto.display_name)

        # 3. Create Account entity
        now = self.clock.now()
        legal_form_enum = LegalForm(input_dto.legal_form)

        account = Account(
            id=0,  # Will be assigned by repository
            user_id=input_dto.user_id,
            display_name=input_dto.display_name,
            legal_form=legal_form_enum,
            legal_id=input_dto.legal_id,
            domain_id=input_dto.domain_id,
            default_rate_cents=input_dto.default_rate_cents,
            service_type_ids=input_dto.service_type_ids or [],
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        # 4. Persist
        created_account = self.repository.create(account)

        # 5. Return ViewModel
        return self._to_viewmodel(created_account)

    def _to_viewmodel(self, account: Account) -> AccountViewModel:
        """Convert Account entity to ViewModel."""
        return AccountViewModel(
            id=account.id,
            user_id=account.user_id,
            display_name=account.display_name,
            legal_form=account.legal_form.value,
            legal_id=account.legal_id,
            domain_id=account.domain_id,
            default_rate_cents=account.default_rate_cents,
            service_type_ids=account.service_type_ids,
            is_active=True,  # New accounts are active by default
            created_at=account.created_at,
            updated_at=account.updated_at,
        )
