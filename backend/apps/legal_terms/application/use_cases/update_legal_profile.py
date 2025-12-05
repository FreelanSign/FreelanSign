"""
Use case for updating legal profile.
"""

from apps.legal_terms.application.dtos.legal_profile_dto import (
    LegalProfileDTO,
    UpdateClauseInput,
)
from apps.legal_terms.application.ports.legal_profile_repository import (
    LegalProfileRepository,
)
from apps.legal_terms.application.ports.legal_template_repository import (
    LegalTemplateRepository,
)
from apps.legal_terms.domain.exceptions import ClauseNotFoundError, ProfileNotFoundError


class UpdateLegalProfileUseCase:
    """Use case for updating legal profile clause overrides."""

    def __init__(
        self,
        profile_repository: LegalProfileRepository,
        template_repository: LegalTemplateRepository,
    ):
        self.profile_repository = profile_repository
        self.template_repository = template_repository

    def execute(self, account_id: str, updates: list[UpdateClauseInput]) -> LegalProfileDTO:
        """
        Update legal profile with clause overrides.
        Validates clauses exist in template.
        """
        # Get profile
        profile = self.profile_repository.get_by_account(account_id)
        if not profile:
            raise ProfileNotFoundError(account_id)

        # Get template to validate clauses
        template = self.template_repository.get_by_id(profile.template_id)
        if not template:
            raise ValueError(f"Template {profile.template_id} not found")

        # Apply updates
        for update in updates:
            # Validate clause exists
            try:
                clause = template.get_clause(update.identifier)
            except ClauseNotFoundError:
                raise ClauseNotFoundError(update.identifier)

            # Check if mandatory
            is_mandatory = template.is_mandatory_clause(update.identifier)

            # Apply override
            profile.set_override(
                identifier=update.identifier,
                is_mandatory=is_mandatory,
                is_active=update.is_active,
                custom_title=update.custom_title,
                custom_body=update.custom_body,
                custom_order=update.custom_order,
            )

        # Save profile
        saved_profile = self.profile_repository.save(profile)

        # Return DTO
        return LegalProfileDTO(
            id=saved_profile.id,
            account_id=saved_profile.account_id,
            template_id=saved_profile.template_id,
            template_version=saved_profile.template_version,
            clause_overrides=saved_profile.clause_overrides,
        )
