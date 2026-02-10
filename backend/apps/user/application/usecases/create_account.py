# apps/user/application/usecases/create_account.py
"""
Use case: Créer un nouveau compte professionnel.
"""

import logging

from apps.user.application.dto.account_inputs import CreateAccountInput

logger = logging.getLogger(__name__)
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
        logger.info(
            f"[USE CASE] Starting CreateAccount for user_id={input_dto.user_id}, display_name={input_dto.display_name}"
        )
        logger.info(
            f"[USE CASE] Input: legal_form={input_dto.legal_form}, legal_id={input_dto.legal_id}, domain_id={input_dto.domain_id}"
        )

        # 1. Validate input data
        logger.info(f"[USE CASE] Step 1: Validating account data...")
        AccountPolicy.validate_account_data(
            display_name=input_dto.display_name,
            legal_form=input_dto.legal_form,
            legal_id=input_dto.legal_id,
            domain_id=input_dto.domain_id,
        )
        logger.info(f"[USE CASE] Step 1: Validation passed")

        # 2. Check uniqueness (case-insensitive)
        logger.info(f"[USE CASE] Step 2: Checking name uniqueness...")
        if self.repository.exists_by_name(input_dto.user_id, input_dto.display_name, None):
            logger.error(f"[USE CASE] Duplicate account name: {input_dto.display_name}")
            raise DuplicateAccountNameError(input_dto.user_id, input_dto.display_name)
        logger.info(f"[USE CASE] Step 2: Name is unique")

        # 3. Create Account entity
        logger.info(f"[USE CASE] Step 3: Creating Account entity...")
        now = self.clock.now()
        # Default to MICRO if legal_form is None
        legal_form_value = input_dto.legal_form if input_dto.legal_form else "micro"
        logger.info(f"[USE CASE] Legal form: {input_dto.legal_form} -> {legal_form_value}")
        legal_form_enum = LegalForm(legal_form_value)

        account = Account(
            id=0,  # Will be assigned by repository
            user_id=input_dto.user_id,
            display_name=input_dto.display_name,
            legal_form=legal_form_enum,
            legal_id=input_dto.legal_id,
            domain_id=input_dto.domain_id,
            default_rate_cents=input_dto.default_rate_cents,
            professional_headline=input_dto.professional_headline,
            service_type_ids=input_dto.service_type_ids or [],
            is_active=True,
            created_at=now,
            updated_at=now,
            # Address fields
            address_line1=input_dto.address_line1,
            address_line2=input_dto.address_line2,
            city=input_dto.city,
            postal_code=input_dto.postal_code,
            country=input_dto.country,
        )
        logger.info(f"[USE CASE] Step 3: Account entity created")

        # 4. Persist
        logger.info(f"[USE CASE] Step 4: Persisting to database...")
        created_account = self.repository.create(account)
        logger.info(f"[USE CASE] Step 4: Account persisted with id={created_account.id}")

        # 5. Return ViewModel
        logger.info(f"[USE CASE] Step 5: Converting to ViewModel")
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
            professional_headline=account.professional_headline,
            service_type_ids=account.service_type_ids,
            is_active=True,  # New accounts are active by default
            created_at=account.created_at,
            updated_at=account.updated_at,
            # Address fields
            address_line1=account.address_line1,
            address_line2=account.address_line2,
            city=account.city,
            postal_code=account.postal_code,
            country=account.country,
        )
