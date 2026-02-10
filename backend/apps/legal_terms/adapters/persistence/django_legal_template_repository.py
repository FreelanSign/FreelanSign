"""
Django implementation of LegalTemplateRepository.
"""

from apps.legal_terms.adapters.persistence.models import LegalTemplateModel
from apps.legal_terms.domain.entities.legal_template import LegalTemplate


class DjangoLegalTemplateRepository:
    """Django ORM implementation of LegalTemplateRepository."""

    def get_active_for_jurisdiction(self, jurisdiction: str) -> LegalTemplate | None:
        """Get active template for jurisdiction."""
        try:
            model = LegalTemplateModel.objects.get(jurisdiction=jurisdiction, is_active=True)
            return self._to_entity(model)
        except LegalTemplateModel.DoesNotExist:
            return None

    def get_by_id(self, template_id: str) -> LegalTemplate | None:
        """Get template by ID."""
        try:
            model = LegalTemplateModel.objects.get(id=template_id)
            return self._to_entity(model)
        except LegalTemplateModel.DoesNotExist:
            return None

    def _to_entity(self, model: LegalTemplateModel) -> LegalTemplate:
        """Convert model to entity."""
        return LegalTemplate(
            id=str(model.id),
            name=model.name,
            jurisdiction=model.jurisdiction,
            version=model.version,
            clauses=model.clauses,
            is_active=model.is_active,
        )
