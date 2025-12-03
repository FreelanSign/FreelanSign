"""
Django implementation of LegalProfileRepository.
"""

import uuid

from apps.legal_terms.adapters.persistence.models import (
    LegalProfileModel,
    LegalTemplateModel,
)
from apps.legal_terms.domain.entities.legal_profile import LegalProfile


class DjangoLegalProfileRepository:
    """Django ORM implementation of LegalProfileRepository."""

    def get_by_account(self, account_id: str) -> LegalProfile | None:
        """Get legal profile by account ID."""
        try:
            model = LegalProfileModel.objects.select_related("template").get(account_id=account_id)
            return self._to_entity(model)
        except LegalProfileModel.DoesNotExist:
            return None

    def save(self, profile: LegalProfile) -> LegalProfile:
        """Save or update legal profile."""
        try:
            model = LegalProfileModel.objects.get(id=profile.id)
            # Update existing
            model.clause_overrides = profile.clause_overrides
            model.save()
        except LegalProfileModel.DoesNotExist:
            # Create new
            model = LegalProfileModel.objects.create(
                id=profile.id,
                account_id=profile.account_id,
                template_id=profile.template_id,
                clause_overrides=profile.clause_overrides,
            )

        return self._to_entity(model)

    def get_or_create_for_account(self, account_id: str, template_id: str, template_version: str) -> LegalProfile:
        """Get existing profile or create new one for account."""
        try:
            model = LegalProfileModel.objects.select_related("template").get(account_id=account_id)
        except LegalProfileModel.DoesNotExist:
            # Create new profile
            model = LegalProfileModel.objects.create(
                id=uuid.uuid4(),
                account_id=account_id,
                template_id=template_id,
                clause_overrides={},
            )

        return self._to_entity(model)

    def _to_entity(self, model: LegalProfileModel) -> LegalProfile:
        """Convert model to entity."""
        return LegalProfile(
            id=str(model.id),
            account_id=str(model.account_id),
            template_id=str(model.template_id),
            template_version=model.template.version,
            clause_overrides=model.clause_overrides,
        )
