"""
Django implementation of AttachedTermsRepository.
"""

from apps.legal_terms.adapters.persistence.models import AttachedTermsModel
from apps.legal_terms.domain.entities.attached_terms import AttachedTerms


class DjangoAttachedTermsRepository:
    """Django ORM implementation of AttachedTermsRepository."""

    def save(self, attached_terms: AttachedTerms) -> AttachedTerms:
        """Save attached terms."""
        model = AttachedTermsModel.objects.create(
            id=attached_terms.id,
            quote_id=attached_terms.quote_id,
            template_version=attached_terms.template_version,
            rendered_html=attached_terms.rendered_html,
            rendered_text=attached_terms.rendered_text,
            snapshot_data=attached_terms.snapshot_data,
        )

        return self._to_entity(model)

    def get_by_quote(self, quote_id: str) -> AttachedTerms | None:
        """Get attached terms by quote ID."""
        try:
            model = AttachedTermsModel.objects.get(quote_id=quote_id)
            return self._to_entity(model)
        except AttachedTermsModel.DoesNotExist:
            return None

    def _to_entity(self, model: AttachedTermsModel) -> AttachedTerms:
        """Convert model to entity."""
        return AttachedTerms(
            id=str(model.id),
            quote_id=str(model.quote_id),
            template_version=model.template_version,
            rendered_html=model.rendered_html,
            rendered_text=model.rendered_text,
            snapshot_data=model.snapshot_data,
        )
