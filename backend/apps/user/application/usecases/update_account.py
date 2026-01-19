# apps/user/application/usecases/update_account.py
"""Use case: Mettre à jour un compte professionnel."""

from apps.user.application.dto.account_inputs import UpdateAccountInput
from apps.user.application.dto.account_viewmodels import AccountViewModel
from apps.user.application.ports.account_repository import AccountRepository
from apps.user.application.ports.clock import Clock
from apps.user.domain.errors import AccountNotFoundError, DuplicateAccountNameError
from apps.user.domain.policies.account_policy import AccountPolicy
from apps.user.domain.value_objects import LegalForm


class UpdateAccount:
    """Use case pour mettre à jour un compte."""

    def __init__(self, repository: AccountRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def execute(self, input_dto: UpdateAccountInput) -> AccountViewModel:
        """Mettre à jour un compte existant."""
        # 1. Validate input
        AccountPolicy.validate_account_data(
            display_name=input_dto.display_name,
            legal_form=input_dto.legal_form,
            legal_id=input_dto.legal_id,
            domain_id=input_dto.domain_id,
        )

        # 2. Fetch existing account
        account = self.repository.get_by_id(input_dto.account_id)
        if not account:
            raise AccountNotFoundError(input_dto.account_id)

        # 3. Check uniqueness (excluding self)
        if self.repository.exists_by_name(account.user_id, input_dto.display_name, exclude_id=input_dto.account_id):
            raise DuplicateAccountNameError(account.user_id, input_dto.display_name)

        # 4. Update entity fields
        account.display_name = input_dto.display_name
        account.legal_form = LegalForm(input_dto.legal_form)
        account.legal_id = input_dto.legal_id
        account.domain_id = input_dto.domain_id
        account.default_rate_cents = input_dto.default_rate_cents
        account.professional_headline = input_dto.professional_headline
        account.service_type_ids = input_dto.service_type_ids or []
        # Address fields
        account.address_line1 = input_dto.address_line1
        account.address_line2 = input_dto.address_line2
        account.city = input_dto.city
        account.postal_code = input_dto.postal_code
        account.country = input_dto.country
        account.updated_at = self.clock.now()

        # 5. Persist
        updated = self.repository.update(account)

        # 6. Return ViewModel
        return self._to_viewmodel(updated)

    def _to_viewmodel(self, account) -> AccountViewModel:
        """Convert Account entity to ViewModel."""
        return AccountViewModel(
            id=account.id,
            user_id=account.user_id,
            display_name=account.display_name,
            legal_form=account.legal_form.value,
            legal_id=account.legal_id,
            domain_id=account.domain_id,
            default_rate_cents=account.default_rate_cents,
            professional_headline=account.professional_headline,
            service_type_ids=account.service_type_ids,
            is_active=True,
            created_at=account.created_at,
            updated_at=account.updated_at,
            # Address fields
            address_line1=account.address_line1,
            address_line2=account.address_line2,
            city=account.city,
            postal_code=account.postal_code,
            country=account.country,
        )
